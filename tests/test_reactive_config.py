"""
Automated Verification Tests for Configurable Tariff & Emission Reactivity.
Implements the 6 mandatory challenge test cases from Section 8:
TEST 1: Baseline TOD configuration (5, 8, 12)
TEST 2: Flat tariff (8, 8, 8) - differential disappears, shift savings = 0
TEST 3: High peak tariff (5, 8, 20) - higher baseline cost, stronger shift incentive
TEST 4: CO2 factor shift (0.716 -> 0.500) - Energy, SEC, Cost invariant; CO2 decreases
TEST 5: Off-peak rate shift (5 -> 10) - Energy, SEC, CO2 invariant; Cost increases
TEST 6: Optimization schedule comparison under flat vs steep TOD tariff
"""

import pytest
import pandas as pd
import numpy as np

from src.config import TariffConfig, EmissionConfig
from src.energy.cost_model import ElectricityCostCalculator
from src.emissions.carbon import CarbonCalculator
from src.optimization.optimizer import FactoryOptimizer
from src.energy.analytics import EnergyAnalyticsEngine


@pytest.fixture
def sample_factory_data():
    """Generates a small representative factory DataFrame covering Off-Peak, Normal, and Peak hours."""
    # 24 hours of 1-hour samples (total 24 records)
    records = []
    for h in range(24):
        # Peak: 18 to 22 (4 hours)
        # Off-Peak: 22 to 6 (8 hours)
        # Normal: 6 to 18 (12 hours)
        if 18 <= h < 22:
            period = "PEAK"
            p_kw = 120.0
            prod = 40.0
            mid = "FURNACE_01"  # flexible load in peak
        elif h >= 22 or h < 6:
            period = "OFF_PEAK"
            p_kw = 40.0
            prod = 10.0
            mid = "COMP_01"
        else:
            period = "NORMAL"
            p_kw = 80.0
            prod = 30.0
            mid = "MOTOR_01"

        records.append({
            "timestamp": f"2026-03-01 {h:02d}:00:00",
            "machine_id": mid,
            "feeder_id": "FDR_01",
            "machine_status": "RUNNING",
            "active_power_kw": p_kw,
            "apparent_power_kva": p_kw / 0.88,
            "energy_kwh": p_kw * 1.0,  # 1 hour = 1.0 hr
            "production_units": prod,
            "idle_flag": 0,
            "power_factor": 0.88,
            "tariff_period": period
        })

    return pd.DataFrame(records)


def test_test1_baseline_tod_tariff_recording(sample_factory_data):
    """TEST 1: OffPeak=5, Normal=8, Peak=12. Record energy, cost, SEC, CO2."""
    t_cfg = TariffConfig(off_peak_rate_inr=5.0, normal_rate_inr=8.0, peak_rate_inr=12.0)
    e_cfg = EmissionConfig(grid_emission_factor_kg_per_kwh=0.716)

    cost_calc = ElectricityCostCalculator(config=t_cfg)
    carb_calc = CarbonCalculator(config=e_cfg)
    analytics = EnergyAnalyticsEngine(cost_calculator=cost_calc)

    energy = float(sample_factory_data["energy_kwh"].sum())
    prod = float(sample_factory_data["production_units"].sum())
    sec = analytics.calculate_sec(energy, prod)
    cost_res = cost_calc.calculate_energy_cost(sample_factory_data)
    carb_res = carb_calc.calculate_emissions(energy)

    # 8 hrs Off-Peak * 40 kWh * 5 = 1600
    # 12 hrs Normal * 80 kWh * 8 = 7680
    # 4 hrs Peak * 120 kWh * 12 = 5760
    # Base energy charges = 1600 + 7680 + 5760 = 15,040
    assert cost_res["energy_charge_inr"] == 15040.0
    assert energy == (8 * 40.0 + 12 * 80.0 + 4 * 120.0)  # 1760 kWh
    assert pytest.approx(sec, rel=1e-3) == (1760.0 / (8 * 10 + 12 * 30 + 4 * 40))
    assert carb_res["emissions_kg_co2"] == pytest.approx(1760.0 * 0.716)


