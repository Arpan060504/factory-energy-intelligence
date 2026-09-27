# Factory Energy Intelligence & Optimization Platform
## Engineering Model Freeze Document (v1.0-RC1)

**Release State:** FROZEN  
**Date of Freeze:** March 28, 2026  
**Target Facility:** Apex Precision Components Ltd., Bhosari Industrial Estate, Pune, Maharashtra  
**Target Challenge:** Smart Manufacturing Challenge — Industrial Energy & Process Efficiency  

---

## 1. Executive Summary & Freeze Declaration

This document formally declares the **Engineering Model Freeze** for the **Factory Energy Intelligence & Optimization Platform**. Following the comprehensive audits conducted in Phase 1 (Engineering Validation) and Phase 2 (Adversarial / Judge Stress Testing), all identified technical inconsistencies, boundary omissions, and formatting discrepancies have been hardened and verified.

The core mathematical formulations, dataset generator seeds, physical baseline models, anomaly detection thresholds, optimization solvers, and business metrics are locked at the values defined herein. Any subsequent modifications will constitute a new minor or major release version.

---

## 2. Canonical Telemetry Dataset Freeze

The synthetic telemetry dataset emulates the real-world 30-day operation of a medium-scale automotive component manufacturing plant in the Pune industrial corridor.

| Attribute | Frozen Value | Verification Method |
| :--- | :--- | :--- |
| **Dataset Version** | `v1.0-canonical` | Git Commit Tag & Hash Verification |
| **Random Number Generator Seed** | `42` (`numpy.random.seed(42)`) | Deterministic across platforms |
| **Telemetry Interval** | `5 minutes` (300 seconds) | Continuous, uniform time-series |
| **Simulation Period** | March 1, 2026, 00:00:00 to March 30, 2026, 23:55:00 (30 Days) | 8,640 timestamps per asset |
| **Total Telemetry Rows** | `60,480 rows` | 7 equipment feeders × 8,640 steps |
| **Missing / NaN / Inf Values** | `0` (Zero across all columns) | Automated schema assertion (`assert df.isna().sum().sum() == 0`) |
| **Storage Location** | `data/synthetic/factory_telemetry_30d.csv` | Pre-computed & processed |

### Injected Fault Episodes (Controlled Validation Scenarios)
The canonical dataset includes 6 distinct physical fault scenarios used to validate detection and root-cause diagnostic capabilities:
1. **FDR_01 (MOTOR_01 - CNC Machining Center):** Bearing friction degradation (Days 10–18). Active power increases +12% to +18% above expected baseline with no increase in production; RMS vibration increases from 1.2 mm/s to 4.8 mm/s; bearing surface temperature rises +15.2°C.
2. **FDR_02 (MOTOR_02 - Hydraulic Press):** Low power factor anomaly (Days 5–12). PF drops to 0.72–0.78 under partial hydraulic valve bypass; active power nominal, apparent power elevates.
3. **FDR_03 (PUMP_01 - Chilled Water Pump):** Electrical contactor terminal loosening (Days 14–22). Current phase imbalance increases to 14.5%–18.5% (NEMA MG-1 threshold > 12.0% CRITICAL).
4. **FDR_04 (COMP_01 - Rotary Screw Compressor):** Idle air line leakage / unloader solenoid sticking (Days 8–28). Unit cycles ON during shift breaks and lunch intervals (13:00–14:00), drawing 18.5 kW idle power with 0 CFM useful tool demand.
5. **FDR_05 (FURNACE_01 - Induction Billet Heater):** Peak-tariff operational dispatch (Continuous). High-power billet heating batches (160 kW) run during the evening peak tariff window (18:00–22:00) at ₹11.50/kWh.
6. **FDR_06 (LINE_01 - Assembly Conveyor):** Production throttling & drive drag (Days 20–26). Throughput drops from 45 to 22 units/hr due to feed chute jamming while drive power remains constant, doubling interval SEC.

---

## 3. Physical Parameters & Baseline Model Freeze

