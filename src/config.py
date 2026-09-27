"""
Centralized Configuration Module for Factory Energy Intelligence Platform.
Contains unified, single-source-of-truth definitions for Industrial Time-of-Day (TOD)
Tariffs, Grid Carbon Emission Factors, and Factory Operating Constraints.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class TariffConfig:
    """
    Industrial Time-of-Day (TOD) Electricity Tariff Configuration.
    Default parameters reflect typical Indian State DISCOM HT-2 industrial tariffs.
    """
    state_or_discom: str = "Generic Indian HT-2 Industrial (e.g., MSEDCL / UGVCL / BESCOM)"
    off_peak_rate_inr: float = 5.20      # INR / kWh (Night incentive slot)
    normal_rate_inr: float = 7.80        # INR / kWh (Day normal slot)
    peak_rate_inr: float = 11.50         # INR / kWh (Evening peak surcharge slot)
    
    # Time-of-Day slot definitions (24-hour clock, start inclusive, end exclusive)
    off_peak_start: int = 22             # 22:00
    off_peak_end: int = 6                # 06:00 (crosses midnight)
    normal_start: int = 6                # 06:00
    normal_end: int = 18                 # 18:00
    peak_start: int = 18                 # 18:00
    peak_end: int = 22                   # 22:00
    
    # Demand charges & Power Factor rules
    demand_charge_per_kva_inr: float = 375.0  # Monthly kVA billing demand charge
    contract_demand_kva: float = 800.0        # Sanctioned demand limit
    pf_penalty_threshold: float = 0.90        # Threshold below which penalty applies
    pf_penalty_rate_pct: float = 1.5          # % surcharge per 0.01 drop below 0.90
    pf_rebate_threshold: float = 0.95         # Threshold above which incentive applies
    pf_rebate_rate_pct: float = 0.5           # % credit per 0.01 rise above 0.95

    def get_tariff_period(self, hour: int) -> str:
        """Determines TOD slot classification from clock hour (0 to 23)."""
        if self.peak_start <= hour < self.peak_end:
            return "PEAK"
        elif hour >= self.off_peak_start or hour < self.off_peak_end:
            return "OFF_PEAK"
        else:
            return "NORMAL"

    def get_rate_for_period(self, period: str) -> float:
        """Returns active rate in INR/kWh for the period label."""
        p = period.upper()
        if p == "PEAK":
            return self.peak_rate_inr
        elif p == "OFF_PEAK":
            return self.off_peak_rate_inr
        else:
            return self.normal_rate_inr

    @property
    def peak_to_offpeak_differential(self) -> float:
        """Price differential between peak and off-peak slots (incentive for load shifting)."""
        return self.peak_rate_inr - self.off_peak_rate_inr


@dataclass(frozen=True)
class EmissionConfig:
    """
    Scope 2 Greenhouse Gas Emission Configuration.
    Default factor: 0.716 kg CO2 / kWh.
    Authority: Central Electricity Authority (CEA), Ministry of Power,
               Government of India - CO2 Baseline Database for Indian Power Sector (Ver. 19.0).
    """
    grid_emission_factor_kg_per_kwh: float = 0.716
    source_authority: str = "CEA India CO2 Baseline Database Ver. 19.0"
