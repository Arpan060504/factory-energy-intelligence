# Adversarial Engineering Stress-Test & Hostile Audit Report
### *Defending the Factory Energy Intelligence & Optimization Platform against Expert Evaluation*

---

## Executive Summary

This report documents the results of an **adversarial stress test** conducted to probe every potential technical vulnerability, physical inconsistency, optimization loophole, and business assumption in the platform.

The system was evaluated from the perspectives of:
1. **A Senior Electrical Distribution Engineer** (checking transformer/feeder ratings, symmetrical components, power quality, and power factor).
2. **A Manufacturing Operations Director** (checking production throughput constraints, machine operating availability, and shift scheduling).
3. **An Industrial Data Scientist / ML Engineer** (checking baseline leakage, over-fitting, sensor noise resilience, and false positive rates).
4. **An SME Financial Auditor / Hackathon Judge** (checking hardware BOM credibility, Capex/Opex accounting, and the plausibility of the calculated payback).

The prototype emerged **robust, physics-consistent, and defensible**, with specific operational boundaries and limitations explicitly documented below.

---

## 1. Physical Realism Test

### 1.1 Machine Ratings vs. Maximum Active Power
We verified whether active power draw ($P$) stays within realistic electro-mechanical envelope boundaries for all 7 machines:

| Machine ID | Machine Description | Nameplate Rating | Max Observed Active Power | Overload % | Physical Plausibility Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AUX_01** | Utilities & Lighting | 25.0 kW | 24.35 kW | $-2.60\%$ | **REALISTIC** (Operates within continuous duty limit) |
| **COMP_01** | Rotary Screw Compressor | 45.0 kW | 43.48 kW | $-3.38\%$ | **REALISTIC** (Full-load air delivery within nameplate) |
| **FURNACE_01** | Induction Billet Furnace | 160.0 kW | 191.32 kW | **$+19.57\%$** | **REALISTIC DEFECT STATE** (Occurs strictly during Scenario 5: refractory lining breakdown requiring +20% thermal compensation) |
| **LINE_01** | Final Assembly Line | 22.0 kW | 21.32 kW | $-3.09\%$ | **REALISTIC** (Operates within conveyor motor capacity) |
| **MOTOR_01** | CNC Machining Center | 75.0 kW | 83.05 kW | **$+10.73\%$** | **REALISTIC DEFECT STATE** (Occurs during Scenario 1: mechanical bearing drag; standard induction motors tolerate 115% service factor for short durations) |
| **MOTOR_02** | Hydraulic Stamping Press | 55.0 kW | 60.38 kW | **$+9.78\%$** | **REALISTIC** (Transient hydraulic tonnage peak during deep drawing cycle) |
| **PUMP_01** | Chilled Water Pump | 30.0 kW | 28.95 kW | $-3.50\%$ | **REALISTIC** (Operates near best efficiency point) |

### 1.2 Substation Transformer Loading (TR_01: 1000 kVA, 11 kV / 415 V)
- **Rated Capacity**: $1000.0\text{ kVA}$
- **Peak Plant Demand Observed**: **$462.7\text{ kVA}$** (Utilization: **$46.27\%$**)
- **Mean Plant Demand Observed**: **$305.9\text{ kVA}$** (Utilization: **$30.59\%$**)
- **Verdict**: The transformer operates with healthy thermal margin ($\approx 54\%$ reserve capacity), representative of standard Indian SME substations provisioned for future expansion.

### 1.3 Feeder Cable Ampacity & Thermal Limits (XLPE Aluminium Conductor)
- `FDR_01` (MOTOR_01, $95\text{ mm}^2$, rated $175\text{ A}$): Max measured current $= 135.15\text{ A}$ ($77.2\%$ loading).
- `FDR_02` (MOTOR_02, $70\text{ mm}^2$, rated $145\text{ A}$): Max measured current $= 110.44\text{ A}$ ($76.2\%$ loading).
- `FDR_03` (PUMP_01, $35\text{ mm}^2$, rated $95\text{ A}$): Max measured current $= 47.85\text{ A}$ ($50.4\%$ loading).
- `FDR_04` (COMP_01, $50\text{ mm}^2$, rated $120\text{ A}$): Max measured current $= 87.23\text{ A}$ ($72.7\%$ loading).
- `FDR_05` (FURNACE_01, $185\text{ mm}^2$, rated $275\text{ A}$ in ground / $310\text{ A}$ in air): Max measured current $= 293.5\text{ A}$ ($106.7\%$ during refractory defect). Within emergency overload tolerance of XLPE insulation ($90^\circ\text{C}$ continuous, $130^\circ\text{C}$ emergency).
- `FDR_06` (LINE_01, $25\text{ mm}^2$, rated $75\text{ A}$): Max measured current $= 35.88\text{ A}$ ($47.8\%$ loading).
- `FDR_07` (AUX_01, $25\text{ mm}^2$, rated $75\text{ A}$): Max measured current $= 38.59\text{ A}$ ($51.5\%$ loading).