def test_test2_flat_tariff_no_tod_differential(sample_factory_data):
    """TEST 2: OffPeak=8, Normal=8, Peak=8. TOD differential disappears; shift advantage = 0."""
    t_cfg_flat = TariffConfig(off_peak_rate_inr=8.0, normal_rate_inr=8.0, peak_rate_inr=8.0)
    optimizer = FactoryOptimizer(tariff_config=t_cfg_flat)

    assert t_cfg_flat.peak_to_offpeak_differential == 0.0

    df_opt, comp = optimizer.run_full_optimization(sample_factory_data)

    # Tariff shifting cost savings must be EXACTLY zero!
    assert comp["impact"]["tariff_shift_cost_saved_inr"] == 0.0
    assert comp["impact"]["peak_to_offpeak_differential_inr"] == 0.0


def test_test3_high_peak_tariff_stronger_shift_incentive(sample_factory_data):
    """TEST 3: OffPeak=5, Normal=8, Peak=20. Peak cost increases; higher shift cost incentive."""
    t_cfg_normal = TariffConfig(off_peak_rate_inr=5.0, normal_rate_inr=8.0, peak_rate_inr=12.0)
    t_cfg_high_peak = TariffConfig(off_peak_rate_inr=5.0, normal_rate_inr=8.0, peak_rate_inr=20.0)

    cost_normal = ElectricityCostCalculator(config=t_cfg_normal).calculate_energy_cost(sample_factory_data)
    cost_high_peak = ElectricityCostCalculator(config=t_cfg_high_peak).calculate_energy_cost(sample_factory_data)

    # Baseline peak consumption cost must be significantly higher under Peak=20 vs Peak=12
    assert cost_high_peak["peak_cost_inr"] > cost_normal["peak_cost_inr"]
    # Differential is 20 - 5 = 15 (vs 12 - 5 = 7)
    assert t_cfg_high_peak.peak_to_offpeak_differential > t_cfg_normal.peak_to_offpeak_differential

    opt_normal = FactoryOptimizer(tariff_config=t_cfg_normal)
    opt_high = FactoryOptimizer(tariff_config=t_cfg_high_peak)

    _, comp_normal = opt_normal.run_full_optimization(sample_factory_data)
    _, comp_high = opt_high.run_full_optimization(sample_factory_data)

    # Shifting savings must be higher with Peak=20
    assert comp_high["impact"]["tariff_shift_cost_saved_inr"] > comp_normal["impact"]["tariff_shift_cost_saved_inr"]


def test_test4_co2_factor_shift_invariance(sample_factory_data):
    """TEST 4: Change CO2 factor 0.716 -> 0.500. Energy, SEC, Cost UNCHANGED; CO2 decreased proportionally."""
    t_cfg = TariffConfig(off_peak_rate_inr=5.20, normal_rate_inr=7.80, peak_rate_inr=11.50)
    e_cfg_orig = EmissionConfig(grid_emission_factor_kg_per_kwh=0.716)
    e_cfg_new = EmissionConfig(grid_emission_factor_kg_per_kwh=0.500)

    opt_orig = FactoryOptimizer(tariff_config=t_cfg, emission_config=e_cfg_orig)
    opt_new = FactoryOptimizer(tariff_config=t_cfg, emission_config=e_cfg_new)

    _, comp_orig = opt_orig.run_full_optimization(sample_factory_data)
    _, comp_new = opt_new.run_full_optimization(sample_factory_data)

    # Energy, SEC, and Cost MUST BE STRICTLY IDENTICAL
    assert comp_orig["baseline"]["energy_kwh"] == comp_new["baseline"]["energy_kwh"]
    assert comp_orig["baseline"]["sec_kwh_per_unit"] == comp_new["baseline"]["sec_kwh_per_unit"]
    assert comp_orig["baseline"]["electricity_cost_inr"] == comp_new["baseline"]["electricity_cost_inr"]
    assert comp_orig["impact"]["cost_reduction_inr"] == comp_new["impact"]["cost_reduction_inr"]

    # CO2 must decrease strictly proportionally: 0.500 / 0.716
    ratio = comp_new["baseline"]["carbon_emissions_kg_co2"] / comp_orig["baseline"]["carbon_emissions_kg_co2"]
    assert pytest.approx(ratio, rel=1e-3) == (0.500 / 0.716)


