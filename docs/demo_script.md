# Factory Energy Intelligence & Optimization Platform
## 3–5 Minute Hackathon Live Demonstration Script

**Target Challenge:** Smart Manufacturing — Industrial Energy & Process Efficiency  
**Target SME Facility:** Apex Precision Components Ltd., Bhosari Industrial Estate, Pune, Maharashtra  
**Presenter Role:** Lead System Architect & Energy Engineering Lead  
**UI Setting:** Streamlit App in **"🎯 HACKATHON DEMO MODE"**  

---

### Central Presenter Narrative

> *"Most Indian SMEs know their monthly electricity bill down to the rupee. What they don't know is which specific machine caused the spike, whether that consumption was justified by production throughput, or what precise physical action will eliminate the waste without throttling production output.*
>
> *Our platform bridges high-resolution electrical telemetry, machine kinematics, production scheduling, and Time-of-Day energy economics. It doesn't stop at detecting an anomaly. It pinpoints the exact equipment in the electrical hierarchy, synthesizes a physical root-cause diagnosis, issues a prioritized maintenance SOP, executes an algorithmic optimization that strictly protects production output, and audits the result.*
>
> *Our North Star metric is not gross energy — it is **Specific Energy Consumption (SEC)**: kWh consumed per finished automotive component."*

---

### Detailed Demonstration Timeline (5 Minutes Total)

---

#### 0:00 – 0:30 | Problem Introduction
- **WHAT THE PRESENTER CLICKS:**
  - Launch browser at `http://localhost:8501`.
  - Confirm sidebar shows **"🎯 HACKATHON DEMO MODE"** and select **"1. Normal Factory Operation"**.
- **WHAT THE AUDIENCE SEES:**
  - Clean, professional industrial dashboard titled *"Factory Energy Intelligence & Optimization Platform"*.
  - Five hero KPI cards:
    - Specific Energy (SEC): **1.3919 kWh/unit** (Normal Baseline)
    - Production Output: **5,251 units** (Daily target met)
    - Total Active Energy: **7,309.1 kWh** (-0.2% vs expected)
    - Electricity Cost: **₹ 57,011 / day**
    - Scope 2 Carbon: **5.23 MT CO2**
  - Diurnal load curve tracking smoothly along the green dashed baseline.
- **WHAT THE PRESENTER SAYS:**
  - *"Good morning, judges. We are looking at Apex Precision Components, a Tier-2 automotive machining plant in Pune with an 800 kVA contracted demand. Under normal operating conditions, like Tuesday, March 3rd, the factory consumes 7,309 kWh to manufacture 5,251 precision parts.*
  - *Notice our headline metric: Specific Energy Consumption, or SEC, is 1.3919 kWh per unit. The actual electrical draw tracks within ±0.2% of our production-normalized Ridge regression baseline. All 7 plant feeders are operating nominally."*

---

#### 0:30 – 1:00 | Factory Overview & Digital Electrical Topology
- **WHAT THE PRESENTER CLICKS:**
  - Point to the facility metadata in the sidebar (Substation SUB_01, 1000 kVA Transformer Dyn11, 415V Bus BUS_A, MSEDCL HT-1 TOD tariffs: ₹5.20 Off-Peak, ₹7.80 Normal, ₹11.50 Peak).
- **WHAT THE AUDIENCE SEES:**
  - Status indicator: `🟢 Edge Gateway Online (5-minute telemetry)`.
  - Feeder energy share pie chart showing balanced distribution between CNC machining centers, stamping presses, air compressors, and induction furnaces.
- **WHAT THE PRESENTER SAYS:**
  - *"Our edge IoT gateway ingests 5-minute telemetry across 8 digital energy meters, capturing three-phase currents, voltages, power factors, and estimated $I^2R$ feeder cable losses. The platform models the entire physical single-line topology from the 11 kV grid down to individual machine spindles.*
  - *Now, let's observe what happens when operational conditions degrade."*

---

#### 1:00 – 1:45 | Energy Anomaly Detection
- **WHAT THE PRESENTER CLICKS:**
  - Click **"Next Step ▶"** (or select **"2. Energy Anomaly Detected"** on the Demo Control Panel).
