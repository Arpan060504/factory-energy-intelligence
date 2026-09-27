# Engineering Hardening & Model Freeze Plan

## 1. Objective & Scope

This hardening plan defines the remedial engineering actions required to transition the **Factory Energy Intelligence & Optimization Platform** from an audited prototype to a **frozen, defensible, industrial-grade software release** ready for evaluation at the Smart Manufacturing challenge.

In accordance with Phase 3 instructions:
- **No new features are added.**
- **No dashboard redesigns or aesthetic changes are permitted.**
- **All identified RED and AMBER issues from the adversarial stress test are resolved with technical rigor.**
- **Over-promising marketing claims are replaced with defensible engineering language.**
- **The canonical scenario, dataset, models, and KPI values are frozen.**

---

## 2. Issue Tracking Matrix (RED & AMBER Issues)

| ID | Issue Description | Severity | Root Cause | Engineering Fix | Validation Method | Target Status |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| **RED-01** | `calculate_sec()` returns `0.0` when production is zero or missing, falsely implying zero energy per unit or infinite efficiency. | **RED** | `src/energy/analytics.py` hardcoded `if production_units <= 0.001: return 0.0`. | Refactor `calculate_sec()` to return `None` (or `NaN`), and update dashboard/summaries to render `"SEC Unavailable / Non-Productive"`. | Automated unit test with `production=0` asserting `result is None`; verify dashboard gracefully displays label. | **FIXED** |
| **RED-02** | Current sensor dropout / open CT circuit misclassified as switchgear terminal contact unbalance. | **RED** | `AnomalyDetector` evaluated NEMA unbalance without checking if a phase current dropped to $0.0\text{ A}$ while others remain heavily loaded. | Add pre-screening in `src/anomaly/detector.py`: if any phase current is $< 0.1\text{ A}$ while $V > 350\text{ V}$ and other phases $> 15\text{ A}$, flag `DATA_QUALITY_CURRENT_SENSOR_LOST`. | Inject single-phase zero-current test; assert sensor loss alarm triggers instead of mechanical unbalance. | **FIXED** |
| **RED-03** | Capex discrepancy between `scripts/run_demo.py` (₹1,52,400) and `docs/business_model.md` / `dashboard/app.py` (₹1,52,150). | **RED** | Outdated hardcoded print string in demo script from early draft BOM estimate. | Update `scripts/run_demo.py` to match the exact BOM total of **₹ 1,52,150**. | Script execution check confirming ₹1,52,150 is printed. | **FIXED** |
| **RED-04** | Optimization production constraint violation guardrail on dashboard. | **RED** | If a future optimization schedule violated production throughput, the UI had no prominent error barrier. | Add strict UI guardrail in `dashboard/app.py`: if `not impact['production_constraint_satisfied']`, halt optimization metric display and display critical error banner. | Unit test verifying constraint checker flags any schedule where $\text{Prod}_{\text{opt}} < \text{Prod}_{\text{base}}$. | **FIXED** |
| **AMB-01** | Business model payback qualification (13-day steady-state vs. 1.8–3.5 month phased ramp-up). | **AMBER** | Evaluators could challenge an instantaneous 13-day simple payback as "too good to be true" if not qualified against phased adoption. | Explicitly document both metrics in `docs/business_model.md`, `docs/assumptions.md`, and Page 7 sensitivity table: 13-day instantaneous steady-state vs. 1.8–3.5 month phased implementation. | Cross-document consistency audit. | **FIXED** |
| **AMB-02** | Strong marketing claims in documentation and UI ("guaranteed savings", "predicts failure", "AI-powered"). | **AMBER** | Residual hackathon promotional phrases that fail hostile expert scrutiny. | Audit and rewrite all occurrences across `README.md`, `dashboard/app.py`, and `docs/` using defensible engineering language (e.g. "Scenario-based optimization demonstrates...", "Detects abnormal operating signatures..."). | Full-text grep search audit across repository. | **FIXED** |
| **AMB-03** | RIL reference data boundary clarity. | **AMBER** | Evaluators might confuse anonymized field reference data with synchronized plant telemetry. | Explicitly document in `README.md`, `docs/data_validation_report.md`, and dashboard that RIL data is used solely for empirical range calibration, not synchronized factory telemetry. | Documentation review. | **FIXED** |
| **AMB-04** | Cable loss and health score labeling. | **AMBER** | Risk of evaluators mistaking model-calculated feeder losses for direct physical sensor measurements. | Ensure all charts and KPI cards explicitly state: "Model Estimate ($I^2R$)" and "Algorithmic screening heuristic, NOT OEM RUL prediction." | Dashboard inspection on Pages 2, 3, and 4. | **FIXED** |
| **AMB-05** | Canonical demo scenario serialization. | **AMBER** | Lack of a single deterministic JSON configuration file defining the canonical hackathon demo. | Create `data/demo_scenario.json` containing exact machine parameters, timestamps, baseline, and optimized values for clean reproducibility. | Verify `scripts/run_demo.py` loads and benchmarks against `data/demo_scenario.json`. | **FIXED** |
| **AMB-06** | Contradictory assumptions and duplicated constants. | **AMBER** | Redundant tariff or technical assumptions across files. | Audit repository to ensure `src/config.py` is the single source of truth for all economic and regulatory parameters. | Repository grep audit. | **FIXED** |

---

## 3. Execution Schedule & Freeze Protocol

1. **Step 1**: Implement core code fixes for RED-01 (`calculate_sec`), RED-02 (`DATA_QUALITY_CURRENT_SENSOR_LOST`), RED-03 (`run_demo.py` BOM Capex), and RED-04 (dashboard production guardrail).
2. **Step 2**: Perform claims audit and replace over-promising language across `README.md`, `dashboard/app.py`, and `docs/` (AMB-02).
3. **Step 3**: Reconcile and harmonize all business model and payback descriptions (AMB-01, AMB-03, AMB-04, AMB-06).
4. **Step 4**: Generate the canonical demo scenario specification in `data/demo_scenario.json` (AMB-05).
5. **Step 5**: Execute the complete test suite (`pytest tests/ -v`), run the master pipeline, and audit cross-page consistency.
6. **Step 6**: Issue `docs/model_freeze.md` to permanently freeze the dataset, models, and optimization methodology.
