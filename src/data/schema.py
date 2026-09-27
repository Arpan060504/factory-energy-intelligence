"""
Data schema definitions and validation models for the Factory Energy Intelligence Platform.
Enforces strict physical constraints and units across all ingestion and processing pipelines.
"""

from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class MachineMetadata(BaseModel):
    machine_id: str
    machine_name: str
    machine_type: Literal[
        "CNC_MACHINING",
        "HYDRAULIC_PRESS",
        "COOLING_PUMP",
        "AIR_COMPRESSOR",
        "INDUCTION_FURNACE",
        "CONVEYOR_LINE",
        "UTILITY_AUX",
    ]
    feeder_id: str
    substation_id: str
    bus_id: str
    rated_power_kw: float = Field(gt=0, description="Nameplate active power in kW")
    rated_voltage_v: float = Field(default=415.0, gt=0, description="Nominal line-to-line voltage in V")
    rated_current_a: float = Field(gt=0, description="Nominal line current in Amperes")
    base_power_factor: float = Field(default=0.88, ge=0.5, le=1.0)
    cable_length_m: float = Field(gt=0, description="Feeder cable distance in meters")
    cable_cross_section_mm2: float = Field(gt=0, description="Cross sectional area in mm2")
    cable_conductor: Literal["ALUMINIUM", "COPPER"] = "ALUMINIUM"
    is_critical_process: bool = False
    is_flexible_load: bool = False


class ElectricalTelemetry(BaseModel):
    timestamp: datetime
    machine_id: str
    feeder_id: str
    substation_id: str = "SUB_01"
    bus_id: str = "BUS_A"
    
    # 3-Phase Voltages (Line-to-Line)
    voltage_avg: float = Field(..., ge=300.0, le=500.0, description="Average Line Voltage in V")
    voltage_r: Optional[float] = Field(None, ge=300.0, le=500.0)
    voltage_y: Optional[float] = Field(None, ge=300.0, le=500.0)
    voltage_b: Optional[float] = Field(None, ge=300.0, le=500.0)
    
    # Phase Currents
    current_r: float = Field(..., ge=0.0, description="Phase R current in Amperes")
    current_y: float = Field(..., ge=0.0, description="Phase Y current in Amperes")
    current_b: float = Field(..., ge=0.0, description="Phase B current in Amperes")
    average_current: float = Field(..., ge=0.0, description="Average 3-phase current in Amperes")
    current_imbalance_pct: float = Field(..., ge=0.0, le=100.0, description="NEMA phase imbalance %")
    
    # Power and Energy
    power_factor: float = Field(..., ge=0.1, le=1.0, description="Operating power factor")
    active_power_kw: float = Field(..., ge=0.0, description="Active power in kW")
    apparent_power_kva: float = Field(..., ge=0.0, description="Apparent power in kVA")
    reactive_power_kvar: float = Field(..., ge=0.0, description="Reactive power in kVAR")
    energy_kwh: float = Field(..., ge=0.0, description="Active energy in kWh for sample interval")
    estimated_cable_loss_kw: float = Field(default=0.0, ge=0.0, description="Calculated I2R cable dissipation in kW")
    
    # Operating & Condition Telemetry
    frequency_hz: float = Field(default=50.0, ge=45.0, le=55.0)
    temperature_c: float = Field(..., ge=-10.0, le=120.0, description="Surface temperature in deg C")
    vibration_mms: float = Field(..., ge=0.0, le=50.0, description="Vibration velocity RMS in mm/s")
    machine_status: Literal["RUNNING", "IDLE", "OFF", "MAINTENANCE"]
    idle_flag: int = Field(default=0, ge=0, le=1)
    production_units: float = Field(default=0.0, ge=0.0, description="Good parts produced in interval")
    production_rate_uph: float = Field(default=0.0, ge=0.0, description="Instantaneous units per hour rate")
    tariff_period: Literal["OFF_PEAK", "NORMAL", "PEAK"]
    maintenance_state: Literal["NORMAL", "SCHEDULED", "OVERDUE"] = "NORMAL"

    @field_validator("apparent_power_kva")
    @classmethod
    def validate_power_triangle(cls, v, info):
        # Physical consistency check: S >= P
        p = info.data.get("active_power_kw")
        if p is not None and v < (p - 0.5):
            raise ValueError(f"Apparent power kVA ({v}) cannot be less than active power kW ({p})")
        return v


class AnomalyAlert(BaseModel):
    alert_id: str
    timestamp: datetime
    machine_id: str
    feeder_id: str
    anomaly_type: Literal[
        "ENERGY_ANOMALY",
        "PHASE_IMBALANCE",
        "LOW_POWER_FACTOR",
        "EXCESSIVE_IDLE_CONSUMPTION",
        "MACHINE_EFFICIENCY_DEGRADATION",
        "HIGH_TEMPERATURE",
        "HIGH_VIBRATION",
        "ABNORMAL_SEC",
    ]
    severity: Literal["NORMAL", "WARNING", "CRITICAL"]
    metric_name: str
    observed_value: float
    threshold_value: float
    deviation_pct: float
    root_cause_diagnosis: str
    recommended_action: str
    estimated_hourly_cost_impact_inr: float
    estimated_monthly_saving_inr: float
    is_active: bool = True


class OptimizationResult(BaseModel):
    optimization_type: Literal["IDLE_ELIMINATION", "TOD_LOAD_SHIFTING", "INTEGRATED_SCHEDULE"]
    period_start: datetime
    period_end: datetime
    
    # Baseline
    baseline_energy_kwh: float
    baseline_production_units: float
    baseline_sec_kwh_per_unit: float
    baseline_cost_inr: float
    baseline_peak_demand_kva: float
    baseline_emissions_kgco2: float
    
    # Optimized
    optimized_energy_kwh: float
    optimized_production_units: float
    optimized_sec_kwh_per_unit: float
    optimized_cost_inr: float
    optimized_peak_demand_kva: float
    optimized_emissions_kgco2: float
    
    # Differences
    energy_reduction_kwh: float
    energy_reduction_pct: float
    sec_improvement_pct: float
    cost_reduction_inr: float
    cost_reduction_pct: float
    peak_demand_reduction_kva: float
    emissions_reduction_kgco2: float
    production_change_units: float
    production_constraint_satisfied: bool
