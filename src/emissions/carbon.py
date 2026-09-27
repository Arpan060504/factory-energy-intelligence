"""
Carbon Emissions Calculation Module for Industrial Manufacturing.
Calculates Scope 2 GHG emissions using configurable grid emission factors,
citing the Central Electricity Authority (CEA), Government of India CO2 Database.
"""

from typing import Dict, Any, Optional, Union
from ..config import EmissionConfig

__all__ = ["EmissionConfig", "CarbonCalculator"]


class CarbonCalculator:
    """
    Scope 2 Carbon Dioxide Equivalent (CO2e) emissions calculator.
    
    Default Emission Factor:
        0.716 kg CO2 / kWh
        Source: Central Electricity Authority (CEA), Ministry of Power,
                Government of India - CO2 Baseline Database for Indian Power Sector (Ver. 19.0).
    """
    def __init__(
        self,
        emission_factor_kg_per_kwh: Optional[float] = None,
        source_label: Optional[str] = None,
        config: Optional[EmissionConfig] = None
    ):
        if config is not None:
            self.emission_factor = config.grid_emission_factor_kg_per_kwh
            self.source_label = config.source_authority
        else:
            self.emission_factor = 0.716 if emission_factor_kg_per_kwh is None else float(emission_factor_kg_per_kwh)
            self.source_label = source_label or "CEA India Grid Baseline v19.0"

    def calculate_emissions(self, energy_kwh: float) -> Dict[str, Any]:
        """Calculates total kg CO2 and metric tonnes CO2."""
        co2_kg = energy_kwh * self.emission_factor
        co2_mt = co2_kg / 1000.0
        return {
            "energy_kwh": round(energy_kwh, 2),
            "emission_factor_kg_per_kwh": self.emission_factor,
            "source_authority": self.source_label,
            "emissions_kg_co2": round(co2_kg, 2),
            "emissions_metric_tonnes_co2": round(co2_mt, 3)
        }

    def compare_emissions(self, baseline_kwh: float, optimized_kwh: float) -> Dict[str, Any]:
        """Compares baseline vs optimized emissions with percentage and absolute reductions."""
        base = self.calculate_emissions(baseline_kwh)
        opt = self.calculate_emissions(optimized_kwh)
        diff_kg = base["emissions_kg_co2"] - opt["emissions_kg_co2"]
        diff_mt = base["emissions_metric_tonnes_co2"] - opt["emissions_metric_tonnes_co2"]
        reduction_pct = (diff_kg / base["emissions_kg_co2"] * 100.0) if base["emissions_kg_co2"] > 0 else 0.0

        return {
            "baseline_kg_co2": base["emissions_kg_co2"],
            "baseline_mt_co2": base["emissions_metric_tonnes_co2"],
            "optimized_kg_co2": opt["emissions_kg_co2"],
            "optimized_mt_co2": opt["emissions_metric_tonnes_co2"],
            "avoided_kg_co2": round(diff_kg, 2),
            "avoided_mt_co2": round(diff_mt, 3),
            "reduction_pct": round(reduction_pct, 2),
            "emission_factor_used": self.emission_factor
        }
