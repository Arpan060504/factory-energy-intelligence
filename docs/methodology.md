# Engineering Methodology & Analytical Foundations

This document provides a comprehensive technical breakdown of the analytical algorithms, physics models, diagnostic logic, and optimization formulations implemented in the **Factory Energy Intelligence & Optimization Platform**.

---

## 1. The 7-Step Engineering Intelligence Chain

Generic commercial energy dashboards stop at showing raw kW or kWh graphs ("IoT + Cloud"). In contrast, this platform operates on an end-to-end industrial intelligence workflow:

$$\text{MEASURE} \longrightarrow \text{UNDERSTAND} \longrightarrow \text{DETECT} \longrightarrow \text{DIAGNOSE} \longrightarrow \text{RECOMMEND} \longrightarrow \text{OPTIMIZE} \longrightarrow \text{VERIFY SAVINGS}$$

### Step 1: MEASURE (Industrial Sub-metering & Telemetry)
- Digital Multifunction Meters (MFMs) with Class 0.5S split-core Current Transformers (CTs) measure phase line currents ($I_r, I_y, I_b$), line voltages ($V_r, V_y, V_b$), power factor ($\cos\theta$), active power ($P$), reactive power ($Q$), and active energy ($E$) at 5-minute synchronized intervals.
- PT100 surface RTDs and tri-axial piezoelectric accelerometers monitor equipment casing temperature and vibration velocity RMS.

### Step 2: UNDERSTAND (Physics Engine & Specific Energy Consumption)
- Calculates true apparent power $S = \sqrt{3} V_L I_L / 1000$ and reactive power $Q = \sqrt{S^2 - P^2}$.
- Computes **Specific Energy Consumption (SEC)**:
  $$\text{SEC} = \frac{\sum E_i\ (\text{kWh})}{\text{Total Good Production}\ (\text{Units})}$$
- Establishes the plant-wide and feeder-level energy balance.

### Step 3: DETECT (Rule-Based & Statistical Screening)
- Evaluates real-time observations against three physical screening layers:
  1. *Hard Physical Bounds*: Instantaneous NEMA current unbalance $> 5\%$, power factor $< 0.85$.
  2. *Baseline Deviations*: Deviation $\Delta P = P_{\text{actual}} - P_{\text{expected}}$ exceeding $12\%$ during active production.
  3. *Vibration/Thermal Limits*: Vibration RMS $> 2.8\text{ mm/s}$ (ISO 10816-3 Class II medium machines), casing temperature $> 55^\circ\text{C}$.

### Step 4: DIAGNOSE (Root Cause Inference)
- Disentangles whether high power draw is caused by higher production demand or parasitic electromechanical failure.
- If $P$ is high but production output is normal, and temperature/vibration are elevated, the system flags **Mechanical Efficiency Degradation** (e.g. bearing race wear, drive belt slippage).
- If $P > 8\text{ kW}$ but production is zero and the machine is in idle or non-working hours, the system flags **Excessive Idle / Unloaded Compressor Consumption**.

### Step 5: RECOMMEND (Contextual Operator SOPs)
- Translates raw anomalies into plain-language Standard Operating Procedures (SOPs) for the shop-floor maintenance technician.
- Explicitly answers: WHAT happened? WHY does it matter? WHAT exact action should the operator take? WHAT are the quantified financial (₹), energy (kWh), and carbon (kg $\text{CO}_2$) savings?

### Step 6: OPTIMIZE (Three-Tier Algorithmic Dispatch)
- Implements:
  1. **Idle Energy Elimination**: Automated standby cutoff interlocks.
  2. **TOD Tariff Load Shifting**: Moves flexible batch thermal/pumping loads out of peak tariff hours into off-peak night hours.
  3. **Peak Demand Shaving**: Flattens coincident plant kVA peaks to prevent DISCOM maximum demand penalties.

### Step 7: VERIFY SAVINGS (Audited Before vs. After Experiment)
- Validates the optimization experiment under a **strict production invariance constraint**:
  $$\text{Production}_{\text{optimized}} \ge \text{Production}_{\text{baseline}}$$
- Confirms whether SEC actually improved or whether energy was simply saved by shutting down factory throughput.

---

## 2. Production-Normalized Baseline Formulation

To avoid false positive alarms caused by normal fluctuations in plant production volume, the baseline active power $P_{\text{expected}}(t)$ is modelled as a function of operational state and throughput rate:

$$P_{\text{expected}}(t) = \beta_0 + \beta_{\text{running}} \cdot \mathbb{I}(\text{State} = \text{RUNNING}) + \beta_{\text{idle}} \cdot \mathbb{I}(\text{State} = \text{IDLE}) + \beta_{\text{prod}} \cdot \text{Rate}(t)$$

Where:
- $\beta_0$: Base de-energized control power (PLC, indicators, sensors).
- $\beta_{\text{running}}$: Constant auxiliary power draw of the energized machine (coolant pump, hydraulics, lubrication pump).
- $\beta_{\text{idle}}$: Unloaded spinning loss (motor magnetization and mechanical friction when energized but waiting for stock).
- $\beta_{\text{prod}}$: Incremental electrical work per part manufactured per hour.

**Model Training:**
- Linear Ridge Regression with $L_2$ regularization ($\alpha = 1.0$) trained exclusively on verified healthy baseline segments ($\text{Anomaly} = \text{NONE}$).
- Explainable coefficients stored as open JSON artifacts (`models/baseline_coefficients.json`), allowing SME plant engineers to audit and adjust parameters directly.

---

## 3. Why This Solution Is Uniquely Suitable for Indian SMEs

1. **Low Instrumentation Cost (Capex Under ₹1.55 Lakhs)**:
   - Does not require replacing existing switchgear or machinery.
   - Non-invasive split-core CTs clamp around existing feeder cables during a scheduled 30-minute maintenance shutdown without interrupting plant wiring.
2. **Resilience to Poor Internet Connectivity (Edge-First)**:
   - Indian industrial SME clusters frequently experience broadband drops.
   - The edge gateway buffers up to 30 days of high-frequency electrical telemetry in a local circular SQLite cache and runs local rule-based safety trips independently of cloud connectivity.
3. **Exploits Time-of-Day (TOD) Industrial Tariffs**:
   - Indian state electricity boards (DISCOMs like MSEDCL, BESCOM, UGVCL, TANGEDCO) enforce steep peak-hour surcharges (up to ₹11.50–₹13.00/kWh between 18:00 and 22:00) compared to off-peak night incentives (₹5.00–₹5.50/kWh).
   - The platform systematically schedules flexible batch heating and stamping into off-peak windows, generating substantial rupee savings without requiring any capital investment in batteries.
4. **Simple Payback Under 3 Months**:
   - The capital cost is recovered within weeks through quick-win idle energy interlocks, APFC capacitor bank health alerts, and TOD load shifting.

---

## 4. Engineering Limitations & System Boundaries

- **Feeder Cable Losses**: Cable losses are theoretical calculations derived from nameplate cable length, cross-sectional area, and measured current ($3I^2R$). They are **not** direct sensory measurements.
- **Machine Health Score**: The 0–100 health index is a heuristic engineering ranking for maintenance scheduling. It is **not** an OEM-certified remaining useful life (RUL) prediction.
- **No Instantaneous Summation of Unsynchronized Field Readings**: Field reference measurements collected from disparate sources are used strictly for parameter range calibration, never summed as a single instantaneous plant state.