- **WHAT THE AUDIENCE SEES:**
  - Header badge flips to `🔴 STEP 2 OF 6 | ANOMALY DETECTION`.
  - Hero KPI updates:
    - Specific Energy (SEC) degrades to **1.4279 kWh/unit** (`+2.6% degraded`).
    - Production Output: **5,272 units** (`+0.4% - virtually identical`).
    - Active Energy: **7,527.9 kWh** (`+183.7 kWh excess / +2.5%`).
    - Daily Cost: **₹ 58,718** (`+₹ 1,707 excess spend`).
  - Active power chart on March 9 displays a prominent red shaded area where actual power surges above the dashed baseline curve between 08:00 and 20:00.
  - Prominent warning banner: *"⚠️ Plant Energy Consumption is +183.7 kWh (+2.5%) above expected baseline with constant production."*
- **WHAT THE PRESENTER SAYS:**
  - *"Six days later, on Monday, March 9th, the plant manager receives an energy alert. The plant consumed 7,528 kWh — an excess of 184 kWh above expected.*
  - *In a conventional factory, management might assume production was higher. But look at our Production card: output was 5,272 units, practically identical to normal day output (+0.4%). As a direct result, Specific Energy Consumption degraded by +2.6% to 1.4279 kWh/unit.*
  - *This is the critical difference: our platform detects that energy is being wasted because it normalizes consumption against production throughput in real time."*

---

#### 1:45 – 2:30 | Drill-Down: Finding the Machine
- **WHAT THE PRESENTER CLICKS:**
  - Click **"Next Step ▶"** (or select **"3. Drill-Down: Find the Machine"**).
- **WHAT THE AUDIENCE SEES:**
  - Header badge updates to `🔍 STEP 3 OF 6 | TOPOLOGICAL LOCALIZATION`.
  - Single-line hierarchy diagram highlighting Feeder FDR_01 in red:
    `Grid ➔ Substation SUB_01 ➔ Bus BUS_A ➔ Feeder FDR_01 ➔ MOTOR_01 (+188.1 kWh EXCESS!)`
  - Equipment telemetry comparison table and metric cards for `MOTOR_01`:
    - Average Current: **84.2 A ➔ 97.2 A (+15.4% draw)**
    - Active Power: **52.7 kW ➔ 60.9 kW (+14.8% excess)**
    - Bearing Vibration RMS: **1.49 mm/s ➔ 3.99 mm/s (+167.8% surge, Exceeds ISO 10816-3 2.8 mm/s limit)**
    - Bearing Temperature: **42.1 °C ➔ 53.9 °C (+11.8 °C rise)**
    - Supply Voltage: **412.8 V (Balanced)**
    - Production: **827.3 u ➔ 831.9 u (+0.6% - strictly unchanged)**
    - Machine SEC: **1.5284 ➔ 1.7560 kWh/u (+14.9% efficiency loss)**
  - Dual-axis graph of `MOTOR_01` showing power surge correlated with vibration velocity.
- **WHAT THE PRESENTER SAYS:**
  - *"Now we answer question number one: WHERE is the waste occurring?*
  - *The system automatically traverses the electrical bus hierarchy. Feeders 2 through 7 are completely normal. But on Feeder FDR_01, driving CNC Machining Center MOTOR_01, energy consumption jumped by +188.1 kWh. That single 75 kW machine accounts for more than 100% of the entire plant's net excess energy!*
  - *Look at the telemetry: average current jumped from 84 to 97 Amperes (+15.4%). Stator and bearing temperature rose by 11.8°C. Vibration RMS more than doubled from 1.49 to 3.99 mm/s, breaching the ISO 10816-3 Class II threshold of 2.8 mm/s.*
  - *Yet production output remained flat at 832 parts. This machine is fighting severe internal resistance."*

---

#### 2:30 – 3:15 | Root Cause Diagnosis & Actionable Maintenance SOP
- **WHAT THE PRESENTER CLICKS:**
  - Click **"Next Step ▶"** (or select **"4. Root Cause & SOP Recommendation"**).