def test_test5_tariff_rate_change_invariance(sample_factory_data):
    """TEST 5: Change tariff OffPeak 5 -> 10. Energy, SEC, CO2 UNCHANGED; Cost changed."""
    t_cfg_1 = TariffConfig(off_peak_rate_inr=5.0, normal_rate_inr=8.0, peak_rate_inr=12.0)
    t_cfg_2 = TariffConfig(off_peak_rate_inr=10.0, normal_rate_inr=8.0, peak_rate_inr=12.0)
    e_cfg = EmissionConfig(grid_emission_factor_kg_per_kwh=0.716)

    opt_1 = FactoryOptimizer(tariff_config=t_cfg_1, emission_config=e_cfg)
    opt_2 = FactoryOptimizer(tariff_config=t_cfg_2, emission_config=e_cfg)

    _, comp_1 = opt_1.run_full_optimization(sample_factory_data)
    _, comp_2 = opt_2.run_full_optimization(sample_factory_data)

    # Energy, Production, SEC, and CO2 MUST BE STRICTLY IDENTICAL
    assert comp_1["baseline"]["energy_kwh"] == comp_2["baseline"]["energy_kwh"]
    assert comp_1["baseline"]["production_units"] == comp_2["baseline"]["production_units"]
    assert comp_1["baseline"]["sec_kwh_per_unit"] == comp_2["baseline"]["sec_kwh_per_unit"]
    assert comp_1["baseline"]["carbon_emissions_kg_co2"] == comp_2["baseline"]["carbon_emissions_kg_co2"]

    # Cost MUST BE DIFFERENT (higher due to higher off-peak rate)
    assert comp_2["baseline"]["electricity_cost_inr"] > comp_1["baseline"]["electricity_cost_inr"]


def test_test6_optimizer_schedule_comparison_flat_vs_tod(sample_factory_data):
    """TEST 6: Compare optimizer schedule and dispatch under flat vs steep TOD tariff."""
    t_flat = TariffConfig(off_peak_rate_inr=8.0, normal_rate_inr=8.0, peak_rate_inr=8.0)
    t_steep = TariffConfig(off_peak_rate_inr=4.0, normal_rate_inr=8.0, peak_rate_inr=16.0)

    opt_flat = FactoryOptimizer(tariff_config=t_flat)
    opt_steep = FactoryOptimizer(tariff_config=t_steep)

    df_opt_flat, comp_flat = opt_flat.run_full_optimization(sample_factory_data)
    df_opt_steep, comp_steep = opt_steep.run_full_optimization(sample_factory_data)

    # In flat tariff, peak load should NOT be shifted to off-peak because there is 0 financial benefit
    furnace_slots_flat = df_opt_flat.loc[df_opt_flat["machine_id"] == "FURNACE_01", "tariff_period"].unique()
    assert "PEAK" in furnace_slots_flat  # Unshifted!

    # In steep TOD tariff, furnace peak load IS shifted to off-peak
    furnace_slots_steep = df_opt_steep.loc[df_opt_steep["machine_id"] == "FURNACE_01", "tariff_period"].unique()
    assert "PEAK" not in furnace_slots_steep  # Shifted to OFF_PEAK!
    assert "OFF_PEAK" in furnace_slots_steep

    # Shift cost savings in steep tariff must be strictly positive, while flat is 0
    assert comp_steep["impact"]["tariff_shift_cost_saved_inr"] > 0.0
    assert comp_flat["impact"]["tariff_shift_cost_saved_inr"] == 0.0
