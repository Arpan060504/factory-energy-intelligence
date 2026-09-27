"""
Anonymize and extract industrial operating parameters from field distribution measurements.
Strips proprietary metadata, normalizes IDs to generic tokens (SUB_01, FEEDER_01),
and computes empirical distributions to calibrate synthetic SME parameters.
"""

import os
import json
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Anonymizer")

DEFAULT_SOURCE_PATH = r"D:\coding\Project\Power_distribution_analytics\data\processed"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "reference")


def anonymize_reference_data(source_dir: str = DEFAULT_SOURCE_PATH, output_dir: str = OUTPUT_DIR) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    
    measurements_file = os.path.join(source_dir, "fact_electrical_measurements.csv")
    feeders_file = os.path.join(source_dir, "dim_feeder.csv")
    transformers_file = os.path.join(source_dir, "dim_transformer.csv")
    loads_file = os.path.join(source_dir, "dim_load.csv")

    if not os.path.exists(measurements_file):
        raise FileNotFoundError(f"Source file not found: {measurements_file}")

    logger.info("Loading reference dimensions and sample measurements...")
    df_feeder = pd.read_csv(feeders_file) if os.path.exists(feeders_file) else pd.DataFrame()
    df_tr = pd.read_csv(transformers_file) if os.path.exists(transformers_file) else pd.DataFrame()
    df_load = pd.read_csv(loads_file) if os.path.exists(loads_file) else pd.DataFrame()

    # Read representative sample (e.g. 10,000 rows across all feeders to capture full diurnal/load range)
    # Using chunksize or sample to avoid excessive memory
    logger.info("Reading representative sample from fact measurements...")
    sample_df = pd.read_csv(measurements_file, nrows=15000)

    # 1. Create ID Mappings
    unique_subs = sorted(sample_df["substation_id"].unique())
    sub_map = {orig: f"SUB_{i+1:02d}" for i, orig in enumerate(unique_subs)}

    unique_trs = sorted(sample_df["transformer_id"].unique())
    tr_map = {orig: f"TRANSFORMER_{i+1:02d}" for i, orig in enumerate(unique_trs)}

    unique_feeders = sorted(sample_df["feeder_id"].unique())
    feeder_map = {orig: f"FEEDER_{i+1:02d}" for i, orig in enumerate(unique_feeders)}

    load_type_map = {
        "LOAD_IND_PROC": "PROCESS_LOAD",
        "LOAD_IND_MOT": "INDUCTION_MOTOR",
        "LOAD_RES": "AUX_FACILITY",
        "LOAD_COMM": "COMMERCIAL_HVAC",
        "LOAD_LIGHT": "PLANT_LIGHTING",
        "LOAD_AUX": "PLANT_UTILITIES",
        "LOAD_AGRI": "PUMPING_STATION"
    }

    # 2. Anonymize Sample Measurements
    sample_df["substation_id"] = sample_df["substation_id"].map(sub_map)
    sample_df["transformer_id"] = sample_df["transformer_id"].map(tr_map)
    sample_df["feeder_id"] = sample_df["feeder_id"].map(feeder_map)
    sample_df["load_type_id"] = sample_df["load_type_id"].map(lambda x: load_type_map.get(x, "GENERIC_LOAD"))

    # Drop any raw internal indices
    cols_to_keep = [
        "substation_id", "transformer_id", "feeder_id", "load_type_id",
        "voltage_avg", "voltage_deviation_pct",
        "current_r", "current_y", "current_b", "current_avg", "current_imbalance_pct",
        "active_power_kw", "reactive_power_kvar", "apparent_power_kva",
        "power_factor", "frequency_hz", "feeder_loss_kw", "feeder_loss_pct",
        "ambient_temperature_c", "equipment_temperature_c"
    ]
    anonymized_df = sample_df[[c for c in cols_to_keep if c in sample_df.columns]].copy()
    
    # Save anonymized reference CSV
    anon_csv_path = os.path.join(output_dir, "anonymized_reference.csv")
    anonymized_df.to_csv(anon_csv_path, index=False)
    logger.info(f"Saved anonymized reference observations to {anon_csv_path} ({len(anonymized_df)} rows)")

    # 3. Extract Operating Range Calibration Profile
    calibration_ranges = {}
    for ltype, group in anonymized_df.groupby("load_type_id"):
        calibration_ranges[ltype] = {
            "voltage_median_v": float(np.round(group["voltage_avg"].median(), 1)),
            "voltage_p05_v": float(np.round(group["voltage_avg"].quantile(0.05), 1)),
            "voltage_p95_v": float(np.round(group["voltage_avg"].quantile(0.95), 1)),
            "current_median_a": float(np.round(group["current_avg"].median(), 1)),
            "current_p95_a": float(np.round(group["current_avg"].quantile(0.95), 1)),
            "power_factor_median": float(np.round(group["power_factor"].median(), 3)),
            "power_factor_p05": float(np.round(group["power_factor"].quantile(0.05), 3)),
            "power_factor_p95": float(np.round(group["power_factor"].quantile(0.95), 3)),
            "current_imbalance_median_pct": float(np.round(group["current_imbalance_pct"].median(), 2)),
            "feeder_loss_median_pct": float(np.round(group["feeder_loss_pct"].median(), 2)),
            "equipment_temp_median_c": float(np.round(group["equipment_temperature_c"].median(), 1)),
        }

    ranges_json_path = os.path.join(output_dir, "calibrated_operating_ranges.json")
    with open(ranges_json_path, "w") as f:
        json.dump(calibration_ranges, f, indent=2)
    logger.info(f"Saved calibrated empirical operating ranges to {ranges_json_path}")

    return calibration_ranges


if __name__ == "__main__":
    anonymize_reference_data()