- **WHAT THE AUDIENCE SEES:**
  - Header badge updates to `📋 STEP 4 OF 6 | ROOT CAUSE & RECOMMENDATION`.
  - Physical Evidence Matrix summarizing power (+14.8%), current (+15.4%), vibration (+167.8%), temperature (+11.8°C), and phase unbalance (1.2% - Normal).
  - Diagnostic Synthesis Card:
    - *"Diagnosis: Mechanical bearing race wear and shaft misalignment causing severe parasitic friction torque. The motor is drawing electrical current to fight mechanical resistance, not to cut metal."*
  - Standard Operating Procedure Card `REC-001` (High Priority):
    - **WHAT HAPPENED?**
    - **WHY?**
    - **RECOMMENDED ACTION:** Bearing regreasing at 14:00 handover, laser shaft alignment, cooling cowl cleaning.
    - **EXPECTED IMPACT:** 3,473 kWh/mo saved | ₹29,520/mo cost saved | 2.48 MT CO2 avoided | Payback < 2 days.
- **WHAT THE PRESENTER SAYS:**
  - *"We don't simply say 'AI found an anomaly.' We provide the physical engineering proof.*
  - *Notice that three-phase voltage and current remain balanced (1.2% unbalance). That proves the contactor switchgear and supply phases are intact — this is NOT an electrical single-phasing or terminal fault. The co-occurrence of high vibration and temperature with constant machining throughput proves it is mechanical bearing race friction and shaft misalignment.*
  - *Instead of sending an ambiguous alert, the platform generates a concrete, prioritized Standard Operating Procedure for the maintenance supervisor: regrease the drive-end bearing at the 14:00 shift handover, check laser alignment, and blow out the cooling cowl. Quantified financial impact: ₹29,520 saved every month."*

---

#### 3:15 – 4:00 | Algorithmic Optimization with Strict Production Protection
- **WHAT THE PRESENTER CLICKS:**
  - Click **"Next Step ▶"** (or select **"5. Apply Optimization"**).
- **WHAT THE AUDIENCE SEES:**
  - Header badge updates to `⚡ STEP 5 OF 6 | THREE-TIER OPTIMIZATION`.
  - **🛡️ Production Protection Guarantee Banner:**
    - Contract Requirement: **131,324.1 units**
    - Baseline Output: **131,324.1 units**
    - Optimized Output: **131,324.1 units (0.0 units change)**
    - Status: `✅ PRODUCTION CONSTRAINT SATISFIED: Throughput 100.0% Preserved`
  - Three optimization levers displayed side-by-side:
    1. **Idle Energy Elimination:** Interlocking compressor COMP_01 during shift breaks (saves 31,973 kWh / ₹2,67,970/mo).
    2. **TOD Tariff Load Shifting:** Rescheduling 160 kW furnace batches from Peak (₹11.50) to Off-Peak (₹5.20) (saves ₹93,619/mo; 0.0 kWh physical energy change).
    3. **Mechanical Health Restoration:** Restoring MOTOR_01 via SOP REC-001 (saves 3,473 kWh / ₹29,520/mo).
- **WHAT THE PRESENTER SAYS:**
  - *"Now we act. We run our multi-tier optimization engine.*
  - *Before looking at cost savings, look at the top banner: **Production output is strictly invariant at 131,324 units**. In industrial manufacturing, if you cut energy by shutting down lines or slowing down feed rates, you lose revenue. Our optimization solver enforces a hard constraint: if production output drops by even a fraction of a unit, the optimization is mathematically rejected.*
  - *The algorithm activates three synchronized levers: it interlocks the air compressor to stop 18 kW of unloaded idling during shift breaks; it shifts the 160 kW induction furnace heating cycle into the night off-peak tariff slot without missing morning delivery deadlines; and it restores the CNC motor's mechanical health."*

---

#### 4:00 – 4:30 | Audited Before vs. After Verification & Decoupled Waterfalls
- **WHAT THE PRESENTER CLICKS:**
  - Click **"Next Step ▶"** (or select **"6. Audited Before vs After & Summary"**).
