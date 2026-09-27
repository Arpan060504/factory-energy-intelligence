"""
Industrial Energy Analytics and Specific Energy Consumption (SEC) Engine.
Computes feeder/machine disaggregation, daily/hourly profiles, timestamp-synchronized
substation load summation, peak demand, idle losses, and verified SEC metrics.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from .cost_model import ElectricityCostCalculator, TariffConfig


class EnergyAnalyticsEngine:
    def __init__(
        self,
        cost_calculator: Optional[ElectricityCostCalculator] = None,
        tariff_config: Optional[TariffConfig] = None
    ):
        if cost_calculator is not None:
            self.cost_calc = cost_calculator
        elif tariff_config is not None:
            self.cost_calc = ElectricityCostCalculator(config=tariff_config)
        else:
            self.cost_calc = ElectricityCostCalculator()

    @staticmethod
    def calculate_sec(energy_kwh: float, production_units: Optional[float]) -> Optional[float]:
        """
        Specific Energy Consumption (SEC) = Energy (kWh) / Good Production (Units)
        Returns kWh / unit. If production is zero or missing, returns None (mathematically undefined).
        """
        if production_units is None:
            return None
        try:
            val = float(production_units)
            if np.isnan(val) or val <= 0.001:
                return None
            return float(round(float(energy_kwh) / val, 4))
        except (ValueError, TypeError, ZeroDivisionError):
            return None

    @staticmethod
    def calculate_sec_improvement(baseline_sec: Optional[float], optimized_sec: Optional[float]) -> float:
        """
        SEC improvement (%) = ((SEC_baseline - SEC_optimized) / SEC_baseline) * 100
        """
        if baseline_sec is None or optimized_sec is None:
            return 0.0
        try:
            b = float(baseline_sec)
            o = float(optimized_sec)
            if np.isnan(b) or np.isnan(o) or b <= 0.0001:
                return 0.0
            return float(round(((b - o) / b) * 100.0, 2))
        except (ValueError, TypeError, ZeroDivisionError):
            return 0.0

    def aggregate_plant_timeseries(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregates individual machine records that share the EXACT SAME timestamp
        into a synchronized plant-level power, demand, and loss profile.
        """
        if df.empty:
            return pd.DataFrame()

        grouped = df.groupby("timestamp").agg(
            total_active_power_kw=("active_power_kw", "sum"),
            total_apparent_power_kva=("apparent_power_kva", "sum"),
            total_reactive_power_kvar=("reactive_power_kvar", "sum"),
            total_energy_kwh=("energy_kwh", "sum"),
            total_cable_loss_kw=("estimated_cable_loss_kw", "sum"),
            total_production_units=("production_units", "sum"),
            total_idle_energy_kwh=("energy_kwh", lambda x: x[df.loc[x.index, "idle_flag"] == 1].sum()),
            avg_voltage_v=("voltage", "mean"),
            avg_power_factor=("power_factor", "mean"),
            tariff_period=("tariff_period", "first"),
            substation_id=("substation_id", "first"),
            bus_id=("bus_id", "first")
        ).reset_index()

        # Plant-wide power factor = Total P / Total S
        grouped["plant_power_factor"] = np.round(
            grouped["total_active_power_kw"] / np.maximum(0.1, grouped["total_apparent_power_kva"]), 3
        )
        grouped["plant_power_factor"] = np.clip(grouped["plant_power_factor"], 0.1, 1.0)
        
        # Interval SEC
        grouped["interval_sec"] = np.where(
            grouped["total_production_units"] > 0,
            np.round(grouped["total_energy_kwh"] / grouped["total_production_units"], 4),
            0.0
        )

        return grouped

    def summarize_by_machine(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates comprehensive machine-level operational summary table.
        """
        summary_rows = []
        for mid, group in df.groupby("machine_id"):
            tot_energy = float(group["energy_kwh"].sum())
            tot_prod = float(group["production_units"].sum())
            sec = self.calculate_sec(tot_energy, tot_prod)
            
            idle_mask = (group["idle_flag"] == 1) | (group["machine_status"] == "IDLE")
            idle_kwh = float(group.loc[idle_mask, "energy_kwh"].sum())
            idle_pct = round((idle_kwh / tot_energy * 100.0) if tot_energy > 0 else 0.0, 1)
            
            cable_loss_kwh = float((group["estimated_cable_loss_kw"] * (5.0 / 60.0)).sum())
            cable_loss_pct = round((cable_loss_kwh / tot_energy * 100.0) if tot_energy > 0 else 0.0, 2)

            cost_res = self.cost_calc.calculate_energy_cost(group)

            summary_rows.append({
                "machine_id": mid,
                "machine_name": group["machine_name"].iloc[0] if "machine_name" in group else mid,
                "feeder_id": group["feeder_id"].iloc[0],
                "machine_type": group["machine_type"].iloc[0],
                "total_energy_kwh": round(tot_energy, 1),
                "total_production_units": round(tot_prod, 1),
                "sec_kwh_per_unit": sec,
                "total_cost_inr": cost_res["total_cost_inr"],
                "peak_power_kw": round(float(group["active_power_kw"].max()), 1),
                "max_demand_kva": round(float(group["apparent_power_kva"].max()), 1),
                "avg_power_factor": round(float(group["power_factor"].mean()), 3),
                "avg_imbalance_pct": round(float(group["current_imbalance_pct"].mean()), 2),
                "idle_energy_kwh": round(idle_kwh, 1),
                "idle_energy_pct": idle_pct,
                "estimated_cable_loss_kwh": round(cable_loss_kwh, 2),
                "estimated_cable_loss_pct": cable_loss_pct,
                "operating_hours": round(float((group["machine_status"] == "RUNNING").sum() * (5.0 / 60.0)), 1),
                "idle_hours": round(float(idle_mask.sum() * (5.0 / 60.0)), 1)
            })

        return pd.DataFrame(summary_rows).sort_values("total_energy_kwh", ascending=False).reset_index(drop=True)

    def calculate_plant_overview_kpis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Computes executive headline KPIs for the entire facility.
        """
        plant_ts = self.aggregate_plant_timeseries(df)
        
        total_energy = float(df["energy_kwh"].sum())
        total_prod = float(df["production_units"].sum())
        sec = self.calculate_sec(total_energy, total_prod)
        
        cost_res = self.cost_calc.calculate_energy_cost(df)
        
        idle_mask = (df["idle_flag"] == 1) | (df["machine_status"] == "IDLE")
        total_idle_kwh = float(df.loc[idle_mask, "energy_kwh"].sum())
        idle_pct = round((total_idle_kwh / total_energy * 100.0) if total_energy > 0 else 0.0, 1)

        total_cable_loss_kwh = float((df["estimated_cable_loss_kw"] * (5.0 / 60.0)).sum())

        peak_demand_kva = float(plant_ts["total_apparent_power_kva"].max()) if not plant_ts.empty else 0.0

        return {
            "total_energy_kwh": round(total_energy, 1),
            "total_production_units": round(total_prod, 1),
            "overall_sec_kwh_per_unit": sec,
            "total_electricity_cost_inr": cost_res["total_cost_inr"],
            "peak_demand_kva": round(peak_demand_kva, 1),
            "contract_demand_kva": self.cost_calc.config.contract_demand_kva,
            "avg_power_factor": round(float(df["power_factor"].mean()), 3),
            "total_idle_energy_kwh": round(total_idle_kwh, 1),
            "idle_energy_pct": idle_pct,
            "estimated_total_cable_loss_kwh": round(total_cable_loss_kwh, 1),
            "active_machine_count": int(df["machine_id"].nunique())
        }