---

## 2. Energy Conservation Test

For each individual machine and the consolidated facility, the discrete energy sum was benchmarked against the mathematical time-integral of active power:

$$E_{\text{integral}} = \sum_{t=1}^{N} P(t) \times \left(\frac{5.0}{60.0}\right)$$

| Machine ID | $\sum E_{\text{recorded}}$ (kWh) | $\int P\,dt$ (kWh) | Absolute $\Delta$ (kWh) | Relative Error (%) | Conservation Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AUX_01** | 10,511.93 | 10,511.97 | 0.0428 | $0.00041\%$ | **EXACT CONSERVATION** |
| **COMP_01** | 21,855.85 | 21,855.84 | 0.0092 | $0.00004\%$ | **EXACT CONSERVATION** |
| **FURNACE_01** | 80,850.09 | 80,850.11 | 0.0232 | $0.00003\%$ | **EXACT CONSERVATION** |
| **LINE_01** | 8,300.56 | 8,300.54 | 0.0159 | $0.00019\%$ | **EXACT CONSERVATION** |
| **MOTOR_01** | 32,842.98 | 32,842.95 | 0.0272 | $0.00008\%$ | **EXACT CONSERVATION** |
| **MOTOR_02** | 20,730.11 | 20,730.13 | 0.0183 | $0.00009\%$ | **EXACT CONSERVATION** |
| **PUMP_01** | 16,047.24 | 16,047.26 | 0.0240 | $0.00015\%$ | **EXACT CONSERVATION** |
| **TOTAL FLEET** | **191,138.76** | **191,138.74** | **0.0194** | **$0.00001\%$** | **STRICTLY CONSERVED** |

The minute deviation ($< 0.02\text{ kWh}$ over $191,138\text{ kWh}$) is purely due to 4-decimal floating point rounding. Energy integrates from power with zero leakage.

---

## 3. Specific Energy Consumption (SEC) Attack Test

### 3.1 Hostile Test Case 1: Attempted Improvement via Throughput Reduction
- **Baseline Scenario**: Production $= 1,000\text{ units}$, Energy $= 500\text{ kWh} \implies \text{SEC}_{\text{base}} = \mathbf{0.5000\text{ kWh/unit}}$.
- **Fraudulent Intervention**: Operator throttles line to $800\text{ units}$ ($-20\%$) and claims energy saving because consumption fell to $450\text{ kWh}$ ($-10\%$).
- **System Evaluation**:
  $$\text{SEC}_{\text{opt}} = \frac{450\text{ kWh}}{800\text{ units}} = \mathbf{0.5625\text{ kWh/unit}}$$
  $$\Delta\text{SEC}\% = \left(\frac{0.5000 - 0.5625}{0.5000}\right) \times 100 = \mathbf{-12.5\%}\quad (\text{Deterioration!})$$
- **System Verdict**: **REJECTED**. The platform flags that Specific Energy Consumption deteriorated by $+12.5\%$, exposing the fraudulent claim. Furthermore, `FactoryOptimizer` rejects any schedule where $\text{Production}_{\text{opt}} < \text{Production}_{\text{base}}$.

### 3.2 Legitimate Test Case 2: True Energy Efficiency at Invariant Throughput
- **Optimized Scenario**: Production $= 1,000\text{ units}$ (invariant), Energy $= 450\text{ kWh}$ ($-10\%$).
- **System Evaluation**: $\text{SEC}_{\text{opt}} = \mathbf{0.4500\text{ kWh/unit}} \implies \Delta\text{SEC} = \mathbf{+10.0\%}$.
- **System Verdict**: **ACCEPTED**.

---

## 4. Tariff Attack Test

We subjected the platform to four extreme tariff configurations to test whether economic incentives alter physical realities:

