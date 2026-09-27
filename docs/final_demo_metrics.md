# Factory Energy Intelligence & Optimization Platform
## Final Hackathon Demonstration Metrics (Canonical 30-Day Evaluation)

**Release Version:** v1.0-RC1 (Engineering Model Frozen)  
**Target Facility:** Apex Precision Components Ltd., Bhosari Industrial Estate, Pune, Maharashtra  
**Audit Scope:** 30-Day Evaluation Period (March 1 to March 30, 2026, 60,480 Telemetry Records, 5-Min Resolution)  
**Tariff Model:** MSEDCL HT-1 Industrial (Off-Peak ₹5.20 / Normal ₹7.80 / Peak ₹11.50 per kWh)  
**Grid Carbon Factor:** 0.716 kg CO2 / kWh (CEA CO2 Baseline Database Version 19)  

---

### 1. Master Performance Metrics Table

| Performance Dimension | Unit of Measurement | Baseline Value | Optimized Value | Impact Delta | Change (%) | Evaluation Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Total Active Energy** | kWh | `191,138.7` | `159,165.7` | `-31,973.1` | **-16.73%** | Audited Reduction |
| **Production Throughput** | Finished Units | `131,324.1` | `131,324.1` | `0.0` | **0.00%** | **Strictly Invariant (100% Protected)** |
| **Specific Energy Consumption (SEC)** | kWh / unit | `1.4555` | `1.2120` | `-0.2435` | **-16.73%** | Audited SEC Improvement |
| **Total Electricity Bill** | INR (₹) | `19,40,446` | `15,78,857` | `-3,61,588` | **-18.63%** | Monthly Cost Reduction |
| **Off-Peak Energy Cost** | INR (₹) | `2,87,545` | `2,89,552` | `+2,007` | `+0.70%` | Increased (Night Batch Shift) |
| **Normal Day Energy Cost** | INR (₹) | `7,91,535` | `6,78,018` | `-1,13,517` | `-14.34%` | Reduced (Idle Elimination) |
| **Evening Peak Energy Cost**| INR (₹) | `3,95,172` | `1,90,407` | `-2,04,764` | `-51.82%` | Shaved (Thermal Batch Shift) |
| **Sanctioned Demand Charge** | INR (₹) | `4,66,194` | `4,20,880` | `-45,314` | `-9.72%` | Shaved Peak Demand |
| **Peak Apparent Demand** | kVA | `462.7` | `450.1` | `-12.6` | **-2.72%** | Shaved below 800 kVA cap |
| **Scope 2 Carbon Emissions**| Metric Tonnes CO2 | `136.855` | `113.963` | `-22.893` | **-16.73%** | Avoided Greenhouse Gas |

---

### 2. Decomposition of Monthly Cost Savings (₹ 3,61,588 / month)

| Optimization Lever | Physical kWh Saved | Monthly Cost Saved (₹) | % of Total Cost Savings | Mechanism |
| :--- | :---: | :---: | :---: | :--- |
| **1. Idle Energy Elimination** | 28,500.0 kWh | ₹ 2,38,450 | 65.9% | Interlocking compressor `COMP_01` & machinery during breaks |
| **2. Mechanical Restoration (SOP REC-001)**| 3,473.1 kWh | ₹ 29,520 | 8.2% | Regreasing bearing & alignment on `MOTOR_01` (CNC center) |
| **3. TOD Tariff Load Shifting** | **0.0 kWh** | **₹ 93,619** | **25.9%** | Shifting 12,997.8 kWh from Peak (₹11.50) to Off-Peak (₹5.20) |
| **Total Plant Optimization** | **31,973.1 kWh** | **₹ 3,61,588** | **100.0%** | Decoupled physical energy vs. tariff economics |

> **Crucial Decoupling Note:** Time-of-Day (TOD) tariff load shifting generates **₹ 93,618.68 / month** in pure financial savings with **0.0 kWh of physical energy change**, because shifting an induction heating batch to night hours alters billing rates without altering thermodynamic energy requirements.

---

### 3. Canonical Demo Anomaly Metrics (Single-Day Incident: March 9 vs. March 3)