- **WHAT THE AUDIENCE SEES:**
  - Header badge updates to `🏆 STEP 6 OF 6 | AUDITED VERIFICATION & ROI`.
  - Master Audited Comparison Table:
    - Energy: **191,139 ➔ 159,166 kWh (-16.73%)**
    - Production: **131,324 ➔ 131,324 units (0.00% Change)**
    - SEC: **1.4555 ➔ 1.2120 kWh/unit (-16.73% Improvement)**
    - Electricity Bill: **₹ 19,40,446 ➔ ₹ 15,78,857 (-₹ 3,61,588 / month, -18.63%)**
    - Peak Demand: **462.7 ➔ 450.1 kVA (-12.6 kVA shaved)**
    - Carbon Emissions: **136.85 ➔ 113.96 MT CO2 (-22.89 MT CO2 avoided / mo)**
  - Dual Decoupled Plotly Waterfall Charts:
    - **Physical Energy Waterfall (kWh):** Baseline (191.1k) ➔ Idle (-28.5k) ➔ Mech (-3.5k) ➔ TOD (0k) ➔ Optimized (159.2k).
    - **Cost Savings Waterfall (₹):** Baseline (₹19.4L) ➔ Idle (-₹2.38L) ➔ Mech (-₹0.30L) ➔ TOD Shifting (-₹0.94L) ➔ Optimized (₹15.79L).
- **WHAT THE PRESENTER SAYS:**
  - *"Here is the audited proof across the 30-day trial period.*
  - *Plant electricity consumption dropped from 191,139 kWh to 159,166 kWh — an audited physical reduction of 16.73%. Because production is 100% preserved, plant SEC dropped directly from 1.4555 to 1.2120 kWh per unit.*
  - *Look closely at the two waterfall charts below: we strictly decouple physical energy from tariff economics. Notice that Time-of-Day load shifting contributes zero physical kWh savings — because shifting a load does not alter its physics. But in the cost waterfall, that same tariff shifting delivers ₹93,619 in pure cost savings by moving power from ₹11.50 peak to ₹5.20 off-peak.*
  - *Total monthly electricity cost drops by ₹3,61,588 — an 18.63% reduction on a ₹19.4 Lakh monthly bill."*

---

#### 4:30 – 5:00 | Executive Summary & Turnkey SME Business Case
- **WHAT THE PRESENTER CLICKS:**
  - Scroll down to the glowing Executive Summary Block and Turnkey ROI Cards.
- **WHAT THE AUDIENCE SEES:**
  - High-contrast Executive Summary Card:
    ```
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                        FACTORY OPTIMIZATION RESULT                           ║
    ║   • Active Energy:       191,138.7 kWh   ──►   159,165.7 kWh   (-16.73%)     ║
    ║   • Specific Energy:     1.4555 kWh/u    ──►   1.2120 kWh/u    (-16.73%)     ║
    ║   • Factory Production:  131,324.1 units ──►   131,324.1 units (0.00% Δ)    ║
    ║   • Electricity Bill:    ₹ 19,40,446     ──►   ₹ 15,78,857     (-18.63%)     ║
    ║   • Carbon Emissions:    136.85 MT CO2   ──►   113.96 MT CO2   (-22.89 MT)   ║
    ║              ✓ Production constraint: SATISFIED (100% Protected)             ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    ```
  - Turnkey SME Business Model:
    - Hardware BOM Capex: **₹ 1,52,150** (~$1,830 USD for 8 meters, CTs, gateway, enclosure)
    - Monthly SaaS: **₹ 3,000 / month**
    - Net Monthly Savings: **₹ 3,58,588 / month**
    - Instantaneous Payback: **12.7 Days (~13 Days)**
    - Phased Industrial Payback: **1.8 to 3.5 Months**
    - Net Year-1 ROI: **₹ 41.5 Lakhs** (27.3× multiple).
- **WHAT THE PRESENTER SAYS:**
  - *"To make this viable for Indian SMEs, the technology must be affordable. We designed a complete turnkey hardware Bill of Materials using standard RS485 Modbus meters, split-core CTs, and an industrial DIN-rail edge gateway. Total hardware capital expenditure is just ₹1,52,150 — under $1,850 USD.*
  - *Against net savings of ₹3.58 Lakhs per month, the theoretical instantaneous payback is under 13 days. In a realistic factory deployment with phased adoption, full capital payback is achieved in under 3.5 months, delivering over ₹41 Lakhs in net bottom-line cash savings in Year 1.*
  - *This is how Indian SMEs become globally competitive: real-time electrical visibility, rigorous SEC reduction, zero throughput loss, and an affordable, defensible technology platform. Thank you, and we welcome your questions."*
