# Industrial Energy & Process Optimization Platform
## Section 11 Debugging & Architectural Audit Report: Configurable Tariff & Emission Reactivity

---

### Executive Summary

A functional defect was identified in the Streamlit application where user modifications to the sidebar controls:
1. **Off-Peak Rate (₹/kWh)**
2. **Normal Day Rate (₹/kWh)**
3. **Evening Peak Rate (₹/kWh)**
4. **Grid CO2 Factor (kg/kWh)**

failed to propagate through downstream analytical engines, optimization models, operator recommendations, and financial payback projections. The UI showed the new slider values, but all calculations on subsequent pages remained static.

Following an exhaustive forensic audit of the codebase, the root cause was traced to a combination of:
1. **Static Precomputed File Dependencies**: Downstream dashboard tabs were loading static JSON artifacts (`data/processed/optimization_comparison.json`) generated once during batch pipeline execution rather than recomputing dynamically.
2. **Coarse Stale Caching**: Data loading functions used `@st.cache_data` without incorporating user tariff and emission parameters into the cache key.
3. **Hardcoded Fallbacks in Business Logic**: Multiple domain modules (`src/recommendations/engine.py`, `src/anomaly/detector.py`, `dashboard/app.py`) had hardcoded financial and carbon constants rather than referencing a centralized configuration object.

This report documents the forensic investigation, the resolution architecture (`src/config.py`), and the verification results demonstrating that the platform now adheres strictly to **Reactive End-to-End Propagation** and **Physical-Economic Invariance Guarantees**.

---

### Detailed Audit of Sections A through I

#### A. Where the Sidebar Inputs Were Originally Defined
- **Original Location**: `dashboard/app.py` lines 167–178.
- **Original Implementation**:
  ```python
  off_peak_rate = st.sidebar.number_input("Off-Peak Rate (₹/kWh)", value=5.20, min_value=1.0, max_value=25.0, step=0.10)
  normal_rate = st.sidebar.number_input("Normal Day Rate (₹/kWh)", value=7.80, min_value=1.0, max_value=25.0, step=0.10)
  peak_rate = st.sidebar.number_input("Evening Peak Rate (₹/kWh)", value=11.50, min_value=1.0, max_value=30.0, step=0.10)
  grid_emission_factor = st.sidebar.number_input("Grid CO2 Factor (kg/kWh)", value=0.716, ...)
  ```
- **Flaw**: The captured variables (`off_peak_rate`, `normal_rate`, `peak_rate`, `grid_emission_factor`) were assigned in Streamlit local scope, but were not passed into the functions that computed optimization savings, machine breakdowns, or recommendation values. They remained isolated display widgets.

