"""
Automated Unit Tests for Industrial Electrical & Energy Calculations.
Verifies three-phase power equations, power factor, NEMA current imbalance,
discrete energy integrals, estimated cable losses, and SEC formulas.
"""

import math
import pytest
import pandas as pd
import numpy as np

from src.energy.calculations import (
    calculate_three_phase_power,
    calculate_phase_imbalance,
    estimate_feeder_cable_loss,
    calculate_conductor_resistance,
    calculate_discrete_energy,
)
from src.energy.analytics import EnergyAnalyticsEngine
from src.energy.cost_model import TariffConfig, ElectricityCostCalculator
from src.emissions.carbon import CarbonCalculator


def test_three_phase_power_balanced():
    """Verify standard formula: S = sqrt(3)*V*I/1000, P = S*PF, Q = sqrt(S^2 - P^2)."""
    v_l = 415.0  # Volts
    i_l = 100.0  # Amperes
    pf = 0.85
    
    result = calculate_three_phase_power(v_l, i_l, pf)
    
    expected_s = (math.sqrt(3) * 415.0 * 100.0) / 1000.0  # 71.880 kVA
    expected_p = expected_s * pf                          # 61.098 kW
    expected_q = math.sqrt(expected_s**2 - expected_p**2) # 37.865 kVAR
    
    assert pytest.approx(result["apparent_power_kva"], rel=1e-3) == round(expected_s, 3)
    assert pytest.approx(result["active_power_kw"], rel=1e-3) == round(expected_p, 3)
    assert pytest.approx(result["reactive_power_kvar"], rel=1e-3) == round(expected_q, 3)
    assert result["power_factor"] == 0.85


def test_power_factor_clamping():
    """Verify PF is clamped within realistic bounds [0.01, 1.0]."""
    res1 = calculate_three_phase_power(415.0, 50.0, 1.2)
    assert res1["power_factor"] == 1.0
    
    res2 = calculate_three_phase_power(415.0, 50.0, -0.5)
    assert res2["power_factor"] == 0.01


def test_nema_phase_imbalance_normal():
    """Verify balanced currents produce ~0% imbalance and NORMAL severity."""
    imb = calculate_phase_imbalance(100.0, 101.0, 99.0)
    assert imb["average_current"] == 100.0
    assert imb["imbalance_pct"] == 1.0
    assert imb["severity"] == "NORMAL"


def test_nema_phase_imbalance_critical():
    """Verify high deviation produces CRITICAL severity (> 10%)."""
    # I_avg = (120 + 90 + 90) / 3 = 100 A. Max dev = |120 - 100| = 20 A. Imbalance = 20%
    imb = calculate_phase_imbalance(120.0, 90.0, 90.0)
    assert imb["average_current"] == 100.0
    assert imb["imbalance_pct"] == 20.0
    assert imb["severity"] == "CRITICAL"


def test_feeder_cable_loss_and_resistivity():
    """Verify single-conductor resistance and 3*I^2*R Joule dissipation."""
    # Aluminium cable: 50m, 50 mm2.
    # rho_20 = 0.0282. At 50C: rho_50 = 0.0282 * (1 + 0.00403*30) = 0.03161
    # R = 0.03161 * (50 / 50) = 0.03161 Ohm
    r = calculate_conductor_resistance(length_m=50.0, cross_section_mm2=50.0, material="ALUMINIUM", operating_temp_c=50.0)
    assert 0.030 < r < 0.033
    
    # Current = 80 A. P_loss = 3 * 80^2 * r / 1000 = 3 * 6400 * 0.03161 / 1000 = 0.606 kW
    loss_kw = estimate_feeder_cable_loss(current_avg_a=80.0, resistance_ohm=r)
    assert 0.58 < loss_kw < 0.63


def test_discrete_energy_integral():
    """Verify E = sum(P_i * dt). For 12 samples of 60 kW at 5 min (1 hour total), E = 60 kWh."""
    power_series = pd.Series([60.0] * 12)
    dt_hours = 5.0 / 60.0
    total_energy = calculate_discrete_energy(power_series, dt_hours)
    assert pytest.approx(total_energy, rel=1e-3) == 60.0


def test_sec_calculation_and_improvement():
    """Verify SEC = Energy / Production and improvement percentage."""
    analytics = EnergyAnalyticsEngine()
    
    # Baseline: 1000 kWh, 2000 units -> SEC = 0.50 kWh/unit
    sec_base = analytics.calculate_sec(1000.0, 2000.0)
    assert sec_base == 0.50
    
    # Optimized: 850 kWh, 2000 units -> SEC = 0.425 kWh/unit
    sec_opt = analytics.calculate_sec(850.0, 2000.0)
    assert sec_opt == 0.425
    
    improvement = analytics.calculate_sec_improvement(sec_base, sec_opt)
    # ((0.50 - 0.425) / 0.50) * 100 = 15.0%
    assert improvement == 15.0

    # Utility asset or zero-production case: SEC is mathematically undefined (None)
    assert analytics.calculate_sec(500.0, 0.0) is None
    assert analytics.calculate_sec(500.0, -10.0) is None
    assert analytics.calculate_sec_improvement(None, 0.425) == 0.0
    assert analytics.calculate_sec_improvement(sec_base, None) == 0.0


def test_carbon_emissions_cea_factor():
    """Verify Scope 2 GHG emissions with CEA factor 0.716 kg/kWh."""
    calc = CarbonCalculator(emission_factor_kg_per_kwh=0.716)
    res = calc.calculate_emissions(10000.0)
    assert res["emissions_kg_co2"] == 7160.0
    assert res["emissions_metric_tonnes_co2"] == 7.16


def test_cost_model_tariff_slots():
    """Verify TOU energy charge pricing across Off-Peak, Normal, and Peak periods."""
    config = TariffConfig(off_peak_rate_inr=5.0, normal_rate_inr=8.0, peak_rate_inr=12.0)
    calc = ElectricityCostCalculator(config)
    
    sample_df = pd.DataFrame([
        {"energy_kwh": 100.0, "tariff_period": "OFF_PEAK", "apparent_power_kva": 50.0, "power_factor": 0.92},
        {"energy_kwh": 200.0, "tariff_period": "NORMAL", "apparent_power_kva": 60.0, "power_factor": 0.92},
        {"energy_kwh": 100.0, "tariff_period": "PEAK", "apparent_power_kva": 70.0, "power_factor": 0.92}
    ])
    
    cost_res = calc.calculate_energy_cost(sample_df)
    # Energy: 100*5 + 200*8 + 100*12 = 500 + 1600 + 1200 = 3300 INR
    assert cost_res["energy_charge_inr"] == 3300.0
