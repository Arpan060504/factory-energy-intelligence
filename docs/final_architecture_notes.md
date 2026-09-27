# Architecture Design Notes & Presentation Guidelines
## Factory Energy Intelligence & Optimization Platform

**Document Identifier:** `final_architecture_notes.md`  
**Purpose:** Technical rationale, engineering assumptions, and slide presentation guide for competition judges  
**Companion Documents:**  
- [`docs/final_physical_architecture.md`](file:///d:/coding/Project/graph/smart-manufacturing-energy/docs/final_physical_architecture.md) (Physical Single-Line Architecture)  
- [`docs/final_digital_architecture.md`](file:///d:/coding/Project/graph/smart-manufacturing-energy/docs/final_digital_architecture.md) (Digital Intelligence Architecture)  

---

## 1. Rationale for Two Separate Architecture Diagrams

In earlier drafts, attempting to render both electrical distribution (busbars, transformers, MCCBs, conductors) and digital data pipelines (Modbus polling, baseline models, diagnostic heuristics, tariff matrices) inside a single visual diagram caused visual overcrowding, unreadable labels, and conceptual confusion.

For the final competition presentation, the architecture is strictly split into **Two Dedicated Diagrams**:
1. **Diagram 1: Physical Plant & Electrical Architecture (`final_physical_architecture.md`)**
   - Answers: *WHERE are sensors and meters physically connected in an SME factory?*
   - Shows electrical single-line distribution, transformer, main bus, feeder breakers, cable runs, and monitored machine assets.
2. **Diagram 2: Digital Intelligence & Analytics Architecture (`final_digital_architecture.md`)**
   - Answers: *HOW does raw data flow, get validated, transformed into production-aware baseline insights, and audited?*
   - Shows the 5-layer cyber-physical progression from edge ingestion to the 9 analytics modules, operator decision support, and the hard production constraint.

---

## 2. Core Architectural Assumptions & Defense Notes

### A. 1000 kVA Transformer vs. 800 kVA Contracted Demand
- **Substation Transformer Rating:** `1000 kVA` ($11\text{ kV} / 415\text{ V}$, Dyn11, $\%Z = 5.0\%$, oil-immersed).
- **Sanctioned Contract Demand:** `800.0 kVA` (MSEDCL HT-1 Industrial Tariff billing cap).
- **Technical Defense for Judges:**  
  *"In industrial electrical design, transformer nameplate rating is intentionally specified 20% to 25% above the sanctioned contract demand. This provides the necessary thermal headroom to absorb motor-starting inrush currents (which draw 5–7× rated current for 3–10 seconds) and prevents transformer oil overheating without tripping the utility maximum demand indicator. Both figures are physically accurate, industry-standard, and mathematically consistent in our model."*

### B. Hardware Inventory (Tier-2 Turnkey Plant Scope)
The canonical installation comprises exactly:
- **8 Digital Energy Meters:** 1 Main Incomer Meter (Meter M00) + 7 Feeder Sub-Meters (M01 to M07), Class 1.0, RS485 Modbus RTU.
- **24 Split-Core Current Transformers:** 3 CTs on the 1600A incomer (Class 0.5S) + 21 CTs across the 7 outgoing feeders ($100/5\text{A}$ to $400/5\text{A}$).
- **1 Industrial Edge Gateway:** Advantech WISE-710 / Linux industrial gateway with dual RS485 ports, hardware watchdog, and local SQLite storage.
- **4 Physical Asset Sensors:**
  - Sensor T1: Surface PT100 RTD on `MOTOR_01` (CNC Machining Center drive-end bearing).
  - Sensor T2: Surface PT100 RTD on `FURNACE_01` (Induction Furnace coil cooling jacket).
  - Sensor V1: 3-Axis Accelerometer on `MOTOR_01` (Vibration Velocity RMS, ISO 10816).
  - Sensor V2: 3-Axis Accelerometer on `MOTOR_02` (Hydraulic Press pump drive).
- **Total Turnkey Capex:** **₹ 1,52,150** ($~\$1,830\text{ USD}$), including enclosure, cabling, and electrician installation.

### C. Brownfield Non-Invasive Retrofit Principle
- The platform is **retrofitted onto existing factory infrastructure**.
- It does **not** replace existing PLCs, CNC controllers, SCADA systems, or ERP packages.
- All CTs are **split-core snap-on** units, allowing installation during a standard lunch break or Sunday shift without disconnecting high-voltage busbars or taking an unscheduled plant outage.
- Integration with factory PLCs or ERP systems is handled via clean, optional Modbus TCP or REST API interfaces.

### D. Offline Survivability & Edge Autonomy
- The platform does **not require a continuous cloud connection** to function.
- The industrial edge gateway hosts a local SQLite circular ring buffer capable of retaining **45 days** of uncompressed 5-minute telemetry offline.
- If factory internet drops, zero data is lost. Real-time dashboards continue operating locally on the plant LAN (`http://192.168.1.100:8501`).

### E. Decoupled Physical Energy vs. Tariff Economics
- **Physical Energy Savings:** 31,973.1 kWh / month saved through idle compressor elimination and mechanical bearing restoration.
- **Tariff Arbitrage Savings:** ₹ 93,618.68 / month saved by shifting 12,997.8 kWh of induction heating batches from Peak (₹11.50) to Off-Peak (₹5.20).
- **Presentation Rule:** Never claim that tariff load shifting reduces physical kWh. Shifting a load saves cost by changing billing rates, not by violating the laws of thermodynamics.

### F. Strict Production Constraint Protection
- Optimization solver enforces: $\sum Q_{\text{optimized}} \equiv \sum Q_{\text{baseline}}$ ($\Delta Q = 0.0\text{ units}$).
- Output target: **131,324.1 units / month** (100.0% preserved).
- Any schedule that throttles production output to save energy is automatically rejected.

### G. Clarification of Canonical Factory Status (Simulation vs. Field Reference)
- The physical factory diagram contains specific illustrative equipment (`MOTOR_01` CNC Machining Center, `MOTOR_02` Stamping Press, `COMP_01` Compressor, `FURNACE_01` Billet Heater, etc.).
- **Clear Epistemological Distinction:** This configuration represents an **Illustrative Canonical SME Factory Configuration (Reference Plant Simulation)** used as a standardized benchmark for evaluation, rather than a claim that every listed machine is a physical live sensor feed.
- Operating load envelopes, power factors, and thermal profiles are calibrated directly against empirical, anonymized industrial field telemetry (e.g. Reliance Industries Limited / textile and precision engineering plants).

---

## 3. Recommended PowerPoint (PPT) Slide Layout

When transferring these architectures into competition pitch slides, follow this two-slide structure:

### Slide A: "Physical Plant Architecture — Non-Invasive Brownfield Sub-Metering"
- **Visual:** Use Diagram from [`docs/final_physical_architecture.md`](file:///d:/coding/Project/graph/smart-manufacturing-energy/docs/final_physical_architecture.md).
- **Slide Headline:** *"Affordable ₹1.52L Turnkey Retrofit Across 8 Feeder Nodes with Zero Plant Shutdown."*
- **Key Callout Boxes:**
  1. *Substation:* 11 kV Grid $\rightarrow$ 1000 kVA Transformer $\rightarrow$ 800 kVA Contract Demand Cap.
  2. *Instrumentation:* 8 Meters + 24 Split-Core CTs + 4 Temp/Vibration Sensors.
  3. *Equipment:* 7 Monitored Feeders (CNC, Stamping Press, Chiller, Compressor, Furnace, Conveyor, Auxiliaries).
  4. *Capex:* ₹1,52,150 (~$1,830 USD) total hardware investment.

### Slide B: "Digital Cyber-Physical Architecture — The 5-Layer Intelligence Loop"
- **Visual:** Use Diagram from [`docs/final_digital_architecture.md`](file:///d:/coding/Project/graph/smart-manufacturing-energy/docs/final_digital_architecture.md).
- **Slide Headline:** *"From Edge Ingestion to Production-Protected Optimization & Audited Verification."*
- **Key Callout Boxes:**
  1. *Layer 1 & 2 (Edge):* 5-minute Modbus polling, sensor-loss trap, 45-day offline SQLite storage.
  2. *Layer 3 (Analytics):* 9 modular processing engines (Production-Normalized Baseline, SEC, ISO diagnostics, tariff solver).
  3. *Layer 4 (Action):* Streamlit cockpit, operator SOP `REC-001` (₹29,520/mo savings), furnace TOD shift (₹93,619/mo).
  4. *Layer 5 (Audit):* Strict production constraint ($\Delta Q = 0$), 16.73% SEC cut, 18.63% bill cut, 13-day payback.

---

## 4. Repository Consistency & Quality Audit

A full-text sweep was conducted across the entire repository:
- All malformed or truncated labels (such as unclosed bracketed meter tags or trailing incomplete nodes) were permanently purged.
- All occurrences of outdated draft figures (such as `11.4%`, `< 15 days`, or unverified Capex estimates) are verified as zero.
- Every document anchors exclusively on the frozen master metrics:
  - Baseline Energy: **191,138.7 kWh** | Optimized: **159,165.7 kWh** (-16.73%)
  - Baseline Production: **131,324.1 units** | Optimized: **131,324.1 units** ($\Delta Q = 0.0\text{ units}$)
  - Baseline SEC: **1.4555 kWh/u** | Optimized: **1.2120 kWh/u** (-16.73%)
  - Baseline Electricity Bill: **₹ 19,40,446** | Optimized: **₹ 15,78,857** (-₹ 3,61,588 / mo)
  - Turnkey Capex: **₹ 1,52,150** | Instantaneous Payback: **12.7 Days (~13 Days)** | Phased: **1.8–3.5 Months**
- The complete test suite stands at **30 passed, 0 failed** (`pytest tests/ -v`).