| Metric | Normal Day (March 3, 2026) | Anomalous Day (March 9, 2026) | Delta / Deviation |
| :--- | :---: | :---: | :---: |
| **Plant Active Energy** | 7,309.1 kWh | 7,527.9 kWh | **+183.7 kWh (+2.5% excess)** |
| **Plant Expected Baseline Energy** | 7,321.7 kWh | 7,344.2 kWh | +22.5 kWh (+0.3%) |
| **Plant Production Throughput** | 5,251.0 units | 5,272.2 units | **+21.2 units (+0.4% - Unchanged)** |
| **Plant Specific Energy (SEC)** | 1.3919 kWh/unit | 1.4279 kWh/unit | **+0.0360 kWh/u (+2.6% degraded)** |
| **Machine FDR_01 (`MOTOR_01`) Energy** | 1,264.4 kWh | 1,460.8 kWh | **+188.1 kWh (+14.8% excess)** |
| **Machine FDR_01 Active Power Avg** | 52.7 kW | 60.9 kW | **+8.2 kW (+14.8% excess)** |
| **Machine FDR_01 Average Current** | 84.2 A | 97.2 A | **+13.0 A (+15.4% draw)** |
| **Machine FDR_01 Vibration RMS** | 1.49 mm/s | 3.99 mm/s | **+2.50 mm/s (+167.8% - ISO Class II)** |
| **Machine FDR_01 Temperature** | 42.1 °C | 53.9 °C | **+11.8 °C (Thermal rise)** |
| **Machine FDR_01 Production** | 827.3 units | 831.9 units | **+4.6 units (+0.6% - Constant)** |
| **Machine FDR_01 Feeder SEC** | 1.5284 kWh/unit | 1.7560 kWh/unit | **+0.2276 kWh/u (+14.9% degraded)** |

---

### 4. Turnkey SME Business Model & Payback Analysis

#### Capital Expenditure (Turnkey 8-Feeder Hardware BOM)
- 8 × 3-Phase Digital Smart Energy Meters (RS485 Modbus RTU, Class 1.0): ₹ 52,000
- 24 × Class 0.5S Split-Core Current Transformers (100A–400A): ₹ 20,400
- 1 × Industrial DIN-Rail Edge IoT Gateway (Quad-Core, RS485/Ethernet/WiFi/MQTT): ₹ 22,000
- 4 × Surface Temperature (PT100) & Vibration Sensors: ₹ 18,000
- 1 × IP65 Control Enclosure, Shielded Twisted-Pair Cabling, Power Supplies: ₹ 24,750
- 1 × Installation, Wiring, Setup & Calibration Commissioning: ₹ 15,000
- **Total Turnkey Capital Expenditure (Capex):** **₹ 1,52,150** ($~\$1,830 USD)

#### Operational Economics & Payback
- **Annual Software & Cloud Analytics Subscription:** ₹ 36,000 / year (₹ 3,000 / month)
- **Gross Monthly Cost Reduction:** ₹ 3,61,588 / month
- **Net Monthly Savings (Gross Savings - SaaS):** **₹ 3,58,588 / month**
- **Theoretical Instantaneous Simple Payback:**
  $$\text{Payback} = \frac{\text{Capex}}{\text{Net Monthly Saving}} \times 30 = \frac{₹ 1,52,150}{₹ 3,58,588} \times 30 = \mathbf{12.7 \text{ Days (~13 Days)}}$$
- **Pragmatic Phased Industrial Payback (SME Adoption Curve):**
  - Month 1 (Visibility & basic shutoff): 5% SEC improvement $\rightarrow$ ₹ 97,000 saving
  - Month 2 (Operator SOP compliance): 10% SEC improvement $\rightarrow$ ₹ 1,94,000 saving
  - Month 3 (Full 16.7% optimization + furnace TOD shifting): ₹ 3,61,588 saving
  - **Pragmatic Payback Window:** **1.8 to 3.5 Months**
- **Net Year-1 Return on Investment (ROI):**
  $$\text{Net Year-1 ROI} = (\text{Net Monthly Saving} \times 12) - \text{Capex} = (₹ 3,58,588 \times 12) - ₹ 1,52,150 = \mathbf{₹ 41,50,911}$$
- **Year-1 ROI Multiple:** **27.3× Capex**

---

### 5. Production Constraint Verification Sign-Off

$$\sum Q_{\text{baseline}} = 131,324.1 \text{ units} \equiv \sum Q_{\text{optimized}} = 131,324.1 \text{ units} \quad (\Delta Q = 0.0 \text{ units})$$

- **Constraint Status:** **SATISFIED**
- **Verification Result:** Passed automated regression suite assertion (`assert comparison['impact']['production_constraint_satisfied'] is True`).
