"""
Controlled Before-vs-After Experiment Simulator.
Executes baseline evaluation, anomaly diagnosis, and optimization passes,
exporting processed datasets and verifying production throughput invariance.
"""

import os
import sys
import json
import logging
import pandas as pd

# Add repository root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.baseline.engine import FactoryBaselineEngine
from src.anomaly.detector import AnomalyDetector
from src.maintenance.health import MachineHealthEngine
from src.recommendations.engine import RecommendationEngine
from src.optimization.optimizer import FactoryOptimizer
from src.energy.analytics import EnergyAnalyticsEngine
from src.energy.cost_model import ElectricityCostCalculator

from src.config import TariffConfig, EmissionConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Simulator")


def run_controlled_experiment(
    synthetic_csv_path: str = None,
    output_dir: str = None,
    tariff_config: TariffConfig = None,
    emission_config: EmissionConfig = None
) -> dict:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    t_cfg = tariff_config or TariffConfig()
    e_cfg = emission_config or EmissionConfig()
    if synthetic_csv_path is None:
        synthetic_csv_path = os.path.join(base_dir, "data", "synthetic", "factory_timeseries.csv")
    if output_dir is None:
        output_dir = os.path.join(base_dir, "data", "processed")

    os.makedirs(output_dir, exist_ok=True)

    logger.info(f"Loading synthetic dataset from {synthetic_csv_path}...")
    df_raw = pd.read_csv(synthetic_csv_path)

    # 1. Fit production-normalized baseline & compute deviations
    logger.info("Fitting production-normalized baseline models...")
    baseline_engine = FactoryBaselineEngine(models_dir=os.path.join(base_dir, "models"))
    baseline_engine.train_all(df_raw)
    df_with_baseline = baseline_engine.compute_deviations(df_raw)
    
    baseline_csv_path = os.path.join(output_dir, "factory_with_baseline.csv")
    df_with_baseline.to_csv(baseline_csv_path, index=False)
    logger.info(f"Saved baseline deviations to {baseline_csv_path}")

    # 2. Run Anomaly Detection & Incident Aggregation
    logger.info("Executing rule-based & statistical anomaly detection...")
    detector = AnomalyDetector()
    alerts = detector.scan_dataframe(df_with_baseline)
    df_incidents = detector.aggregate_alert_incidents(alerts)
    incidents_path = os.path.join(output_dir, "incidents_summary.csv")
    df_incidents.to_csv(incidents_path, index=False)
    logger.info(f"Identified {len(alerts)} raw alerts, consolidated into {len(df_incidents)} incidents.")

    # 3. Evaluate Fleet Health
    logger.info("Computing machine health scores across fleet...")
    health_engine = MachineHealthEngine()
    df_fleet_health = health_engine.evaluate_fleet_health(df_with_baseline)
    health_path = os.path.join(output_dir, "machine_health_fleet.csv")
    df_fleet_health.to_csv(health_path, index=False)

    # 4. Generate Actionable SOP Recommendations
    logger.info("Generating quantified operator recommendations...")
    rec_engine = RecommendationEngine(tariff_config=t_cfg, emission_config=e_cfg)
    recommendations = rec_engine.generate_recommendations(df_incidents, df_fleet_health)
    recs_path = os.path.join(output_dir, "operator_recommendations.json")
    with open(recs_path, "w") as f:
        json.dump(recommendations, f, indent=2)

    # 5. Run Controlled Optimization (Idle + TOU Shifting)
    logger.info("Running controlled before vs. after optimization...")
    optimizer = FactoryOptimizer(tariff_config=t_cfg, emission_config=e_cfg)
    df_opt, comparison = optimizer.run_full_optimization(df_with_baseline)
    
    opt_csv_path = os.path.join(output_dir, "factory_optimized.csv")
    df_opt.to_csv(opt_csv_path, index=False)
    
    comparison_path = os.path.join(output_dir, "optimization_comparison.json")
    with open(comparison_path, "w") as f:
        json.dump(comparison, f, indent=2)

    # 6. Generate Machine-level Analytics Summary
    analytics_engine = EnergyAnalyticsEngine(tariff_config=t_cfg)
    machine_summary_base = analytics_engine.summarize_by_machine(df_with_baseline)
    machine_summary_path = os.path.join(output_dir, "machine_summary_baseline.csv")
    machine_summary_base.to_csv(machine_summary_path, index=False)

    machine_summary_opt = analytics_engine.summarize_by_machine(df_opt)
    machine_summary_opt_path = os.path.join(output_dir, "machine_summary_optimized.csv")
    machine_summary_opt.to_csv(machine_summary_opt_path, index=False)

    # Print Verification Table (Using 'INR' for safe cross-platform console output)
    print("\n" + "=" * 70)
    print("CONTROLLED OPTIMIZATION EXPERIMENT AUDIT REPORT")
    print("=" * 70)
    print(f"Baseline Energy:        {comparison['baseline']['energy_kwh']:>12,.1f} kWh")
    print(f"Optimized Energy:       {comparison['optimized']['energy_kwh']:>12,.1f} kWh")
    print(f"Energy Reduction:       {comparison['impact']['energy_reduction_kwh']:>12,.1f} kWh ({comparison['impact']['energy_reduction_pct']}%)")
    print("-" * 70)
    print(f"Baseline Production:    {comparison['baseline']['production_units']:>12,.1f} units")
    print(f"Optimized Production:   {comparison['optimized']['production_units']:>12,.1f} units")
    print(f"Production Invariance:  {str(comparison['impact']['production_constraint_satisfied']):>12} (Change: {comparison['impact']['production_change_units']} units)")
    print("-" * 70)
    print(f"Baseline SEC:           {comparison['baseline']['sec_kwh_per_unit']:>12.4f} kWh/unit")
    print(f"Optimized SEC:          {comparison['optimized']['sec_kwh_per_unit']:>12.4f} kWh/unit")
    print(f"SEC Improvement:        {comparison['impact']['sec_improvement_pct']:>12.2f} %")
    print("-" * 70)
    print(f"Baseline Energy Cost:   INR {comparison['baseline']['electricity_cost_inr']:>12,.2f}")
    print(f"Optimized Energy Cost:  INR {comparison['optimized']['electricity_cost_inr']:>12,.2f}")
    print(f"Cost Reduction:         INR {comparison['impact']['cost_reduction_inr']:>12,.2f} ({comparison['impact']['cost_reduction_pct']}%)")
    print("-" * 70)
    print(f"Peak Demand Reduction:  {comparison['impact']['peak_demand_reduction_kva']:>12.1f} kVA ({comparison['impact']['peak_demand_reduction_pct']}%)")
    print(f"Carbon CO2 Avoided:     {comparison['impact']['emissions_avoided_kg_co2']:>12,.1f} kg ({comparison['impact']['emissions_avoided_mt_co2']} MT CO2)")
    print("=" * 70 + "\n")

    return comparison


if __name__ == "__main__":
    run_controlled_experiment()