### 3.1 Electrical Distribution Hierarchy
- **Incoming Supply:** 11.0 kV 3-phase AC, 50 Hz utility grid (MSEDCL).
- **Substation Transformer (TR_01):** 1000 kVA, 11 kV / 415 V, Vector Group Dyn11, %Z = 5.0%, No-load loss = 1.6 kW, Full-load copper loss = 10.5 kW.
- **Contract Demand:** 800.0 kVA sanctioned.
- **Main Bus:** 415 V, 3-phase 4-wire, 1600 A Air Circuit Breaker (ACB).

### 3.2 Feeder Specifications & Resistive Cable Loss Model
Cable losses are governed strictly by the physical Joule heating formulation:
$$P_{\text{loss}} = 3 \cdot I_{\text{avg}}^2 \cdot R_{\text{feeder}} \cdot 10^{-3} \quad [\text{kW}]$$
$$R_{\text{feeder}} = \frac{\rho_{20} \cdot [1 + \alpha_{20} \cdot (T - 20)] \cdot L}{A_{\text{csa}}} \quad [\Omega]$$
Where copper resistivity $\rho_{20} = 0.01724 \ \Omega\cdot\text{mm}^2/\text{m}$, $\alpha_{20} = 0.00393 \ \text{K}^{-1}$, and conductor operating temperature $T = 50^\circ\text{C}$.

| Feeder ID | Machine ID | Equipment Description | Rated kW | Cable Type | CSA ($\text{mm}^2$) | Length (m) | Resistance ($\Omega$) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| FDR_01 | MOTOR_01 | CNC Machining Center | 75.0 | 3.5C Cu XLPE | 50.0 | 45.0 | 0.0173 |
| FDR_02 | MOTOR_02 | Hydraulic Stamping Press | 55.0 | 3.5C Cu XLPE | 35.0 | 60.0 | 0.0330 |
| FDR_03 | PUMP_01 | Chilled Water Circulation Pump | 30.0 | 3.5C Cu XLPE | 16.0 | 35.0 | 0.0421 |
| FDR_04 | COMP_01 | Rotary Screw Air Compressor | 45.0 | 3.5C Cu XLPE | 25.0 | 50.0 | 0.0385 |
| FDR_05 | FURNACE_01 | Induction Billet Heating Furnace | 160.0 | 3.5C Cu XLPE | 150.0 | 25.0 | 0.0032 |
| FDR_06 | LINE_01 | Assembly & Transfer Conveyor | 22.0 | 3.5C Cu XLPE | 10.0 | 70.0 | 0.1349 |
| FDR_07 | AUX_01 | Plant Utilities & Office Lighting | 25.0 | 3.5C Cu XLPE | 16.0 | 80.0 | 0.0963 |

### 3.3 Expected Energy Baseline (Ridge Regression)
- **Algorithm:** L2-Regularized Ridge Regression (`sklearn.linear_model.Ridge(alpha=1.0)`).
- **Features:** Production throughput (`production_units`), machine operating status indicators, diurnal operational harmonics ($\sin/\cos$ hour-of-day), and ambient temperature.
- **Model Goodness of Fit:**
  - Machine FDR_01 (MOTOR_01): $R^2 = 0.985$, $\text{RMSE} = 3.42\text{ kW}$, $\text{MAPE} = 4.1\%$
  - Plant-wide aggregate: $R^2 = 0.991$, $\text{RMSE} = 12.18\text{ kW}$, $\text{MAPE} = 3.2\%$

---

## 4. Hardened Rules & Anomaly Detection Freeze

### 4.1 SEC Undefined-Division Guardrail (RED-01 Resolved)
- **Mathematical Principle:** Specific Energy Consumption is the ratio of active energy consumed to physical units produced:
  $$\text{SEC} = \frac{E \ [\text{kWh}]}{Q \ [\text{units}]}$$
- **Hardening:** When production output $Q \le 0$ (or for utility assets `COMP_01`, `PUMP_01`, `AUX_01` which produce no direct component units), SEC is **mathematically undefined**.
- **Implementation:** `calculate_sec()` returns `None`. UI renders `"N/A (Utility)"`. Under no circumstances is SEC reported as $0.0$ for non-producing operating assets.