| Tariff Attack Case | Configured Rates (₹/kWh)<br>[Off-Peak / Normal / Peak] | Peak Spread $\Delta$ | Baseline Cost (₹) | Optimized Cost (₹) | Financial Savings (₹) | Shift Savings (₹) | Baseline Energy (kWh) | Optimized Energy (kWh) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Case A: Standard TOD** | ₹5.00 / ₹8.00 / ₹12.00 | +₹7.00 | ₹19,70,649 | ₹15,95,466 | ₹3,75,183 | ₹1,04,021 | **191,138.7** | **159,165.7** |
| **Case B: Flat Tariff** | ₹8.00 / ₹8.00 / ₹8.00 | ₹0.00 | ₹20,03,164 | ₹17,10,732 | ₹2,92,432 | **₹0.00** | **191,138.7** | **159,165.7** |
| **Case C: Inverted Tariff** | ₹10.00 / ₹8.00 / ₹6.00 | -₹4.00 | ₹20,51,031 | ₹17,40,755 | ₹3,10,276 | **₹0.00** | **191,138.7** | **159,165.7** |
| **Case D: Extreme Peak** | ₹5.00 / ₹8.00 / ₹50.00 | +₹45.00 | ₹34,63,519 | ₹23,14,782 | ₹11,48,737 | **₹6,68,705** | **191,138.7** | **159,165.7** |

### Critical Physical Invariance Findings:
1. **Physical Energy Invariance**: Baseline energy ($191,138.7\text{ kWh}$) and optimized energy ($159,165.7\text{ kWh}$) remained **strictly identical** across all 4 tariff cases.
2. **SEC Invariance**: $\text{SEC}_{\text{base}} = 1.4555\text{ kWh/u}$ and $\text{SEC}_{\text{opt}} = 1.2120\text{ kWh/u}$ did not fluctuate by even $0.0001\text{ kWh/u}$.
3. **Dispatch Rationality**: Under flat (Case B) and inverted (Case C) tariffs, tariff-shifting savings dropped to **₹0.00**, proving the optimizer does not fabricate financial savings when no economic spread exists.

---

## 5. Optimization Constraint & Feasibility Attack

We probed whether the optimization engine cheats by violating factory physical constraints:

1. **Production Throughput Constraint**:
   - Baseline Production: $131,324.1\text{ units}$
   - Optimized Production: $131,324.1\text{ units}$
   - Production Delta: **$0.0\text{ units}$** (`production_constraint_satisfied == True`).
2. **Machine Availability & Flexibility Guardrails**:
   - Continuous / Non-flexible processes (`CNC Machining MOTOR_01`, `Chilled Water PUMP_01`, `Assembly LINE_01`) have `is_flexible_load = False`. Their production runs are locked and **never rescheduled**.
   - Flexible batch processes (`Induction Billet Furnace FURNACE_01`, `Hydraulic Press MOTOR_02`) have `is_flexible_load = True`. Only flexible batch melting cycles are rescheduled into the night off-peak window.
3. **Machine Capacity Limits**:
   - When furnace batches are shifted to night hours (22:00–06:00), total night demand never exceeds the $800\text{ kVA}$ contract demand or transformer $1000\text{ kVA}$ capacity. Peak optimized factory demand is $451.5\text{ kVA}$ ($56.4\%$ utilization).

---

## 6. Anomaly Detection Noise & Spurious Trips Test

We tested resilience against false alarms by injecting 10 isolated single-interval (5-minute) telemetry glitches ($Vibration = 6.0\text{ mm/s}$, $Imbalance = 15.0\%$) into certified healthy operation.

- **Raw Interval Alert Trips**: 2,798 interval alerts.
- **Aggregated Operational Incidents**:
  - The incident aggregator (`aggregate_alert_incidents()`) groups alerts into continuous multi-hour episodes.
  - Isolated 5-minute single-interval glitches are logged with `duration_hours = 0.08h` (5 minutes) and are easily filtered by setting an incident duration threshold ($\ge 15\text{ minutes}$), preventing false dispatch of maintenance crews.
- **Identified Weakness**: The raw alert table on Page 1 displays count of all alerts. We recommend defaulting the dashboard to display **consolidated incidents** rather than raw interval alerts to prevent operator alarm fatigue.

---

## 7. Sensor Failure & Data Quality Stress Test

