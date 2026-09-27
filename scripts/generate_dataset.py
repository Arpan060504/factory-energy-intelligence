"""
Physics-Grounded Synthetic Dataset Generator for Indian SME Manufacturing.
Simulates a 30-day continuous 5-minute operational timeline for 7 major industrial machines.
Embeds 7 explicit industrial anomaly scenarios with ground-truth labels.
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Conductor Resistivity at 20 deg C (Ohm * mm2 / m) and temperature coefficient
RHO_20 = {
    "ALUMINIUM": 0.0282,
    "COPPER": 0.0175
}
ALPHA = {
    "ALUMINIUM": 0.00403,
    "COPPER": 0.00393
}

# Machine Master Specifications (Generic Indian SME Precision Engineering Plant)
MACHINE_SPECS = [
    {
        "machine_id": "MOTOR_01",
        "machine_name": "CNC Machining Center",
        "machine_type": "CNC_MACHINING",
        "feeder_id": "FDR_01",
        "rated_power_kw": 75.0,
        "rated_voltage_v": 415.0,
        "rated_current_a": 125.0,
        "base_pf": 0.88,
        "standby_power_kw": 4.5,
        "idle_power_kw": 18.0,
        "nominal_production_uph": 45.0,
        "cable_length_m": 65.0,
        "cable_cross_section_mm2": 95.0,
        "cable_conductor": "ALUMINIUM",
        "base_temp_c": 42.0,
        "base_vib_mms": 1.6,
        "is_flexible_load": False
    },
    {
        "machine_id": "MOTOR_02",
        "machine_name": "Hydraulic Stamping Press",
        "machine_type": "HYDRAULIC_PRESS",
        "feeder_id": "FDR_02",
        "rated_power_kw": 55.0,
        "rated_voltage_v": 415.0,
        "rated_current_a": 95.0,
        "base_pf": 0.85,
        "standby_power_kw": 3.0,
        "idle_power_kw": 14.0,
        "nominal_production_uph": 120.0,
        "cable_length_m": 45.0,
        "cable_cross_section_mm2": 70.0,
        "cable_conductor": "ALUMINIUM",
        "base_temp_c": 45.0,
        "base_vib_mms": 1.8,
        "is_flexible_load": True  # Batch stamping can be shifted
    },
    {
        "machine_id": "PUMP_01",
        "machine_name": "Chilled Water Circulation Pump",
        "machine_type": "COOLING_PUMP",
        "feeder_id": "FDR_03",
        "rated_power_kw": 30.0,
        "rated_voltage_v": 415.0,
        "rated_current_a": 52.0,
        "base_pf": 0.86,
        "standby_power_kw": 0.5,
        "idle_power_kw": 12.0,
        "nominal_production_uph": 0.0,  # Utility pump supports production
        "cable_length_m": 80.0,
        "cable_cross_section_mm2": 35.0,
        "cable_conductor": "ALUMINIUM",
        "base_temp_c": 38.0,
        "base_vib_mms": 1.4,
        "is_flexible_load": False
    },
    {
        "machine_id": "COMP_01",
        "machine_name": "Rotary Screw Air Compressor",
        "machine_type": "AIR_COMPRESSOR",
        "feeder_id": "FDR_04",
        "rated_power_kw": 45.0,
        "rated_voltage_v": 415.0,
        "rated_current_a": 78.0,
        "base_pf": 0.87,
        "standby_power_kw": 1.2,
        "idle_power_kw": 16.5,  # Unloaded spinning loss
        "nominal_production_uph": 0.0,  # Utility support
        "cable_length_m": 50.0,
        "cable_cross_section_mm2": 50.0,
        "cable_conductor": "ALUMINIUM",
        "base_temp_c": 62.0,
        "base_vib_mms": 2.1,
        "is_flexible_load": False
    },
    {
        "machine_id": "FURNACE_01",
        "machine_name": "Induction Billet Heating Furnace",
        "machine_type": "INDUCTION_FURNACE",
        "feeder_id": "FDR_05",
        "rated_power_kw": 160.0,
        "rated_voltage_v": 415.0,
        "rated_current_a": 255.0,
        "base_pf": 0.92,
        "standby_power_kw": 8.0,
        "idle_power_kw": 35.0,
        "nominal_production_uph": 80.0,  # Billets heated per hour
        "cable_length_m": 30.0,
        "cable_cross_section_mm2": 185.0,
        "cable_conductor": "COPPER",
        "base_temp_c": 75.0,
        "base_vib_mms": 0.8,
        "is_flexible_load": True  # High flexibility for batch pre-heating
    },
    {
        "machine_id": "LINE_01",
        "machine_name": "Conveyor & Final Assembly Line",
        "machine_type": "CONVEYOR_LINE",
        "feeder_id": "FDR_06",
        "rated_power_kw": 22.0,
        "rated_voltage_v": 415.0,
        "rated_current_a": 38.0,
        "base_pf": 0.84,
        "standby_power_kw": 1.0,
        "idle_power_kw": 6.0,
        "nominal_production_uph": 60.0,
        "cable_length_m": 110.0,
        "cable_cross_section_mm2": 25.0,
        "cable_conductor": "ALUMINIUM",
        "base_temp_c": 35.0,
        "base_vib_mms": 1.1,
        "is_flexible_load": False
    },
    {
        "machine_id": "AUX_01",
        "machine_name": "Plant Utilities, Exhaust & Lighting",
        "machine_type": "UTILITY_AUX",
        "feeder_id": "FDR_07",
        "rated_power_kw": 25.0,
        "rated_voltage_v": 415.0,
        "rated_current_a": 42.0,
        "base_pf": 0.90,
        "standby_power_kw": 3.0,
        "idle_power_kw": 8.0,
        "nominal_production_uph": 0.0,
        "cable_length_m": 90.0,
        "cable_cross_section_mm2": 25.0,
        "cable_conductor": "ALUMINIUM",
        "base_temp_c": 32.0,
        "base_vib_mms": 0.6,
        "is_flexible_load": False
    }
]


def calculate_cable_resistance(material: str, length_m: float, area_mm2: float, temp_c: float = 50.0) -> float:
    """Calculates single-conductor cable resistance in Ohms at operating temperature."""
    rho_20 = RHO_20[material.upper()]
    alpha = ALPHA[material.upper()]
    rho_t = rho_20 * (1.0 + alpha * (temp_c - 20.0))
    return rho_t * (length_m / area_mm2)


def get_tariff_period(hour: int) -> str:
    """Classifies Time-of-Day (TOD) tariff slot per Indian State DISCOM standard."""
    if 18 <= hour < 22:
        return "PEAK"  # Evening peak (18:00 - 22:00)
    elif 22 <= hour or hour < 6:
        return "OFF_PEAK"  # Night off-peak (22:00 - 06:00)
    else:
        return "NORMAL"  # Day normal (06:00 - 18:00)


def generate_synthetic_dataset(
    days: int = 30,
    interval_minutes: int = 5,
    random_seed: int = 42,
    output_path: str = None
) -> pd.DataFrame:
    np.random.seed(random_seed)
    
    start_time = datetime(2026, 3, 1, 0, 0, 0)
    total_steps = int(days * 24 * 60 / interval_minutes)
    timestamps = [start_time + timedelta(minutes=i * interval_minutes) for i in range(total_steps)]
    
    records = []
    
    # Precompute cable resistances
    cable_r = {
        m["machine_id"]: calculate_cable_resistance(
            m["cable_conductor"], m["cable_length_m"], m["cable_cross_section_mm2"], 50.0
        )
        for m in MACHINE_SPECS
    }

    for step_idx, ts in enumerate(timestamps):
        day_of_month = ts.day
        hour = ts.hour
        minute = ts.minute
        weekday = ts.weekday()  # 0=Monday, 6=Sunday
        tariff = get_tariff_period(hour)
        
        # Diurnal ambient temperature profile (22 to 36 deg C)
        ambient_temp = 25.0 + 8.0 * np.sin(np.pi * (hour - 8.0) / 12.0) + np.random.normal(0, 0.4)
        
        # Grid line-to-line voltage with slight diurnal drift (415V nominal +/- 3%)
        grid_v_base = 415.0 - 5.0 * np.sin(np.pi * (hour - 14.0) / 12.0)
        v_avg = float(np.clip(grid_v_base + np.random.normal(0, 1.8), 395.0, 435.0))
        
        # Shop floor operating schedule
        is_sunday = (weekday == 6)
        is_lunch = (13 <= hour < 14) and (minute < 30)
        is_tea_break = (10 <= hour < 11) and (15 <= minute < 30)
        is_shift_change = (13 <= hour < 14) and (45 <= minute <= 59) or (21 <= hour < 22) and (45 <= minute <= 59)
        
        # Plant operational state
        plant_shift_active = not is_sunday and (6 <= hour < 22)
        plant_night_active = not is_sunday and (hour >= 22 or hour < 6)

        for spec in MACHINE_SPECS:
            mid = spec["machine_id"]
            mtype = spec["machine_type"]
            rated_p = spec["rated_power_kw"]
            base_pf = spec["base_pf"]
            standby_p = spec["standby_power_kw"]
            idle_p = spec["idle_power_kw"]
            nominal_uph = spec["nominal_production_uph"]
            base_temp = spec["base_temp_c"]
            base_vib = spec["base_vib_mms"]
            r_cable = cable_r[mid]

            # Determine baseline operational state
            if is_sunday:
                # Factory shut; only security, essential exhaust, or idle standby
                status = "OFF" if mid not in ["AUX_01", "PUMP_01"] else "IDLE"
            elif is_lunch or is_tea_break or is_shift_change:
                status = "IDLE"
            elif plant_shift_active:
                status = "RUNNING"
            elif plant_night_active:
                # Night shift: partial operation (furnace batching, machining runs, or idling)
                if mid in ["FURNACE_01", "PUMP_01", "COMP_01"]:
                    status = "RUNNING"
                elif mid == "MOTOR_01":
                    status = "RUNNING" if (step_idx % 2 == 0) else "IDLE"
                else:
                    status = "IDLE"
            else:
                status = "OFF"

            # Compute power and production
            idle_flag = 0
            defect_type = "NONE"

            if status == "OFF":
                active_p = standby_p + np.random.uniform(0.0, 0.2)
                prod_rate = 0.0
                prod_units = 0.0
                pf = 0.55 + np.random.uniform(-0.02, 0.02)
                temp = ambient_temp + 2.0 + np.random.uniform(-0.5, 0.5)
                vib = 0.2 + np.random.uniform(0.0, 0.1)

            elif status == "IDLE":
                idle_flag = 1
                active_p = idle_p + np.random.normal(0, idle_p * 0.04)
                prod_rate = 0.0
                prod_units = 0.0
                pf = base_pf - 0.12 + np.random.normal(0, 0.01)  # Unloaded motor has poorer PF
                temp = base_temp - 5.0 + np.random.normal(0, 0.5)
                vib = base_vib * 0.7 + np.random.normal(0, 0.05)

            else:  # RUNNING
                load_factor = np.random.uniform(0.75, 0.92)
                active_p = rated_p * load_factor + np.random.normal(0, rated_p * 0.02)
                prod_rate = nominal_uph * (load_factor / 0.85) + np.random.normal(0, 1.2)
                prod_rate = max(0.0, prod_rate)
                prod_units = prod_rate * (interval_minutes / 60.0)
                pf = base_pf + np.random.normal(0, 0.01)
                temp = base_temp + 12.0 * (load_factor - 0.7) + np.random.normal(0, 0.8)
                vib = base_vib + np.random.normal(0, 0.1)

            # =========================================================
            # INJECT DELIBERATE ANOMALY SCENARIOS
            # =========================================================

            # SCENARIO 1: Motor Efficiency Degradation (Bearing wear on MOTOR_01)
            # Window: Days 7 to 10
            if mid == "MOTOR_01" and 7 <= day_of_month <= 10:
                defect_type = "MOTOR_EFFICIENCY_DEGRADATION"
                if status == "RUNNING":
                    active_p *= 1.16  # +16% power without production gain
                    temp += 15.0      # +15 deg C thermal rise
                    vib += 3.2        # severe vibration spike (exceeds 4.5 mm/s ISO limit)

            # SCENARIO 2: Excessive Compressor Idle Operation (COMP_01 air leaks)
            # Window: Days 12 to 16
            if mid == "COMP_01" and 12 <= day_of_month <= 16:
                defect_type = "EXCESSIVE_IDLE_CONSUMPTION"
                # Even when factory is in break or night, compressor continues running unloaded
                if is_lunch or is_tea_break or is_shift_change or (hour >= 23 or hour < 5):
                    status = "RUNNING"
                    idle_flag = 1
                    active_p = 22.5 + np.random.normal(0, 0.8)  # High unloaded idle power
                    prod_units = 0.0
                    temp += 6.0

            # SCENARIO 3: Low Power Factor Event (APFC Bank failure on FDR_02 / MOTOR_02 & COMP_01)
            # Window: Days 18 to 20
            if mid in ["MOTOR_02", "COMP_01"] and 18 <= day_of_month <= 20:
                defect_type = "LOW_POWER_FACTOR"
                pf = float(np.clip(pf - 0.16, 0.68, 0.74))

            # SCENARIO 4: Three-Phase Current Imbalance (Loose contactor lug on PUMP_01)
            # Window: Days 21 to 23
            is_imbalance_anomaly = False
            if mid == "PUMP_01" and 21 <= day_of_month <= 23:
                defect_type = "PHASE_IMBALANCE"
                is_imbalance_anomaly = True

            # SCENARIO 5: Abnormal Energy Consumption (Furnace Refractory Degradation on FURNACE_01)
            # Window: Days 24 to 27
            if mid == "FURNACE_01" and 24 <= day_of_month <= 27:
                defect_type = "ABNORMAL_ENERGY_CONSUMPTION"
                if status == "RUNNING":
                    active_p *= 1.23  # +23% excess power to maintain heat
                    temp += 18.0

            # SCENARIO 6: Inefficient Production Scheduling (Peak Tariff Operation)
            # Window: Days 14 to 28 on FURNACE_01 during Peak window (18:00 - 22:00)
            if mid == "FURNACE_01" and 14 <= day_of_month <= 28 and tariff == "PEAK":
                if status == "RUNNING":
                    defect_type = "INEFFICIENT_PEAK_SCHEDULING"

            # SCENARIO 7: Machine Degradation Compound Failure (MOTOR_02 hydraulic cavitation)
            # Window: Days 27 to 29
            if mid == "MOTOR_02" and 27 <= day_of_month <= 29:
                defect_type = "MACHINE_DEGRADATION"
                if status == "RUNNING":
                    active_p *= 1.15
                    temp += 19.0
                    vib += 3.8

            # Ensure valid bounds
            pf = float(np.clip(pf, 0.50, 0.99))
            active_p = max(0.05, float(active_p))
            
            # Physics calculations
            apparent_kva = active_p / pf
            reactive_kvar = np.sqrt(max(0.0, apparent_kva**2 - active_p**2))
            
            # Line current calculation from 3-phase power: I = P * 1000 / (sqrt(3) * V * PF)
            i_avg = (active_p * 1000.0) / (np.sqrt(3.0) * v_avg * pf)
            
            # Phase currents with normal random slight unbalance (<2.5%) or Scenario 4 severe unbalance
            if is_imbalance_anomaly and status in ["RUNNING", "IDLE"]:
                i_r = i_avg * 1.35
                i_y = i_avg * 0.98
                i_b = i_avg * 0.67
            else:
                unbal_noise = np.random.normal(0, 0.012, 3)
                i_r = max(0.0, i_avg * (1.0 + unbal_noise[0]))
                i_y = max(0.0, i_avg * (1.0 + unbal_noise[1]))
                i_b = max(0.0, i_avg * (1.0 + unbal_noise[2]))
            
            curr_avg_actual = (i_r + i_y + i_b) / 3.0
            
            # NEMA current imbalance %
            if curr_avg_actual > 0.1:
                imbalance_pct = (max(abs(i_r - curr_avg_actual), abs(i_y - curr_avg_actual), abs(i_b - curr_avg_actual)) / curr_avg_actual) * 100.0
            else:
                imbalance_pct = 0.0

            # Energy in interval (kWh)
            energy_kwh = active_p * (interval_minutes / 60.0)
            
            # Estimated cable Joule loss (kW) = 3 * I_avg^2 * R / 1000
            cable_loss_kw = (3.0 * (curr_avg_actual**2) * r_cable) / 1000.0

            records.append({
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "machine_id": mid,
                "machine_name": spec["machine_name"],
                "machine_type": mtype,
                "feeder_id": spec["feeder_id"],
                "substation_id": "SUB_01",
                "bus_id": "BUS_A",
                "voltage": round(v_avg, 2),
                "current_r": round(float(i_r), 2),
                "current_y": round(float(i_y), 2),
                "current_b": round(float(i_b), 2),
                "average_current": round(float(curr_avg_actual), 2),
                "current_imbalance_pct": round(float(imbalance_pct), 2),
                "power_factor": round(float(pf), 3),
                "apparent_power_kva": round(float(apparent_kva), 2),
                "active_power_kw": round(float(active_p), 2),
                "reactive_power_kvar": round(float(reactive_kvar), 2),
                "energy_kwh": round(float(energy_kwh), 4),
                "estimated_cable_loss_kw": round(float(cable_loss_kw), 3),
                "temperature": round(float(temp), 2),
                "vibration": round(float(vib), 2),
                "machine_status": status,
                "idle_flag": int(idle_flag),
                "production_units": round(float(prod_units), 2),
                "production_rate": round(float(prod_rate), 2),
                "tariff_period": tariff,
                "maintenance_state": "OVERDUE" if defect_type != "NONE" else "NORMAL",
                "ground_truth_anomaly": defect_type
            })

    df = pd.DataFrame(records)
    
    if output_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(base_dir, "data", "synthetic", "factory_timeseries.csv")
        manifest_path = os.path.join(base_dir, "data", "synthetic", "scenario_manifest.json")
    else:
        manifest_path = os.path.splitext(output_path)[0] + "_manifest.json"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated synthetic factory timeseries: {output_path}")
    print(f"Total records: {len(df):,} across {len(MACHINE_SPECS)} machines for {days} days.")

    # Generate scenario manifest
    manifest = {
        "dataset_name": "Apex Precision Components Ltd. - Synthetic Time-Series",
        "generated_at": datetime.now().isoformat(),
        "total_records": len(df),
        "days": days,
        "interval_minutes": interval_minutes,
        "random_seed": random_seed,
        "machines": [m["machine_id"] for m in MACHINE_SPECS],
        "scenarios": [
            {
                "id": "SCENARIO_1",
                "name": "Motor Efficiency Degradation",
                "machine_id": "MOTOR_01",
                "window": "Day 7 to Day 10",
                "symptoms": "Power +16%, Temp +15C, Vibration > 4.5 mm/s, Production constant"
            },
            {
                "id": "SCENARIO_2",
                "name": "Excessive Compressor Idle Operation",
                "machine_id": "COMP_01",
                "window": "Day 12 to Day 16",
                "symptoms": "Continuous unloaded run (22.5 kW) during breaks and night hours"
            },
            {
                "id": "SCENARIO_3",
                "name": "Low Power Factor Event",
                "machine_id": "MOTOR_02, COMP_01",
                "window": "Day 18 to Day 20",
                "symptoms": "PF drops to 0.71, Apparent power surges, kVA penalty risk"
            },
            {
                "id": "SCENARIO_4",
                "name": "Three-Phase Current Imbalance",
                "machine_id": "PUMP_01",
                "window": "Day 21 to Day 23",
                "symptoms": "Phase R/Y/B currents diverge, Imbalance > 28% (NEMA)"
            },
            {
                "id": "SCENARIO_5",
                "name": "Abnormal Energy Consumption",
                "machine_id": "FURNACE_01",
                "window": "Day 24 to Day 27",
                "symptoms": "Actual active power +23% above expected baseline (refractory wear)"
            },
            {
                "id": "SCENARIO_6",
                "name": "Inefficient Production Scheduling",
                "machine_id": "FURNACE_01",
                "window": "Day 14 to Day 28",
                "symptoms": "160 kW thermal batch scheduled in Peak tariff slot (18:00 - 22:00)"
            },
            {
                "id": "SCENARIO_7",
                "name": "Machine Degradation Compound Failure",
                "machine_id": "MOTOR_02",
                "window": "Day 27 to Day 29",
                "symptoms": "Current +15%, Temp +19C, Vibration 5.4 mm/s (hydraulic cavitation)"
            }
        ]
    }
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Saved scenario manifest: {manifest_path}")

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic SME factory dataset")
    parser.add_argument("--days", type=int, default=30, help="Simulation duration in days")
    parser.add_argument("--interval", type=int, default=5, help="Sampling interval in minutes")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output", type=str, default=None, help="Output CSV path")
    args = parser.parse_args()

    generate_synthetic_dataset(
        days=args.days,
        interval_minutes=args.interval,
        random_seed=args.seed,
        output_path=args.output
    )