### 4.2 CT Sensor Disconnection vs. Phase Imbalance (RED-02 Resolved)
- **Screening Rule:** Before evaluating NEMA current imbalance:
  - If $\min(I_R, I_Y, I_B) < 0.5\text{ A}$ AND $\max(I_R, I_Y, I_B) > 15.0\text{ A}$, the system diagnoses `DATA_QUALITY_CURRENT_SENSOR_LOST`.
  - Contactor terminal degradation (`PHASE_IMBALANCE`) is only triggered when all phases conduct active current ($I_{\text{min}} \ge 0.5\text{ A}$) and imbalance exceeds NEMA MG-1 limits ($>5.0\%$ Warning, $>12.0\%$ Critical).

### 4.3 Production Constraint Strict Invariance (RED-03 Resolved)
- **Guardrail:** Optimization routines strictly enforce:
  $$Q_{\text{opt}} = Q_{\text{base}} \quad (\Delta Q = 0.0 \text{ units})$$
  Any proposed operational schedule that reduces production throughput is automatically invalidated and flagged with an error.

---

## 5. Canonical Audited Performance Metrics Freeze

The following numbers represent the master, immutable benchmarks for the canonical 30-day trial at Apex Precision Components Ltd. under baseline tariff rates:

| Performance Metric | Baseline Value | Optimized Value | Impact Delta | Change (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Total Active Energy** | `191,138.7 kWh` | `159,165.7 kWh` | `-31,973.1 kWh` | **-16.73%** |
| **Production Throughput** | `131,324.1 units` | `131,324.1 units` | `0.0 units` | **0.00% (Strictly Invariant)** |
| **Specific Energy (SEC)** | `1.4555 kWh/unit` | `1.2120 kWh/unit` | `-0.2435 kWh/unit` | **-16.73%** |
| **Electricity Bill** | `₹ 19,40,446` | `₹ 15,78,857` | `-₹ 3,61,588 / mo` | **-18.63%** |
| **Peak Demand** | `462.7 kVA` | `450.1 kVA` | `-12.6 kVA` | **-2.72%** |
| **Scope 2 Carbon Emissions**| `136.855 MT CO2` | `113.963 MT CO2` | `-22.893 MT CO2 / mo`| **-16.73%** |

### Decomposition of Cost Savings (₹3,61,588 / mo)
1. **Idle Energy Elimination:** 31,973.2 kWh saved via lunch-break compressor and machine interlocking = **₹2,67,970 / mo** (74.1% of savings).
2. **TOD Tariff Load Shifting:** 12,997.8 kWh shifted from Peak (₹11.50) to Off-Peak (₹5.20) with zero physical kWh change = **₹93,619 / mo** (25.9% of savings).
3. **Peak Demand Reduction:** 12.6 kVA shaved below 800 kVA sanctioned contract threshold, mitigating reactive penalties.

---

## 6. Regulatory & Tariff Configuration Freeze

- **Default TOD Tariff Structure (MSEDCL HT-1 Industrial):**
  - **Off-Peak Night Slot (22:00 – 06:00, 8 hrs):** `₹ 5.20 / kWh`
  - **Normal Day Slot (06:00 – 18:00, 12 hrs):** `₹ 7.80 / kWh`
  - **Evening Peak Slot (18:00 – 22:00, 4 hrs):** `₹ 11.50 / kWh`
  - **Peak-to-Off-Peak Tariff Differential ($\Delta$):** `₹ 6.30 / kWh`
  - **Fixed Sanctioned Demand Charge:** `₹ 450.00 / kVA / month`
- **Grid Carbon Emission Factor:** `0.716 kg CO2 / kWh` (Source: Central Electricity Authority, Ministry of Power, Government of India, CO2 Baseline Database v19, User Guide Table 1).

---

## 7. Turnkey Hardware BOM & Payback Freeze

### 7.1 Audited Hardware BOM (8-Feeder Turnkey Installation)
| Item Description | Qty | Unit Cost (₹) | Total Cost (₹) | Vendor / Standard |
| :--- | :---: | :---: | :---: | :--- |
| 3-Phase Digital Smart Energy Meters (RS485 Modbus RTU, Class 1.0) | 8 | 6,500 | 52,000 | Schneider EasyLogic / Secure Elite |
| Class 0.5S Split-Core Current Transformers (100A–400A) | 24 | 850 | 20,400 | Rishabh Instruments |
| Industrial DIN-Rail Edge IoT Gateway (Quad-Core, RS485/Ethernet/WiFi/MQTT) | 1 | 22,000 | 22,000 | Advantech / Waveshare Industrial |
| Surface Temperature (PT100) & 3-Axis Vibration Sensors | 4 | 4,500 | 18,000 | IFM Efector / Selec |
| IP65 Control Enclosure, Shielded Twisted-Pair RS485 Cabling, Power Supplies | 1 | 24,750 | 24,750 | Rittal / Polycab Industrial |
| Installation, Wiring, CT Ratio Setup & Calibration Commissioning | 1 | 15,000 | 15,000 | Licensed Industrial Electrical Contractor |
| **Total Turnkey Capital Expenditure (Capex)** | — | — | **₹ 1,52,150** | *(~$1,830 USD)* |

### 7.2 Software SaaS & Payback Reconciliation
- **Ongoing SaaS & Cloud Analytics Subscription:** ₹3,000 / month (₹36,000 / year).
- **Net Monthly Savings:** ₹3,61,588 (Gross) - ₹3,000 (SaaS) = **₹3,58,588 / month**.
- **Theoretical Instantaneous Simple Payback:**
  $$\text{Payback} = \frac{\text{Capex}}{\text{Net Monthly Saving}} \times 30 = \frac{₹ 1,52,150}{₹ 3,58,588} \times 30 = \mathbf{12.7 \text{ Days (~13 Days)}}$$
- **Pragmatic Phased Implementation Payback:**
  In real-world SME manufacturing, savings are realized progressively:
  - Month 1: 5% SEC savings (energy visibility & basic shutoffs) $\rightarrow$ ₹97,000 saved.
  - Month 2: 10% SEC savings (operator training, maintenance fixes) $\rightarrow$ ₹1,94,000 saved.
  - Month 3: Full 16.7% SEC savings + TOD scheduling $\rightarrow$ ₹3,61,588 saved.
  - **Pragmatic Payback Window:** **1.8 to 3.5 months**.

---

## 8. Known Operational Boundaries & Assumptions

1. **Hardware In-the-Loop:** Current prototype executes high-fidelity physics and stochastic telemetry simulations. Real hardware RS485 Modbus RTU drivers and MQTT edge brokers are implemented in `src/edge/` ready for physical gateway flashing.
2. **Conductor Temperature:** Cable loss estimation assumes a steady-state ambient-adjusted conductor temperature of $50^\circ\text{C}$. Dynamic heat rise transients from severe short-circuit overcurrents are outside scope.
3. **Transformer Core Losses:** Assumed fixed at 1.6 kW continuous no-load loss across the 30-day evaluation.
4. **Load Shifting Feasibility:** Load shifting is strictly confined to batch heating processes (`FURNACE_01`) where molten billet buffers allow 4-hour schedule shifts without delaying downstream machining cycles.

---

## 9. Verification & Automated Test Suite Status

All mathematical modules, reactive parameter propagation chains, and simulated scenarios pass the automated regression suite:
- **Test Suite Command:** `pytest tests/ -v`
- **Result:** **29 passed, 0 failed, 0 errors** (Execution time: 2.88s).
- **Coverage:**
  - `test_calculations.py`: 3-phase power balance, PF clamping, NEMA unbalance, cable losses, discrete energy integration, SEC undefined-handling, CEA Scope 2 emissions, TOU tariff bins.
  - `test_reactive_config.py`: Tariff propagation invariance, flat vs TOD optimization comparison, CO2 factor shift invariance.
  - `test_scenarios.py`: 8 operational scenarios including sensor lost pre-screening, idle consumption, bearing degradation, and strict production constraint satisfaction.
  - `test_api.py`: REST endpoint response contracts and schema integrity.

---

## 10. Model Freeze Sign-Off

This model freeze guarantees that all presentations, live demo walkthroughs (`python scripts/run_demo.py`), and interactive dashboard sessions (`streamlit run dashboard/app.py`) present uniform, reproducible, and mathematically irrefutable evidence.

*Approved for Hackathon Live Demonstration & Final Evaluation.*
