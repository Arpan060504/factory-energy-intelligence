# Synthetic Dataset Design & Anomaly Scenario Specifications

## 1. Overview & SME Plant Profile

The synthetic dataset models a precision engineering and metal-working Indian SME facility (**"Apex Precision Components Ltd."** - Anonymized Generic SME). The facility operates on an 11 kV grid connection stepped down to 415 V via a 1000 kVA distribution transformer (`TR_01`) feeding 7 major industrial machine feeders plus a utility/lighting feeder.

### Machine Master Catalog

| Feeder ID | Machine ID | Machine Type | Rated Power (kW) | Rated Current (A) | Base PF | Cable Specs (Material, Length, Area) |
|---|---|---|---|---|---|---|
| FDR_01 | MOTOR_01 | CNC Machining Center | 75.0 | 125.0 | 0.88 | Aluminium 95 mm², 65 m |
| FDR_02 | MOTOR_02 | Hydraulic Stamping Press | 55.0 | 95.0 | 0.85 | Aluminium 70 mm², 45 m |
| FDR_03 | PUMP_01 | Chilled Water Pump | 30.0 | 52.0 | 0.86 | Aluminium 35 mm², 80 m |
| FDR_04 | COMP_01 | Screw Air Compressor | 45.0 | 78.0 | 0.87 | Aluminium 50 mm², 50 m |
| FDR_05 | FURNACE_01 | Induction Billet Heater | 160.0 | 255.0 | 0.92 | Copper 185 mm², 30 m |
| FDR_06 | LINE_01 | Conveyor & Assembly | 22.0 | 38.0 | 0.84 | Aluminium 25 mm², 110 m |
| FDR_07 | AUX_01 | Plant Aux & Lighting | 25.0 | 42.0 | 0.90 | Aluminium 25 mm², 90 m |

---

## 2. Dataset Temporal Characteristics

- **Time Horizon**: 30 days (1 month of continuous industrial operations)
- **Time Step ($\Delta t$)**: 5 minutes ($8,640$ timestamps per machine; $69,120$ total records across all 8 feeders)
- **Shift Schedule**:
  - Shift 1 (Morning): 06:00 to 14:00 (Active Production)
  - Shift 2 (Evening): 14:00 to 22:00 (Active Production)
  - Shift 3 (Night): 22:00 to 06:00 (Reduced Operations, Batch furnace processing, maintenance)
  - Sunday: Maintenance / low-load utility baseline

---

## 3. Physics-Informed Inter-Variable Relationships

Rather than generating independent random numbers, the dataset generator enforces strict physical and electrical laws:

1. **Power Equation**:
   $$P = \sqrt{3} \times V_{\text{avg}} \times I_{\text{avg}} \times \text{PF} / 1000$$
2. **Current Scaling**:
   $$I_{\text{avg}} = \frac{P \times 1000}{\sqrt{3} \times V_{\text{avg}} \times \text{PF}}$$
   Phase currents $I_r, I_y, I_b$ fluctuate symmetrically around $I_{\text{avg}}$ during normal operation with small natural imbalance ($\le 2.5\%$).
3. **Apparent & Reactive Power**:
   $$S = P / \text{PF}, \quad Q = \sqrt{S^2 - P^2}$$
4. **Energy Step**:
   $$E_{\text{interval}} = P \times \frac{5}{60}\text{ kWh}$$
5. **Operating States**:
   - `OFF`: $P \approx 0.05\text{ kW}$ (control circuit standby), $I \approx 0.1\text{ A}$, $\text{Prod} = 0$.
   - `IDLE`: Machine energized, motor spinning unloaded (hydraulics/air circulated), $P \approx 25\%\text{--}40\%$ of rated, $\text{Prod} = 0$.
   - `RUNNING`: $P \approx 65\%\text{--}95\%$ of rated, proportional to production rate.
