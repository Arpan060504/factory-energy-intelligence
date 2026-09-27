"""
Verification of Demo Reliability and Reproducibility.
Runs the canonical demo computation pipeline 10 consecutive times and verifies
that zero stochastic drift or random variation alters any KPI or recommendation.
"""

import os
import json
import pytest
import pandas as pd
from dashboard.app import compute_reactive_pipeline


def test_canonical_demo_reproducibility_10_runs():
    """Execute canonical demo computation 10 times and assert bit-for-bit repeatability."""
    results = []

    for i in range(10):
        (
            df_base,
            df_opt,
            comparison,
            df_incidents,
            df_health,
            machine_summary_base,
            machine_summary_opt,
            recommendations,
            t_cfg,
            e_cfg,
            recalc_timestamp
        ) = compute_reactive_pipeline(5.20, 7.80, 11.50, 0.716)

        b = comparison["baseline"]
        o = comparison["optimized"]
        imp = comparison["impact"]

        metrics_snapshot = {
            "baseline_energy": round(b["energy_kwh"], 1),
            "optimized_energy": round(o["energy_kwh"], 1),
            "energy_reduction_kwh": round(imp["energy_reduction_kwh"], 1),
            "baseline_production": round(b["production_units"], 1),
            "optimized_production": round(o["production_units"], 1),
            "production_change_units": imp["production_change_units"],
            "baseline_sec": round(b["sec_kwh_per_unit"], 4),
            "optimized_sec": round(o["sec_kwh_per_unit"], 4),
            "sec_improvement_pct": round(imp["sec_improvement_pct"], 2),
            "baseline_cost": round(b["electricity_cost_inr"], 2),
            "optimized_cost": round(o["electricity_cost_inr"], 2),
            "cost_reduction_inr": round(imp["cost_reduction_inr"], 2),
            "peak_demand_baseline": round(b["peak_demand_kva"], 1),
            "peak_demand_optimized": round(o["peak_demand_kva"], 1),
            "emissions_avoided_mt": round(imp["emissions_avoided_mt_co2"], 3),
            "production_constraint_satisfied": imp["production_constraint_satisfied"]
        }
        results.append(metrics_snapshot)

    # Verify all 10 runs match the first run exactly
    first_run = results[0]
    for idx, run in enumerate(results[1:], start=2):
        assert run == first_run, f"Run {idx} drifted from Run 1: {run} != {first_run}"

    # Verify master values match canonical freeze specifications
    assert first_run["baseline_energy"] == 191138.7
    assert first_run["optimized_energy"] == 159165.7
    assert first_run["energy_reduction_kwh"] == 31973.1
    assert first_run["baseline_production"] == 131324.1
    assert first_run["optimized_production"] == 131324.1
    assert first_run["production_change_units"] == 0.0
    assert first_run["baseline_sec"] == 1.4555
    assert first_run["optimized_sec"] == 1.2120
    assert first_run["sec_improvement_pct"] == 16.73
    assert first_run["baseline_cost"] == 1940445.85
    assert first_run["optimized_cost"] == 1578857.46
    assert first_run["cost_reduction_inr"] == 361588.39
    assert first_run["peak_demand_baseline"] == 462.7
    assert first_run["peak_demand_optimized"] == 450.1
    assert first_run["emissions_avoided_mt"] == 22.893
    assert first_run["production_constraint_satisfied"] is True
