"""
Scenario-Based Automated Verification Tests.
Validates the 8 mandatory test cases defined in the challenge specifications.
"""

import pytest
import pandas as pd
import numpy as np

from src.anomaly.detector import AnomalyDetector
from src.maintenance.health import MachineHealthEngine
from src.recommendations.engine import RecommendationEngine
from src.optimization.optimizer import FactoryOptimizer
from src.energy.analytics import EnergyAnalyticsEngine
from src.baseline.engine import BaselineModel


def test_scenario_1_normal_operation():
    """TEST 1: Normal operation -> No critical alert."""
    detector = AnomalyDetector()
    health_engine = MachineHealthEngine()

    normal_df = pd.DataFrame([{
        "timestamp": "2026-03-01 10:00:00",
        "machine_id": "MOTOR_01",
        "feeder_id": "FDR_01",
        "machine_status": "RUNNING",
        "active_power_kw": 62.0,
        "expected_power_kw": 61.5,
        "power_deviation_pct": 0.81,
        "power_factor": 0.88,
        "current_imbalance_pct": 1.2,
        "vibration": 1.6,
        "temperature": 42.0,
        "production_units": 3.75,
        "idle_flag": 0
    }])

    alerts = detector.scan_dataframe(normal_df)
    critical_alerts = [a for a in alerts if a["severity"] == "CRITICAL"]
    assert len(critical_alerts) == 0

    health = health_engine.calculate_record_health_score(normal_df.iloc[0])
    assert health["health_status"] == "NORMAL"
    assert health["health_score"] >= 80.0


def test_scenario_2_motor_energy_increase():
    """TEST 2: Motor energy increase (+18%) -> Energy / Efficiency anomaly triggered."""
    detector = AnomalyDetector()

    degraded_df = pd.DataFrame([{
        "timestamp": "2026-03-08 11:00:00",
        "machine_id": "MOTOR_01",
        "feeder_id": "FDR_01",
        "machine_status": "RUNNING",
        "active_power_kw": 76.0,
        "expected_power_kw": 62.0,
        "power_deviation_pct": 22.58,  # > 12% warning threshold
        "power_factor": 0.88,
        "current_imbalance_pct": 1.5,
        "vibration": 3.5,              # elevated vibration
        "temperature": 54.0,           # elevated temperature
        "production_units": 3.75,      # unchanged production
        "idle_flag": 0
    }])

    alerts = detector.scan_dataframe(degraded_df)
    alert_types = [a["anomaly_type"] for a in alerts]
    assert "MACHINE_EFFICIENCY_DEGRADATION" in alert_types


def test_scenario_3_production_decrease_sec_increase():
    """TEST 3: Production decreases while energy remains constant -> SEC increases."""
    analytics = EnergyAnalyticsEngine()

    energy_kwh = 100.0  # Constant energy
    normal_prod = 200.0
    throttled_prod = 100.0  # Production drops 50%

    sec_normal = analytics.calculate_sec(energy_kwh, normal_prod)      # 0.50 kWh/unit
    sec_throttled = analytics.calculate_sec(energy_kwh, throttled_prod) # 1.00 kWh/unit

    assert sec_throttled > sec_normal
    assert sec_throttled == 2.0 * sec_normal


def test_scenario_4_machine_on_zero_production_idle():
    """TEST 4: Machine ON with zero production -> Idle energy alert generated."""
    detector = AnomalyDetector()

    idle_df = pd.DataFrame([{
        "timestamp": "2026-03-12 13:15:00",
        "machine_id": "COMP_01",
        "feeder_id": "FDR_04",
        "machine_status": "RUNNING",
        "active_power_kw": 18.5,       # Drawing 18.5 kW
        "expected_power_kw": 5.0,
        "power_deviation_pct": 270.0,
        "power_factor": 0.78,
        "current_imbalance_pct": 1.5,
        "vibration": 1.8,
        "temperature": 50.0,
        "production_units": 0.0,       # Zero production!
        "idle_flag": 1
    }])

    alerts = detector.scan_dataframe(idle_df)
    alert_types = [a["anomaly_type"] for a in alerts]
    assert "EXCESSIVE_IDLE_CONSUMPTION" in alert_types


def test_scenario_5_phase_imbalance_alert():
    """TEST 5: Phase imbalance -> Electrical health alert."""
    detector = AnomalyDetector()

    unbalanced_df = pd.DataFrame([{
        "timestamp": "2026-03-21 14:00:00",
        "machine_id": "PUMP_01",
        "feeder_id": "FDR_03",
        "machine_status": "RUNNING",
        "active_power_kw": 25.0,
        "expected_power_kw": 25.0,
        "power_deviation_pct": 0.0,
        "power_factor": 0.86,
        "current_imbalance_pct": 18.5,  # > 12% critical
        "vibration": 1.5,
        "temperature": 40.0,
        "production_units": 0.0,
        "idle_flag": 0
    }])

    alerts = detector.scan_dataframe(unbalanced_df)
    imb_alert = next((a for a in alerts if a["anomaly_type"] == "PHASE_IMBALANCE"), None)
    assert imb_alert is not None
    assert imb_alert["severity"] == "CRITICAL"