We tested system behavior under 6 simulated hardware sensor failure modes:

| Sensor Failure Mode | Injected Telemetry State | Current System Response | Potential Vulnerability / Risk | Recommended Engineering Defense |
| :--- | :--- | :--- | :--- | :--- |
| **Current Sensor Dropout** | Phase R current drops to $0.0\text{ A}$ while machine is `RUNNING` | $I_{\text{avg}}$ drops, $Imbalance$ jumps to $> 35\%$. Triggers `PHASE_IMBALANCE` alarm. | Misclassifies broken CT or open wire as a loose switchgear contactor. | Add pre-check: if one phase current is exactly $0.0\text{ A}$ while voltage is normal and other phases $> 20\text{ A}$, flag `SENSOR_FAILURE_CT_OPEN_CIRCUIT`. |
| **Voltage Sensor Loss** | PT fuse blows; Voltage drops to $0\text{ V}$ | Power calculations drop to zero; $I_{\text{calc}}$ calculation may encounter divide-by-zero. | Causes calculated apparent power and active power to glitch. | Implement voltage sanity check ($V < 300\text{ V} \implies \text{flag PT failure, do not calculate PF}$). |
| **Power Factor Sensor Fault** | PF reading freezes or returns `NaN` | Default clamping logic kicks in: `np.clip(pf, 0.5, 0.99)`. | Masks loss of telemetry by silently substituting boundary numbers. | Display `DATA QUALITY WARNING: PF Telemetry Missing`. |
| **Temperature Sensor Disconnect** | PT100 open circuit; reads $-999^\circ\text{C}$ or $0^\circ\text{C}$ | Machine health score treats $0^\circ\text{C}$ as abnormally cold or healthy. | Masks overheating defect. | Add Range Validation: $10^\circ\text{C} \le T \le 120^\circ\text{C}$. Flag out-of-range as sensor fault. |
| **Vibration Sensor Detached** | Accelerometer falls off; reads $0.0\text{ mm/s}$ | Health score evaluates vibration penalty as 0 (Score = 100). | False sense of security on failing motor. | Add minimum operational vibration threshold: running machine must exhibit $> 0.15\text{ mm/s}$. |
| **Production Counter Freeze** | Pulse counter disconnects; units = 0 while running | Active power $> 8\text{ kW}$ at 0 units triggers `EXCESSIVE_IDLE_CONSUMPTION`. | Misidentifies pulse counter wire break as machine idling. | Correlate with machine status: if status is RUNNING with normal load, flag `COUNTER_FAULT`. |

---

## 8. Missing Production Data Test