6. **Vibration & Temperature**:
   - Baseline ambient temperature: $22^\circ\text{C}$ to $36^\circ\text{C}$ (Indian ambient diurnal cycle).
   - Motor temperature rise is driven by $I^2R$ loading and cooling airflow.
   - Vibration RMS baseline: $1.2$ to $2.2\text{ mm/s}$.

---

## 4. Ground-Truth Anomaly Scenarios

The synthetic generator embeds 7 distinct industrial anomalies at known intervals to benchmark detection engines:

### Scenario 1: Motor Efficiency Degradation (Mechanical Bearing Wear)
- **Machine**: `MOTOR_01` (CNC Spindle)
- **Time Window**: Days 7 to 10
- **Physical Symptoms**: Active power rises $+16\%$, phase currents rise $+18\%$, surface temperature rises $+14^\circ\text{C}$, vibration RMS rises from $1.8\text{ mm/s}$ to $4.9\text{ mm/s}$, while production output remains unchanged.
- **Root Cause**: Bearing race pitting and mechanical misalignment causing increased friction.

### Scenario 2: Excessive Compressor Idle Operation (Air Leaks / Unloaded Run)
- **Machine**: `COMP_01` (Screw Compressor)
- **Time Window**: Days 12 to 16
- **Physical Symptoms**: Compressor runs continuously unloaded ($16.5\text{ kW}$) during lunch breaks, shift handovers, and night idle windows when factory air demand is near zero.
- **Root Cause**: Plant pneumatic leaks (>30% leak rate) preventing the compressor controller from entering automatic auto-purge standby.

### Scenario 3: Low Power Factor Event (Capacitor Bank Cell Failure)
- **Machine**: Plant Bus / `MOTOR_02` & `COMP_01`
- **Time Window**: Days 18 to 20
- **Physical Symptoms**: Active power remains standard, but power factor deteriorates from $0.88$ down to $0.72\text{ lag}$. Apparent power $S$ surges from $120\text{ kVA}$ to $165\text{ kVA}$, risking utility penalty.
- **Root Cause**: Blown fuses in the 50 kVAR APFC capacitor bank step.

### Scenario 4: Three-Phase Current Imbalance
- **Machine**: `PUMP_01` (Chilled Water Pump)
- **Time Window**: Days 21 to 23
- **Physical Symptoms**: $I_r = 68\text{ A}, I_y = 51\text{ A}, I_b = 39\text{ A}$. Phase imbalance jumps to $28.3\%$ (NEMA formula), accompanied by local winding heating.
- **Root Cause**: High contact resistance on contactor terminal pole R and loose lug connection.

### Scenario 5: Abnormal Energy Consumption (Furnace Refractory Degradation)
- **Machine**: `FURNACE_01` (Induction Heater)
- **Time Window**: Days 24 to 27
- **Physical Symptoms**: Energy consumption per billet batch rises $+22\%$ above the production-normalized baseline.
- **Root Cause**: Deteriorated coil thermal insulation lining causing excessive thermal dissipation.

### Scenario 6: Inefficient Production Scheduling (Peak Tariff Operation)
- **Machine**: `FURNACE_01` & `MOTOR_02`
- **Time Window**: Days 14 to 28
- **Physical Symptoms**: Intensive 160 kW thermal batch heating scheduled between 18:00 and 22:00 (Peak TOD window at ₹11.50/kWh) despite sufficient spare capacity in the Off-Peak night window (₹5.20/kWh).
- **Root Cause**: Suboptimal shift job-dispatching by shop floor supervisor.

### Scenario 7: Machine Degradation Compound Failure
- **Machine**: `MOTOR_02` (Hydraulic Press)
- **Time Window**: Days 26 to 29
- **Physical Symptoms**: High current $+15\%$, severe vibration ($5.6\text{ mm/s}$), temperature $+18^\circ\text{C}$ above ambient, hydraulic valve cavitation.
- **Root Cause**: Hydraulic pump cavitation and oil contamination.