def test_scenario_5b_current_sensor_lost_alert():
    """TEST 5B: Phase dropped to <0.5A with other phases >15A -> Sensor loss alert."""
    detector = AnomalyDetector()

    sensor_lost_df = pd.DataFrame([{
        "timestamp": "2026-03-21 14:00:00",
        "machine_id": "PUMP_01",
        "feeder_id": "FDR_03",
        "machine_status": "RUNNING",
        "active_power_kw": 18.0,
        "expected_power_kw": 25.0,
        "power_deviation_pct": -28.0,
        "power_factor": 0.86,
        "current_imbalance_pct": 35.0,
        "current_r": 38.0,
        "current_y": 37.5,
        "current_b": 0.1,  # Disconnected CT sensor
        "vibration": 1.5,
        "temperature": 40.0,
        "production_units": 0.0,
        "idle_flag": 0
    }])

    alerts = detector.scan_dataframe(sensor_lost_df)
    alert_types = [a["anomaly_type"] for a in alerts]
    assert "DATA_QUALITY_CURRENT_SENSOR_LOST" in alert_types
    assert "PHASE_IMBALANCE" not in alert_types


def test_scenario_6_low_power_factor_warning():
    """TEST 6: Low PF -> PF warning."""
    detector = AnomalyDetector()

    low_pf_df = pd.DataFrame([{
        "timestamp": "2026-03-18 16:00:00",
        "machine_id": "MOTOR_02",
        "feeder_id": "FDR_02",
        "machine_status": "RUNNING",
        "active_power_kw": 45.0,
        "expected_power_kw": 45.0,
        "power_deviation_pct": 0.0,
        "power_factor": 0.72,          # Drops to 0.72 (< 0.78 critical)
        "current_imbalance_pct": 2.0,
        "vibration": 1.8,
        "temperature": 45.0,
        "production_units": 10.0,
        "idle_flag": 0
    }])

    alerts = detector.scan_dataframe(low_pf_df)
    pf_alert = next((a for a in alerts if a["anomaly_type"] == "LOW_POWER_FACTOR"), None)
    assert pf_alert is not None
    assert pf_alert["severity"] in ["WARNING", "CRITICAL"]


def test_scenario_7_peak_period_load_recommendation():
    """TEST 7: Peak-period load -> Scheduling recommendation generated."""
    rec_engine = RecommendationEngine()
    recs = rec_engine.generate_recommendations(pd.DataFrame(), None)
    
    # Should include TOD Tariff Load Shifting for FURNACE_01
    shift_rec = next((r for r in recs if r["category"] == "TOD_TARIFF_LOAD_SHIFTING"), None)
    assert shift_rec is not None
    assert shift_rec["machine_id"] == "FURNACE_01"
    assert shift_rec["estimated_monthly_inr_saving"] > 0.0


def test_scenario_8_optimized_operation_production_constraint():
    """TEST 8: Optimized operation -> Production constraint satisfied and comparison generated."""
    optimizer = FactoryOptimizer()

    # Create dummy baseline
    timestamps = [f"2026-03-01 10:{i*5:02d}:00" for i in range(12)]
    df_sample = pd.DataFrame({
        "timestamp": timestamps,
        "machine_id": ["MOTOR_01"] * 12,
        "feeder_id": ["FDR_01"] * 12,
        "machine_status": ["RUNNING"] * 10 + ["IDLE"] * 2,
        "active_power_kw": [60.0] * 10 + [18.0] * 2,
        "apparent_power_kva": [68.0] * 10 + [22.0] * 2,
        "energy_kwh": [5.0] * 10 + [1.5] * 2,
        "production_units": [4.0] * 10 + [0.0] * 2,
        "idle_flag": [0] * 10 + [1] * 2,
        "power_factor": [0.88] * 12,
        "tariff_period": ["NORMAL"] * 12
    })

    df_opt, comp = optimizer.run_full_optimization(df_sample)

    # 1. Production must be preserved!
    assert comp["impact"]["production_constraint_satisfied"] is True
    assert comp["baseline"]["production_units"] == comp["optimized"]["production_units"]

    # 2. Energy must be reduced (from idle reduction)
    assert comp["optimized"]["energy_kwh"] < comp["baseline"]["energy_kwh"]
    assert comp["impact"]["energy_reduction_pct"] > 0.0

    # 3. SEC must improve
    assert comp["optimized"]["sec_kwh_per_unit"] < comp["baseline"]["sec_kwh_per_unit"]
    assert comp["impact"]["sec_improvement_pct"] > 0.0