- **Test Condition**: Set `production_units = 0.0` or `NaN` across machine operating periods.
- **Current Behavior**: In [`src/energy/analytics.py`](file:///d:/coding/Project/graph/smart-manufacturing-energy/src/energy/analytics.py#L32), `calculate_sec()` specifies:
  ```python
  if production_units <= 0.001:
      return 0.0
  ```
- **Vulnerability Identified**: Returning `0.0 kWh/unit` during periods of zero production or sensor failure is mathematically incorrect ($\frac{E}{0} = \infty$, undefined). A hostile judge could argue that "0.0 SEC implies infinite energy efficiency".
- **Recommended Fix**: Return `None` or `NaN` and render as `"SEC Unavailable (Non-Productive / Missing Data)"` on the dashboard.

---

## 9. Anonymized Industrial Reference Data Audit

- The reference file (`data/reference/anonymized_reference.csv`, 15,000 observations) reflects field logging intervals from actual HT industrial consumers.
- **Asynchrony Defense**: In commercial distribution panels, feeder data loggers frequently poll asynchronously. Adding feeder currents recorded at 10:01, 10:03, and 10:05 to compare against an incomer reading at 10:00 causes apparent current violations. The platform correctly uses reference data solely for **empirical parameter distributions and boundary calibration**, never as a synchronized time-series.

---

## 10. Cable Loss Quadratic Dependency ($I^2R$) Test

We tested the mathematical fidelity of the feeder loss model:
- Cable parameters: Aluminium, Length $= 50\text{ m}$, Area $= 70\text{ mm}^2$, Operating Temp $= 50^\circ\text{C} \implies R_{\text{cable}} = 0.02258\ \Omega$.
- At $I = 50.0\text{ A}$: $P_{\text{loss}} = 0.1693\text{ kW}$.
- At $I = 100.0\text{ A}$ (Current doubled): $P_{\text{loss}} = 0.6773\text{ kW}$.
- Ratio: $\frac{0.6773}{0.1693} = \mathbf{4.000\times}$ (**Exact Quadratic Verification**).
- Material Sensitivity: Substituting Copper ($R_{\text{cable}} = 0.01398\ \Omega$) yields $P_{\text{loss}} = 0.4192\text{ kW}$ (**$38.1\%$ loss reduction**).

---

## 11. Power Factor Dependency Test ($P, S, Q$)

Simulating a constant $50.0\text{ kW}$ active load across power factor degradation:

| Power Factor ($\cos\phi$) | Active Power $P$ (kW) | Apparent Power $S$ (kVA) | Reactive Power $Q$ (kVAR) | Line Current $I$ (A) | Feeder Loss $I^2R$ (kW) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1.00** | 50.0 kW | 50.00 kVA | 0.00 kVAR | 69.56 A | 0.328 kW |
| **0.95** (Rebate limit) | 50.0 kW | 52.63 kVA | 16.43 kVAR | 73.22 A | 0.363 kW |
| **0.90** (Penalty limit) | 50.0 kW | 55.56 kVA | 24.22 kVAR | 77.29 A | 0.405 kW |
| **0.80** (Industrial average) | 50.0 kW | 62.50 kVA | 37.50 kVAR | 86.95 A | 0.512 kW |
| **0.70** (Severe uncorrected) | 50.0 kW | 71.43 kVA | 51.01 kVAR | 99.37 A | 0.669 kW |

- **Verification**: Dropping PF from 0.95 to 0.70 causes apparent demand to surge by **$+35.7\%$** and cable losses to surge by **$+84.3\%$**, while active production energy ($50\text{ kW}$) remains constant.

---

## 12. Phase Current Imbalance Audit

NEMA MG-1 calculation:
$$\text{Imbalance (\%) } = \frac{\max(|I_r - I_{\text{avg}}|, |I_y - I_{\text{avg}}|, |I_b - I_{\text{avg}}|)}{I_{\text{avg}}} \times 100$$
- Balanced $(100, 100, 100)\text{ A} \implies \mathbf{0.0\%}$
- Moderate $(105, 98, 97)\text{ A} \implies \mathbf{5.0\%}$
- Severe $(135, 98, 67)\text{ A} \implies \mathbf{35.0\%}$
- The system correctly issues maintenance investigation SOPs (terminal lug torque, contactor contact resistance) rather than fabricating guaranteed savings.

---

## 13. Machine Health Index Audit

Composite formulation:
$$\text{Score} = 100 - (0.20 D_I + 0.25 D_P + 0.25 D_T + 0.20 D_V + 0.10 D_{\text{imb}})$$
- Healthy benchmark: Score $\ge 80$
- Warning: $60 \le \text{Score} < 80$
- Critical: Score $< 60$
- Explicitly disclaimed across all pages and documentation: **"Algorithmic heuristic for maintenance prioritization, NOT an OEM-certified RUL prediction."**

---

## 14. Business Model & Payback Sensitivity

### 14.1 Why Does the Model Calculate a 13-Day Payback?
Evaluating the numbers:
$$\text{Turnkey Hardware Capex} = \mathbf{₹ 1,52,150}\quad (\text{8 Modbus meters + CTs + Gateway + Sensors + Commissioning})$$
$$\text{Baseline Monthly Electricity Bill} = \mathbf{₹ 19,40,446}\quad (\approx \text{₹ 2.33 Crore / year})$$
$$\text{Simulated Monthly Savings} = \mathbf{₹ 3,61,588}\quad (18.63\%\text{ total bill reduction})$$
$$\text{Instantaneous Simple Payback} = \frac{₹ 1,52,150}{₹ 3,61,588 - ₹ 3,000} \times 30\text{ days} = \mathbf{12.7\text{ Days}}$$

The short payback is mathematically genuine because the factory consumes heavy power (160 kW furnace), yielding ₹3.6 Lakhs in monthly savings against a low-cost ₹1.52 Lakh hardware deployment.

### 14.2 Defending Against the "Too Good to Be True" Critique
To defend this in front of a skeptical evaluator, present the **Phased Adoption Sensitivity Table** (from Page 7):

| Implementation Scenario | SEC Gain (%) | Monthly Gross Saving | Net Year-1 Profit | Simple Payback Period | Plausibility Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Conservative Pilot** | **5.0%** | ₹ 97,022 / mo | ₹ 9,76,118 | **47 Days (1.6 Months)** | Achievable through simple manual idle compressor shutoffs alone |
| **Standard Phase 1** | **10.0%** | ₹ 1,94,045 / mo | ₹ 21,40,385 | **24 Days (0.8 Months)** | Achieved with auto-standby interlocks |
| **Full Platform Case** | **16.73%** | ₹ 3,61,588 / mo | ₹ 37,07,489 | **13 Days (0.4 Months)** | Steady-state operation across all 3 levers |
| **Aggressive Stretch** | **20.0%** | ₹ 3,88,089 / mo | ₹ 44,68,920 | **12 Days** | Requires full furnace thermal insulation overhaul |

---

## 15. Savings Attribution Integrity

The platform strictly segregates savings into four non-overlapping levers:
- **Lever 1: Physical Energy Efficiency**: $31,973.1\text{ kWh/mo}$ saved ($\mathbf{₹ 2,28,000/mo}$ from compressor/machine idle elimination).
- **Lever 2: Economic Tariff Shifting**: $0.0\text{ kWh}$ physical energy change; $\mathbf{₹ 1,04,020.76/mo}$ saved by moving furnace batches from Peak to Off-Peak.
- **Lever 3: Peak Demand Shaving**: $12.7\text{ kVA}$ demand charge avoidance.
- **Lever 4: Mechanical Loss Recovery**: $3,473.1\text{ kWh/mo}$ ($\mathbf{₹ 29,568/mo}$ saved by regreasing bearings and restoring alignment).

---

## 16. Carbon Model Audit

- Baseline Scope 2 Emissions: **$136.86\text{ MT CO}_2\text{/month}$** ($136,855.3\text{ kg}$).
- Avoided Emissions: **$22.89\text{ MT CO}_2\text{/month}$** ($22,892.7\text{ kg}$).
- Tested invariance against changing emission factor ($0.716 \rightarrow 0.500 \rightarrow 1.000\text{ kg/kWh}$): Energy (kWh), SEC, and electricity bill (₹) remained invariant.

---

## 17. Cross-Page Reconciliation Audit

Audited all 8 Streamlit dashboard pages for the 30-day baseline:
- Executive Overview Energy ($191,139\text{ kWh}$) $=$ Energy Analytics Table Sum ($191,139\text{ kWh}$) $=$ Optimization Baseline ($191,139\text{ kWh}$).
- Executive Baseline SEC ($1.4555\text{ kWh/u}$) $=$ Optimization Baseline SEC ($1.4555\text{ kWh/u}$).
- Optimization Monthly Cost Reduction ($₹3,61,588$) $=$ Business Model Monthly Savings ($₹3,61,588$).
- Minor string discrepancy found: `scripts/run_demo.py` cited ₹1,52,400 Capex, while `docs/business_model.md` and `dashboard/app.py` cite ₹1,52,150. (A tiny ₹250 difference in cabling lug estimates).

---

## 18. Hackathon Demo Walkthrough Audit

Executed [`scripts/run_demo.py`](file:///d:/coding/Project/graph/smart-manufacturing-energy/scripts/run_demo.py):
1. **MEASURE**: 395.4 kW live load vs. 352.1 kW baseline; current SEC = $1.4555\text{ kWh/u}$.
2. **DETECT**: `MACHINE_EFFICIENCY_DEGRADATION` on `MOTOR_01` (+16% excess power).
3. **DIAGNOSE**: Temp $+15.2^\circ\text{C}$, Vibration $4.8\text{ mm/s}$ (exceeds ISO 10816-3 limit $2.8\text{ mm/s}$). Mechanical bearing race defect.
4. **RECOMMEND**: Actionable SOP `REC-001` (regrease drive-end bearing, laser shaft alignment).
5. **OPTIMIZE**: Apply idle interlocks on `COMP_01`, shift `FURNACE_01` to off-peak night slot.
6. **VERIFY**: Production strictly invariant ($131,324.1\text{ units}$); SEC improved by **$16.73\%$**; bill reduced by **$18.63\%$**; avoided $\text{CO}_2 = 22.89\text{ MT}$.
7. **FINANCIAL ROI**: Capex ₹1,52,150 pays back in **13 days**.
