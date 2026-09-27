# Factory Energy Intelligence & Optimization Platform - Implementation Roadmap

This document outlines the systematic, phased engineering implementation roadmap from inception to final demonstrator.

---

## Roadmap Phases & Work Breakdown

| Phase | Steps | Objectives | Deliverables | Status |
|---|---|---|---|---|
| **Phase 1** | Steps 1–5 | Repository, Architecture, Engineering Equations & Specifications | Directory tree, `docs/architecture.md`, `docs/assumptions.md`, `docs/synthetic_data_design.md`, `README.md` | In Progress |
| **Phase 2** | Steps 6–8 | Reference Calibration & Synthetic Data Generation | `src/data/anonymize_reference.py`, `scripts/generate_dataset.py`, `data/reference/anonymized_reference.csv`, `data/synthetic/factory_timeseries.csv` | Planned |
| **Phase 3** | Steps 9–11 | Electrical Physics, Loss Calculations & SEC Analytics | `src/energy/calculations.py`, `src/energy/analytics.py`, cable loss models, feeder aggregation | Planned |
| **Phase 4** | Steps 12–14 | Explainable Baseline Model & Anomaly Diagnostics | `src/baseline/engine.py`, `src/anomaly/detector.py`, `src/maintenance/health.py`, 8 diagnostic alert types | Planned |
| **Phase 5** | Steps 15–17 | Recommendation Engine & Three-Tier Optimization | `src/recommendations/engine.py`, `src/optimization/optimizer.py` (Idle elimination, TOU load shifting, production scheduling) | Planned |
| **Phase 6** | Steps 18–19 | Before/After Verification, Tariff & Carbon Modules | `src/emissions/carbon.py`, `src/energy/cost_model.py`, `simulation/before_after.py` with production invariance checks | Planned |
| **Phase 7** | Steps 20–21 | FastAPI Backend & Interactive 7-Page Streamlit Dashboard | `backend/api/main.py`, `dashboard/app.py` (Executive, Analytics, Electrical, Health, Alerts, Optimization, Business) | Planned |
| **Phase 8** | Steps 22–23 | Automated Testing Suite, Demo Scripts & Final Audit | `tests/test_calculations.py`, `tests/test_scenarios.py`, `scripts/run_demo.py`, `scripts/run_pipeline.py` | Planned |

---

## Verification Criteria
Each phase requires:
1. Automated unit test verification using `pytest`.
2. Physical bounds check (e.g., active power $P \le S$, $\text{PF} \le 1.0$, $\text{Losses} \ge 0$, $\text{SEC} > 0$).
3. Zero tolerance for unlabelled assumptions or fabricated measurements.
