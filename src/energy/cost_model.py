"""
Industrial Electricity Tariff Model for Indian Manufacturing SMEs.
Supports Time-of-Day (TOD) active energy charges, contract demand charges,
power factor surcharges/rebates, and configurable state regulatory profiles.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from ..config import TariffConfig

__all__ = ["TariffConfig", "ElectricityCostCalculator"]


class ElectricityCostCalculator:
    def __init__(self, config: Optional[TariffConfig] = None):
        self.config = config or TariffConfig()

    def calculate_energy_cost(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Computes detailed industrial electricity bill breakdown from time-series DataFrame.
        Enforces:
            cost_t = energy_kwh_t * tariff_rate_t
            total_energy_cost = sum(cost_t)
        Requires columns: 'energy_kwh', and either 'tariff_period' or 'timestamp'.
        """
        if df.empty:
            return {
                "total_cost_inr": 0.0,
                "energy_charge_inr": 0.0,
                "demand_charge_inr": 0.0,
                "pf_penalty_inr": 0.0,
                "peak_cost_inr": 0.0,
                "normal_cost_inr": 0.0,
                "off_peak_cost_inr": 0.0,
                "off_peak_energy_kwh": 0.0,
                "normal_energy_kwh": 0.0,
                "peak_energy_kwh": 0.0,
                "max_demand_kva": 0.0,
                "billed_demand_kva": 0.0,
                "avg_power_factor": 1.0,
                "span_days": 30.0
            }

        # Resolve tariff period per row
        if "tariff_period" in df.columns:
            periods = df["tariff_period"].astype(str).str.upper()
        elif "timestamp" in df.columns:
            ts = pd.to_datetime(df["timestamp"])
            periods = ts.dt.hour.map(self.config.get_tariff_period)
        else:
            periods = pd.Series(["NORMAL"] * len(df), index=df.index)

        # Rate mapping from active TariffConfig
        cost_map = {
            "OFF_PEAK": float(self.config.off_peak_rate_inr),
            "NORMAL": float(self.config.normal_rate_inr),
            "PEAK": float(self.config.peak_rate_inr)
        }

        rates = periods.map(cost_map).fillna(float(self.config.normal_rate_inr)).values
        energy_kwh = df["energy_kwh"].values

        # Interval-by-interval active energy cost: cost_t = energy_kwh_t * rate_t
        cost_t = energy_kwh * rates
        base_energy_cost = float(np.sum(cost_t)) if len(cost_t) > 0 else 0.0

        # Subtotals by tariff slot
        off_peak_mask = (periods == "OFF_PEAK").values
        normal_mask = (periods == "NORMAL").values
        peak_mask = (periods == "PEAK").values

        off_peak_energy = float(np.sum(energy_kwh[off_peak_mask]))
        normal_energy = float(np.sum(energy_kwh[normal_mask]))
        peak_energy = float(np.sum(energy_kwh[peak_mask]))

        off_peak_cost = float(np.sum(cost_t[off_peak_mask]))
        normal_cost = float(np.sum(cost_t[normal_mask]))
        peak_cost = float(np.sum(cost_t[peak_mask]))

        # Maximum Demand (kVA) - simultaneous peak across factory or peak recorded
        max_demand_kva = float(df["apparent_power_kva"].max()) if "apparent_power_kva" in df.columns else 0.0
        
        # Billed demand is max of recorded peak or 85% of sanctioned contract demand
        billed_demand_kva = max(max_demand_kva, 0.85 * self.config.contract_demand_kva)
        
        # Determine duration in months
        if "timestamp" in df.columns:
            ts = pd.to_datetime(df["timestamp"])
            span_days = max(1.0, (ts.max() - ts.min()).total_seconds() / 86400.0)
            month_fraction = span_days / 30.0
        else:
            month_fraction = 1.0

        demand_charge = billed_demand_kva * self.config.demand_charge_per_kva_inr * month_fraction

        # Power Factor Penalty / Rebate Assessment
        avg_pf = float(df["power_factor"].mean()) if "power_factor" in df.columns else 0.88
        pf_adjustment = 0.0
        if avg_pf < self.config.pf_penalty_threshold:
            pf_deficit = (self.config.pf_penalty_threshold - avg_pf) / 0.01
            pf_adjustment = base_energy_cost * (pf_deficit * (self.config.pf_penalty_rate_pct / 100.0))
        elif avg_pf > self.config.pf_rebate_threshold:
            pf_surplus = (avg_pf - self.config.pf_rebate_threshold) / 0.01
            pf_adjustment = -base_energy_cost * (pf_surplus * (self.config.pf_rebate_rate_pct / 100.0))

        total_cost = base_energy_cost + demand_charge + pf_adjustment

        return {
            "total_cost_inr": round(total_cost, 2),
            "energy_charge_inr": round(base_energy_cost, 2),
            "demand_charge_inr": round(demand_charge, 2),
            "pf_penalty_inr": round(pf_adjustment, 2),
            "off_peak_energy_kwh": round(off_peak_energy, 2),
            "normal_energy_kwh": round(normal_energy, 2),
            "peak_energy_kwh": round(peak_energy, 2),
            "off_peak_cost_inr": round(off_peak_cost, 2),
            "normal_cost_inr": round(normal_cost, 2),
            "peak_cost_inr": round(peak_cost, 2),
            "max_demand_kva": round(max_demand_kva, 2),
            "billed_demand_kva": round(billed_demand_kva, 2),
            "avg_power_factor": round(avg_pf, 3),
            "span_days": round(month_fraction * 30.0, 1)
        }
