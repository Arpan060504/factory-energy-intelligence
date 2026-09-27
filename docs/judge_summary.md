# Factory Energy Intelligence & Optimization Platform
## Executive Judge Summary & Defense Brief

**Competition:** Smart Manufacturing Challenge — Industrial Energy & Process Efficiency  
**Target Beneficiary:** Indian SME Discrete & Batch Manufacturing Plants  
**Release State:** Engineering Model Frozen (v1.0-RC1)  

---

### 1. What problem are we solving?
Indian manufacturing SMEs spend 15% to 35% of their operating costs on electricity under expensive Time-of-Day (TOD) tariffs (up to ₹11.50/kWh). Yet over 85% have zero sub-metering, leaving them unaware of which machines waste energy, whether consumption is justified by production output, or how to reduce energy without accidentally cutting factory production throughput.

### 2. Who pays for it?
The SME factory owner, plant director, or managing partner pays for the installation. Because electricity bills average ₹15–25 Lakhs per month, saving 15–18% generates ₹2.5–4.0 Lakhs in monthly cash flow, making the investment self-funding from operating savings within the first quarter.

### 3. What data does it require?
- **Electrical Telemetry:** 3-phase voltages ($V_{RY}, V_{YB}, V_{BR}$), phase currents ($I_R, I_Y, I_B$), active power ($P$), apparent power ($S$), power factor ($\text{PF}$) sampled at 5-minute intervals via standard RS485 Modbus meters.
- **Physical Sensor Data:** Motor bearing surface temperature (PT100 RTD) and 3-axis vibration velocity RMS ($10\text{–}1000\text{ Hz}$).
- **Operational Data:** Finished production piece counts per shift (from ERP or shopfloor operator log) and the local utility Time-of-Day tariff schedule.

### 4. What does the system actually do?
It executes a closed-loop cyber-physical intelligence cycle:
$$\mathbf{DETECT} \longrightarrow \mathbf{DIAGNOSE} \longrightarrow \mathbf{RECOMMEND} \longrightarrow \mathbf{OPTIMIZE} \longrightarrow \mathbf{VERIFY}$$
It normalizes energy against production output using machine learning, pinpoints abnormal equipment within the electrical hierarchy, triangulates physical root causes (e.g. bearing friction vs. electrical unbalance), issues prioritized maintenance SOPs, and reschedules flexible high-power loads into off-peak tariff slots.

### 5. How is Specific Energy Consumption (SEC) calculated?
$$\text{SEC} = \frac{\text{Total Active Electrical Energy Imported } [k\text{Wh}]}{\text{Total Finished Manufactured Output } [\text{Units}]}$$
When production is zero (or for utility assets like air compressors and water pumps that produce no discrete parts), direct SEC is mathematically undefined. The system returns `None` and displays `"N/A (Utility)"` to prevent division-by-zero errors or false claims of infinite efficiency.

### 6. How do we ensure production is preserved?
The optimization solver enforces a hard mathematical constraint:
$$\sum_{t=1}^{T} Q_{\text{optimized}}(t) \equiv \sum_{t=1}^{T} Q_{\text{baseline}}(t) \quad (\Delta Q = 0.0\text{ units})$$
If any proposed schedule throttles machine output or fails to deliver the full contract production target ($131,324.1\text{ units}$ in the canonical scenario), the optimization proposal is automatically rejected. Energy reduction is achieved purely through idle cutoff and mechanical restoration, never by reducing throughput.

### 7. How is physical energy saving different from tariff/cost saving?
- **Physical Energy Savings ($k\text{Wh}$):** Thermodynamic reduction in electricity consumed (31,973.1 kWh / month saved via idle compressor cutoffs and mechanical friction elimination).
- **Tariff Cost Savings ($\text{INR}$):** Financial savings achieved through Time-of-Day scheduling arbitrage (₹93,619 / month saved by shifting 12,998 kWh of billet furnace heating from Peak @ ₹11.50 to Off-Peak @ ₹5.20).
- **Crucial Distinction:** Shifting a load to night hours contributes **0.0 kWh** to physical energy savings because the physics of heating metal does not change. We strictly decouple these numbers and never combine them into a single misleading metric.

### 8. How is the solution deployed?
Via non-invasive retrofitting in under 2 days without factory shutdowns:
- Split-core CTs snap directly around live feeder cables.
- Standard Class 1.0 digital meters mount in an external IP65 enclosure.
- RS485 shielded serial daisy-chain connects meters to a DIN-rail Linux edge gateway.
- Temperature and vibration sensors attach magnetically to machine casings.

### 9. What does the pilot cost?
- **Single-Line Pilot (Tier 1):** **₹ 45,500** (~$550 USD) covering 2 digital smart meters, 6 split-core CTs, 1 edge gateway, and 1 vibration sensor.
- **Complete 8-Feeder Factory (Tier 2 - Canonical):** **₹ 1,52,150** (~$1,830 USD) turnkey hardware Capex.

### 10. What is the expected payback?
- **Theoretical Instantaneous Simple Payback:** **12.7 Days (~13 Days)** (₹1.52L Capex vs ₹3.58L net monthly savings on a ₹19.4L/mo power bill).
- **Pragmatic Phased Industrial Payback:** **1.8 to 3.5 Months** across progressive adoption (Month 1: 5% SEC savings, Month 2: 10% SEC savings, Month 3: full 16.7% optimization).
- **Net Year-1 ROI:** **₹ 41,50,911** (27.3× Capex multiple).

### 11. What is simulated?
The 30-day canonical dataset (60,480 rows) is generated using physical differential equations (alternating-current vector relationships, motor kinematics, thermal heat rise, and ISO 10816 vibration models) seeded with deterministic random seed 42.

### 12. What is measured?
Operating boundaries, voltage sags, power factors, and machine load factors are calibrated directly against empirical, anonymized industrial field telemetry from manufacturing plants (e.g. Reliance Industries Limited / textile and precision engineering facilities).

### 13. What happens when connectivity is lost?
The edge gateway operates completely autonomously. A local SQLite ring buffer stores up to **45 days** of 5-minute telemetry offline. If factory internet drops, zero records are lost, and local operator dashboards continue serving real-time analytics over the plant's internal LAN.

### 14. How does the system scale?
1. Single Machine $\rightarrow$ 2. Machining Cell $\rightarrow$ 3. Complete Factory (8 Feeders) $\rightarrow$ 4. Multi-Plant Enterprise (via centralized MQTT/PostgreSQL TimescaleDB cloud tier). The modular RS485 architecture allows adding new meters for ₹7,350 per feeder.