#### B. Where Tariff Calculations Actually Happen
- **Primary Engine**: `src/energy/cost_model.py` in class [`ElectricityCostCalculator`](file:///d:/coding/Project/graph/smart-manufacturing-energy/src/energy/cost_model.py).
- **Core Function**: `calculate_energy_cost(df: pd.DataFrame) -> Dict[str, Any]`
- **Calculation Mechanism**:
  1. Identifies Time-of-Day slot for each timestamp row (vectorized evaluation based on `TariffConfig`).
  2. Multiplies interval kilowatt-hours by the respective slot rate:
     $$E_i \times R(\text{Slot}_i)$$
  3. Computes slot subtotals: `peak_cost_inr`, `normal_cost_inr`, `off_peak_cost_inr`.
  4. Evaluates peak billing demand charges against contract demand (kVA) and applies two-tier Power Factor incentives/surcharges.
- **Resolution**: `ElectricityCostCalculator` now requires or accepts `TariffConfig(frozen=True)` as its single source of truth, enabling dynamic instantiation with active sidebar values.

#### C. Where the Optimization Model Reads Tariff Values
- **Primary Engine**: `src/optimization/optimizer.py` in class [`FactoryOptimizer`](file:///d:/coding/Project/graph/smart-manufacturing-energy/src/optimization/optimizer.py).
- **Core Methods**:
  - `optimize_tariff_load_shifting(df: pd.DataFrame)`
  - `run_full_optimization(df: pd.DataFrame)`
- **Calculation Mechanism**:
  The optimizer evaluates whether flexible batch processes (specifically the electric heat treatment furnace `FURNACE_01`) should be rescheduled out of the evening peak window (18:00–22:00) into off-peak night hours (22:00–06:00).
- **Economic Dispatch Logic**:
  ```python
  differential = self.tariff_config.peak_to_offpeak_differential  # peak_rate - off_peak_rate
  if differential > 0:
      # Economically viable to shift flexible load to off-peak slot
      tariff_savings = shift_energy_kwh * differential
  else:
      # Flat or inverted tariff: zero financial justification for schedule disruption
      tariff_savings = 0.0
      # Retain baseline schedule
  ```
- **Resolution**: `FactoryOptimizer` initializes its internal `ElectricityCostCalculator` and `CarbonCalculator` using the active `TariffConfig` and `EmissionConfig`, dynamically adapting schedule dispatch to real-time tariff differentials.

#### D. Where Business-Model Calculations Happen
- **Primary Engines**: `dashboard/app.py` (Page 7: SME Business Model & Payback) and `docs/business_model.md`.
- **Core Metrics**:
  - Monthly Energy Cost Savings (₹)
  - Annualized Net Benefit (₹)
  - Simple Payback Period (Months):
    $$\text{Payback} = \frac{\text{Platform Capex}}{\text{Monthly Cost Savings}}$$
  - 3-Year Net Cumulative ROI:
    $$\text{Net Benefit} = \sum_{m=1}^{36} \text{Monthly Savings}_m - (\text{Capex} + \text{Opex}_{3\text{yr}})$$
- **Resolution**: Previously, Page 7 used fixed figures (e.g., ₹2,28,000 baseline bill, ₹1,12,000 monthly savings) hardcoded in string templates. Page 7 now computes payback dynamically using the active `comparison["impact"]["cost_reduction_inr"]` derived directly from `compute_reactive_pipeline()`.

#### E. Where CO2 Calculations Happen
- **Primary Engine**: `src/emissions/carbon.py` in class [`CarbonCalculator`](file:///d:/coding/Project/graph/smart-manufacturing-energy/src/emissions/carbon.py).
- **Authority Benchmark**: Central Electricity Authority (CEA), Ministry of Power, Government of India — CO2 Baseline Database for the Indian Power Sector (User Guide Version 19.0, weighted average grid factor $0.716\text{ kg CO}_2\text{/kWh}$).
- **Core Methods**:
  - `calculate_emissions(energy_kwh: float) -> Dict[str, float]`
  - `calculate_avoided_emissions(baseline_kwh: float, optimized_kwh: float) -> Dict[str, float]`
- **Calculation Mechanism**:
  $$\text{Emissions (kg CO}_2\text{)} = \text{Energy (kWh)} \times \text{grid\_emission\_factor}$$
  $$\text{Avoided CO}_2 = (\text{Baseline kWh} - \text{Optimized kWh}) \times \text{grid\_emission\_factor}$$
- **Resolution**: `CarbonCalculator` accepts `EmissionConfig(frozen=True)`. When the sidebar CO2 factor changes, avoided emissions across all pages recalculate instantly while leaving physical kWh and financial costs completely unchanged.

#### F. Hardcoded Tariff Values Identified & Removed
The following hardcoded instances were uncovered and replaced with dynamic references:
1. `src/recommendations/engine.py` (line 21): Default tariff parameter was hardcoded to `tariff_per_kwh: float = 8.50`. Multiple recommendation rules multiplied saved kWh by fixed values like `₹8.50`, `₹11.50`, or `₹5.20`. Refactored to read `self.tariff_config.get_rate_for_period()` and `self.tariff_config.normal_rate_inr`.
2. `src/anomaly/detector.py` (line 25): Default parameter `electricity_cost_per_kwh: float = 8.50`. Refactored so any incident cost estimations use dynamic active rates.
3. `dashboard/app.py` (Page 6 & Page 7): Hardcoded strings citing `"Baseline bill: ₹2,28,000"` and `"Estimated savings: ₹30,240/month"`. Refactored to format strings dynamically using active comparison dictionaries.

#### G. Hardcoded CO2 Values Identified & Removed
1. `src/recommendations/engine.py` (line 22): Default CO2 factor was hardcoded as `co2_factor: float = 0.716`. Refactored to accept and use `EmissionConfig`.
2. `src/emissions/carbon.py`: Refactored to draw default values exclusively from `EmissionConfig(grid_emission_factor_kg_per_kwh=0.716)`.
3. `dashboard/app.py` (Page 1 & Page 6): Refactored to reference `e_cfg.grid_emission_factor_kg_per_kwh` instead of fixed text literals.

#### H. How Caching Was Fixed to Trigger Recalculation
- **Root Cause of Stale Caching**: Earlier code cached data loaders with no arguments (`@st.cache_data def load_data(): ...`), and then read fixed JSON files off the disk. Even if the user modified the inputs, Streamlit returned the cached result or loaded the frozen JSON.
- **Architectural Solution**:
  1. Created a dedicated reactive evaluation function:
     ```python
     @st.cache_data
     def compute_reactive_pipeline(
         off_peak_rate: float,
         normal_rate: float,
         peak_rate: float,
         grid_emission_factor: float
     ):
         ...
     ```
  2. The function arguments `(off_peak_rate, normal_rate, peak_rate, grid_emission_factor)` form the hash key for `@st.cache_data`. Any modification to a slider immediately invalidates the cache key and triggers re-execution.
  3. Precomputed disk JSON reading was bypassed in favor of in-memory execution on `df_base`.
  4. Added a visual **"Active Model Inputs"** status panel in the sidebar showing the active rates, the peak spread $\Delta$, and the exact timestamp of the last recomputation.

#### I. How Duplicated Configuration Was Resolved
- **Problem**: Tariff thresholds, TOD clock hours, and emission constants were scattered across 6 files (`cost_model.py`, `carbon.py`, `optimizer.py`, `recommendations/engine.py`, `anomaly/detector.py`, `dashboard/app.py`).
- **Solution**: Created `src/config.py` defining:
  - `TariffConfig`: Immutable dataclass encapsulating `off_peak_rate_inr`, `normal_rate_inr`, `peak_rate_inr`, TOD hour slots (22–06, 06–18, 18–22), demand charges, and power factor penalty/rebate thresholds.
  - `EmissionConfig`: Immutable dataclass encapsulating `grid_emission_factor_kg_per_kwh` and regulatory metadata (CEA India v19).
  - All analytical modules now import and reference these dataclasses exclusively.

---

### Verification Test Suite Results

Six mandatory end-to-end regression tests were implemented in `tests/test_reactive_config.py` and executed via pytest:

```
tests/test_reactive_config.py::test_test1_baseline_tod_tariff_recording PASSED
tests/test_reactive_config.py::test_test2_flat_tariff_no_tod_differential PASSED
tests/test_reactive_config.py::test_test3_high_peak_tariff_stronger_shift_incentive PASSED
tests/test_reactive_config.py::test_test4_co2_factor_shift_invariance PASSED
tests/test_reactive_config.py::test_test5_tariff_rate_change_invariance PASSED
tests/test_reactive_config.py::test_test6_optimizer_schedule_comparison_flat_vs_tod PASSED
```

#### Test Scenario Summary:

| Test ID | Test Scenario | Inputs Tested | Expected Mathematical Behavior | Observed Outcome | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TEST 1** | Baseline TOD Tariff Verification | Off-Peak=₹5, Normal=₹8, Peak=₹12 | Energy charges strictly match weighted TOD hours ($\sum E_t \times R_t = ₹15,040$). | Exact match ($₹15,040.00$). Baseline metrics recorded. | **PASSED** |
| **TEST 2** | Flat Tariff Test | Off-Peak=₹8, Normal=₹8, Peak=₹8 | Peak-to-offpeak differential $\Delta = ₹0.00$. Tariff load shifting savings must evaluate to exactly $₹0.00$. | Differential is $₹0.00$. Tariff shift cost saved is exactly $₹0.00$. | **PASSED** |
| **TEST 3** | High Peak Tariff Incentive | Off-Peak=₹5, Normal=₹8, Peak=₹20 | Peak energy costs spike. Differential widens to $₹15.00/\text{kWh}$. Shifting savings increase relative to baseline. | Peak cost and shifting financial savings are strictly higher under Peak=₹20 than Peak=₹12. | **PASSED** |
| **TEST 4** | Carbon Factor Invariance | CO2 Factor: $0.716 \rightarrow 0.500\text{ kg/kWh}$ | Scope 2 emissions decrease by $30.17\%$. Physical energy (kWh), production, SEC, and electricity bill (₹) remain strictly identical. | Emissions drop from $1260.16\text{ kg}$ to $880.00\text{ kg}$. Energy, SEC, and Costs match to 9 decimal places. | **PASSED** |
| **TEST 5** | Tariff Rate Change Invariance | Off-Peak: $₹5.00 \rightarrow ₹10.00$ | Monetary costs increase. Physical kWh, production throughput, SEC, and Scope 2 CO2 emissions remain strictly identical. | Cost increases from $₹15,040$ to $₹16,640$. Energy ($1760\text{ kWh}$), SEC, and CO2 remain perfectly invariant. | **PASSED** |
| **TEST 6** | Optimizer Schedule Comparison | Flat ($₹8/₹8/₹8$) vs. Steep ($₹4/₹8/₹16$) | Under flat tariff, furnace load remains unshifted in peak slot. Under steep tariff, furnace load is shifted to off-peak slot. | Furnace slots in flat schedule contain `PEAK`. Furnace slots in steep schedule contain zero `PEAK` (moved to `OFF_PEAK`). | **PASSED** |

---

### Overall System Test Suite Status

The complete automated test suite comprising 28 unit, integration, scenario, API, and reactivity tests was executed:

```
tests/test_api.py::test_api_health PASSED
tests/test_api.py::test_api_topology PASSED
tests/test_api.py::test_api_overview PASSED
tests/test_api.py::test_api_machines PASSED
tests/test_api.py::test_api_recommendations PASSED
tests/test_calculations.py::test_three_phase_power_balanced PASSED
tests/test_calculations.py::test_power_factor_clamping PASSED
tests/test_calculations.py::test_nema_phase_imbalance_normal PASSED
tests/test_calculations.py::test_nema_phase_imbalance_critical PASSED
tests/test_calculations.py::test_feeder_cable_loss_and_resistivity PASSED
tests/test_calculations.py::test_discrete_energy_integral PASSED
tests/test_calculations.py::test_sec_calculation_and_improvement PASSED
tests/test_calculations.py::test_carbon_emissions_cea_factor PASSED
tests/test_calculations.py::test_cost_model_tariff_slots PASSED
tests/test_reactive_config.py::test_test1_baseline_tod_tariff_recording PASSED
tests/test_reactive_config.py::test_test2_flat_tariff_no_tod_differential PASSED
tests/test_reactive_config.py::test_test3_high_peak_tariff_stronger_shift_incentive PASSED
tests/test_reactive_config.py::test_test4_co2_factor_shift_invariance PASSED
tests/test_reactive_config.py::test_test5_tariff_rate_change_invariance PASSED
tests/test_reactive_config.py::test_test6_optimizer_schedule_comparison_flat_vs_tod PASSED
tests/test_scenarios.py::test_scenario_1_normal_operation PASSED
tests/test_scenarios.py::test_scenario_2_motor_energy_increase PASSED
tests/test_scenarios.py::test_scenario_3_production_decrease_sec_increase PASSED
tests/test_scenarios.py::test_scenario_4_machine_on_zero_production_idle PASSED
tests/test_scenarios.py::test_scenario_5_phase_imbalance_alert PASSED
tests/test_scenarios.py::test_scenario_6_low_power_factor_warning PASSED
tests/test_scenarios.py::test_scenario_7_peak_period_load_recommendation PASSED
tests/test_scenarios.py::test_scenario_8_optimized_operation_production_constraint PASSED

======================== 28 passed, 1 warning in 2.65s ========================
```

---

### Conclusion & Operational Readiness

With this architecture:
1. Every page in the Streamlit application reflects the real-time configuration without requiring server restarts or page refreshes.
2. The platform guarantees strict fidelity to physical laws: tariffs govern monetary costs and dispatch economics; thermodynamic/mechanical consumption governs energy, power, and Specific Energy Consumption.
3. The codebase complies with industrial-grade engineering practices for SME energy audits and deployment readiness.
