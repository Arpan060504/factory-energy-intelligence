"""
Master End-to-End Execution Pipeline for Factory Energy Intelligence Platform.
Runs data generation, baseline training, anomaly detection, recommendations,
optimization simulation, and verification audits in a single command.
"""

import os
import sys
import time
import logging

# Add repository root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.anonymize_reference import anonymize_reference_data
from scripts.generate_dataset import generate_synthetic_dataset
from simulation.before_after import run_controlled_experiment

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Pipeline")


def run_full_pipeline(days: int = 30, interval: int = 5, seed: int = 42):
    start_total = time.time()
    logger.info("=" * 70)
    logger.info("STARTING FACTORY ENERGY INTELLIGENCE MASTER PIPELINE")
    logger.info("=" * 70)

    # 1. Anonymize industrial reference measurements
    logger.info("STEP 1: Calibrating against industrial reference distributions...")
    try:
        anonymize_reference_data()
    except Exception as e:
        logger.warning(f"Reference data anonymization skipped/fallback: {e}")

    # 2. Generate physics-grounded synthetic factory timeseries
    logger.info(f"STEP 2: Generating synthetic factory timeseries ({days} days, {interval} min)...")
    generate_synthetic_dataset(days=days, interval_minutes=interval, random_seed=seed)

    # 3. Execute baseline modeling, diagnostics, and controlled optimization
    logger.info("STEP 3: Running baseline modeling, anomaly detection & optimization...")
    comparison = run_controlled_experiment()

    elapsed = time.time() - start_total
    logger.info("=" * 70)
    logger.info(f"PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f} SECONDS")
    logger.info("=" * 70)
    return comparison


if __name__ == "__main__":
    run_full_pipeline()
