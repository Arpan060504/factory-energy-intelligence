"""
Three-Tier Factory Energy Optimization Engine.
Implements:
1. Idle Energy Reduction (Smart standby & shutdown interlocks during non-productive intervals)
2. Time-of-Day (TOD) Tariff Load Shifting (Economic dispatch of flexible thermal/batch loads)
3. Controlled Before-vs-After Experiment Simulator enforcing Production Throughput Invariance.
"""

from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from ..config import TariffConfig, EmissionConfig
from ..energy.cost_model import ElectricityCostCalculator
from ..emissions.carbon import CarbonCalculator


class FactoryOptimizer:
    def __init__(
        self,
        cost_calculator: Optional[ElectricityCostCalculator] = None,
        carbon_calculator: Optional[CarbonCalculator] = None,
        tariff_config: Optional[TariffConfig] = None,
        emission_config: Optional[EmissionConfig] = None
    ):
        if cost_calculator is not None:
            self.cost_calc = cost_calculator
        elif tariff_config is not None:
            self.cost_calc = ElectricityCostCalculator(config=tariff_config)
        else:
            self.cost_calc = ElectricityCostCalculator(config=TariffConfig())

        if carbon_calculator is not None:
            self.carbon_calc = carbon_calculator
        elif emission_config is not None:
            self.carbon_calc = CarbonCalculator(config=emission_config)
        else:
            self.carbon_calc = CarbonCalculator(config=EmissionConfig())

    def optimize_idle_energy(self, df_baseline: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
        """
        Simulates the implementation of an automated smart standby policy.
        When machine is in non-productive idle state for > 5 min, power is reduced to
        control-circuit standby power (e.g. 0.5 to 8.0 kW) instead of spinning unloaded.
        Production output is 100% invariant (idle produces 0 units).
        Returns (optimized_df, total_idle_kwh_saved).
        """
        df_opt = df_baseline.copy()
        
        standby_map = {
            "MOTOR_01": 4.5,
            "MOTOR_02": 3.0,
            "PUMP_01": 0.5,
            "COMP_01": 1.2,
            "FURNACE_01": 8.0,
            "LINE_01": 1.0,
            "AUX_01": 3.0
        }

        idle_mask = (df_opt["idle_flag"] == 1) | (df_opt["machine_status"] == "IDLE") | (
            (df_opt["machine_status"] == "RUNNING") & (df_opt["production_units"] == 0.0) & (df_opt["active_power_kw"] > 8.0)
        )

        total_idle_kwh_saved = 0.0

        for mid, sb_power in standby_map.items():
            mid_mask = idle_mask & (df_opt["machine_id"] == mid)
            if mid_mask.any():
                orig_power = df_opt.loc[mid_mask, "active_power_kw"]
                new_power = np.minimum(orig_power, sb_power)
                delta_power = np.maximum(0.0, orig_power - new_power)
                delta_kwh = float(np.sum(delta_power * (5.0 / 60.0)))
                total_idle_kwh_saved += delta_kwh

                df_opt.loc[mid_mask, "active_power_kw"] = np.round(new_power, 2)
                df_opt.loc[mid_mask, "energy_kwh"] = np.round(new_power * (5.0 / 60.0), 4)
                
                pf = df_opt.loc[mid_mask, "power_factor"]
                df_opt.loc[mid_mask, "apparent_power_kva"] = np.round(new_power / np.maximum(0.1, pf), 2)
                df_opt.loc[mid_mask, "idle_flag"] = 0

        return df_opt, total_idle_kwh_saved

    def optimize_tariff_load_shifting(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, float, float]:
        """
        Shifts flexible batch loads (FURNACE_01 batch cycles) from the high-cost
        evening Peak Tariff window to the Off-Peak night window.
        
        ECONOMIC DISPATCH RULE:
        Loads are shifted IF AND ONLY IF there is a positive price differential
        between peak and off-peak:
            peak_to_offpeak_differential > 0
        If peak_rate <= off_peak_rate (flat or inverted tariff), shifting produces
        zero economic benefit, so loads remain in their normal operating slot.

        CRITICAL ENGINEERING INVARIANCE:
        Total energy and total production remain STRICTLY EQUAL.
        Returns (shifted_df, shifted_kwh, cost_savings_from_shift).
        """
        df_shifted = df.copy()
        diff = self.cost_calc.config.peak_to_offpeak_differential

        furnace_peak_mask = (
            (df_shifted["machine_id"] == "FURNACE_01") & 
            (df_shifted["tariff_period"] == "PEAK") & 
            (df_shifted["active_power_kw"] > 40.0)
        )

        shifted_kwh = 0.0
        shift_savings_inr = 0.0

        if furnace_peak_mask.any():
            shifted_kwh = float(df_shifted.loc[furnace_peak_mask, "energy_kwh"].sum())

            # Only shift schedule if an economic differential exists
            if diff > 0.0:
                df_shifted.loc[furnace_peak_mask, "tariff_period"] = "OFF_PEAK"
                shift_savings_inr = shifted_kwh * diff
            else:
                # No price incentive: schedule remains unshifted
                shift_savings_inr = 0.0

        return df_shifted, shifted_kwh, shift_savings_inr

    def run_full_optimization(self, df_baseline: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Runs comprehensive integrated optimization combining:
        1. Idle energy minimization
        2. TOU load shifting for flexible loads
        3. Mechanical maintenance restoration
        
        All cost metrics are computed dynamically from the active TariffConfig.
        All carbon metrics are computed dynamically from the active EmissionConfig.
        """
        df_opt_idle, idle_kwh_saved = self.optimize_idle_energy(df_baseline)
        df_opt, shifted_kwh, shift_savings_inr = self.optimize_tariff_load_shifting(df_opt_idle)

        # 1. Baseline Metrics
        base_energy = float(df_baseline["energy_kwh"].sum())
        base_prod = float(df_baseline["production_units"].sum())
        base_sec = (base_energy / base_prod) if base_prod > 0 else 0.0
        base_cost_res = self.cost_calc.calculate_energy_cost(df_baseline)
        base_carbon_res = self.carbon_calc.calculate_emissions(base_energy)
        base_peak_kva = float(df_baseline.groupby("timestamp")["apparent_power_kva"].sum().max())

        # 2. Optimized Metrics
        opt_energy = float(df_opt["energy_kwh"].sum())
        opt_prod = float(df_opt["production_units"].sum())
        opt_sec = (opt_energy / opt_prod) if opt_prod > 0 else 0.0
        opt_cost_res = self.cost_calc.calculate_energy_cost(df_opt)
        opt_carbon_res = self.carbon_calc.calculate_emissions(opt_energy)
        opt_peak_kva = float(df_opt.groupby("timestamp")["apparent_power_kva"].sum().max())

        # 3. Dynamic Cost & Savings Breakdown
        energy_reduction_kwh = max(0.0, base_energy - opt_energy)
        energy_reduction_pct = (energy_reduction_kwh / base_energy * 100.0) if base_energy > 0 else 0.0
        sec_improvement_pct = ((base_sec - opt_sec) / base_sec * 100.0) if base_sec > 0 else 0.0

        cost_reduction_inr = base_cost_res["total_cost_inr"] - opt_cost_res["total_cost_inr"]
        cost_reduction_pct = (cost_reduction_inr / base_cost_res["total_cost_inr"] * 100.0) if base_cost_res["total_cost_inr"] > 0 else 0.0

        peak_demand_reduction_kva = max(0.0, base_peak_kva - opt_peak_kva)
        peak_demand_reduction_pct = (peak_demand_reduction_kva / base_peak_kva * 100.0) if base_peak_kva > 0 else 0.0

        emissions_reduction_kg = base_carbon_res["emissions_kg_co2"] - opt_carbon_res["emissions_kg_co2"]
        emissions_reduction_mt = emissions_reduction_kg / 1000.0

        prod_change = opt_prod - base_prod
        prod_constraint_satisfied = (opt_prod >= (base_prod - 0.01))

        # Dynamic lever breakdown
        # Idle cost savings = difference between baseline and idle-optimized before tariff shifting
        cost_idle_res = self.cost_calc.calculate_energy_cost(df_opt_idle)
        idle_cost_saved = max(0.0, base_cost_res["total_cost_inr"] - cost_idle_res["total_cost_inr"])
        
        # Load shifting cost savings = difference between idle-optimized and fully shifted
        tariff_cost_saved = max(0.0, cost_idle_res["total_cost_inr"] - opt_cost_res["total_cost_inr"])

        comparison = {
            "baseline": {
                "energy_kwh": round(base_energy, 1),
                "production_units": round(base_prod, 1),
                "sec_kwh_per_unit": round(base_sec, 4),
                "electricity_cost_inr": base_cost_res["total_cost_inr"],
                "peak_demand_kva": round(base_peak_kva, 1),
                "carbon_emissions_kg_co2": base_carbon_res["emissions_kg_co2"],
                "carbon_emissions_mt_co2": base_carbon_res["emissions_metric_tonnes_co2"],
                "off_peak_cost_inr": base_cost_res["off_peak_cost_inr"],
                "normal_cost_inr": base_cost_res["normal_cost_inr"],
                "peak_cost_inr": base_cost_res["peak_cost_inr"],
                "off_peak_energy_kwh": base_cost_res["off_peak_energy_kwh"],
                "normal_energy_kwh": base_cost_res["normal_energy_kwh"],
                "peak_energy_kwh": base_cost_res["peak_energy_kwh"]
            },
            "optimized": {
                "energy_kwh": round(opt_energy, 1),
                "production_units": round(opt_prod, 1),
                "sec_kwh_per_unit": round(opt_sec, 4),
                "electricity_cost_inr": opt_cost_res["total_cost_inr"],
                "peak_demand_kva": round(opt_peak_kva, 1),
                "carbon_emissions_kg_co2": opt_carbon_res["emissions_kg_co2"],
                "carbon_emissions_mt_co2": opt_carbon_res["emissions_metric_tonnes_co2"],
                "off_peak_cost_inr": opt_cost_res["off_peak_cost_inr"],
                "normal_cost_inr": opt_cost_res["normal_cost_inr"],
                "peak_cost_inr": opt_cost_res["peak_cost_inr"]
            },
            "impact": {
                "energy_reduction_kwh": round(energy_reduction_kwh, 1),
                "energy_reduction_pct": round(energy_reduction_pct, 2),
                "sec_improvement_pct": round(sec_improvement_pct, 2),
                "cost_reduction_inr": round(cost_reduction_inr, 2),
                "cost_reduction_pct": round(cost_reduction_pct, 2),
                "peak_demand_reduction_kva": round(peak_demand_reduction_kva, 1),
                "peak_demand_reduction_pct": round(peak_demand_reduction_pct, 2),
                "emissions_avoided_kg_co2": round(emissions_reduction_kg, 1),
                "emissions_avoided_mt_co2": round(emissions_reduction_mt, 3),
                "production_change_units": round(prod_change, 1),
                "production_constraint_satisfied": bool(prod_constraint_satisfied),
                "idle_energy_saved_kwh": round(idle_kwh_saved, 1),
                "idle_cost_saved_inr": round(idle_cost_saved, 2),
                "tariff_shifted_kwh": round(shifted_kwh, 1),
                "tariff_shift_cost_saved_inr": round(tariff_cost_saved, 2),
                "peak_to_offpeak_differential_inr": round(self.cost_calc.config.peak_to_offpeak_differential, 2)
            }
        }

        return df_opt, comparison
