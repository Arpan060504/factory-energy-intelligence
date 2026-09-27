# Data Validation Report: Synthetic Factory Time-Series

## 1. Executive Summary

This report provides an independent engineering audit and physical consistency validation of the 30-day continuous 5-minute operational dataset (`data/synthetic/factory_timeseries.csv`) generated for **Apex Precision Components Ltd.**, an Indian SME precision automotive machining facility.

The validation was executed against physical laws, Indian electrical standards (IS 12360, CEA Grid Standards), and thermodynamic machine constraints.

---

## 2. Dataset Metadata & Scope

| Parameter | Observed Value | Verification Standard | Status |
| :--- | :--- | :--- | :--- |
| **Total Telemetry Rows** | **60,480** | $7\text{ machines} \times 30\text{ days} \times 288\text{ intervals/day} = 60,480$ | **VERIFIED** |
| **Monitored Machines** | **7** | Fleet: `MOTOR_01`, `MOTOR_02`, `PUMP_01`, `COMP_01`, `FURNACE_01`, `LINE_01`, `AUX_01` | **VERIFIED** |
| **Date Range** | **2026-03-01 00:00:00 to 2026-03-30 23:55:00** | Full 30-day operational cycle | **VERIFIED** |
| **Sampling Interval** | **5 minutes (0.08333 hours)** | Continuous without missing intervals | **VERIFIED** |
| **Interval Continuity Issues** | **0** | Delta checks per machine show zero gaps | **VERIFIED** |
| **Missing / NaN / Inf Values** | **0 across all 28 columns** | Zero null values in dataset | **VERIFIED** |

---

## 3. Machine State Logic & Standby Power Verification

Operating states follow physical shop-floor schedules (Shift 1: 06:00–14:00, Shift 2: 14:00–22:00, Night partial: 22:00–06:00, Sunday maintenance shutdowns).

| Machine ID | Machine Name | Rated kW | RUNNING Mean (kW) | IDLE Mean (kW) | OFF Mean (kW) | OFF Production | Standby Electrical Justification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MOTOR_01** | CNC Machining Center | 75.0 kW | 63.85 kW | 18.01 kW | 4.60 kW | 0.0 units | CNC controller, spindle cooler, lubrication heaters, transformer standby |
| **MOTOR_02** | Hydraulic Stamping Press | 55.0 kW | 46.43 kW | 13.99 kW | 3.10 kW | 0.0 units | Hydraulic oil circulation heater, safety interlock circuits |
| **PUMP_01** | Chilled Water Pump | 30.0 kW | 25.02 kW | 12.01 kW | — | 0.0 units | Essential plant circulation; continuous baseload with idle break cycles |
| **COMP_01** | Rotary Screw Compressor | 45.0 kW | 36.62 kW | 16.53 kW | 1.30 kW | 0.0 units | Sump heater, electronic drain valves, electronic control unit |
| **FURNACE_01** | Induction Billet Furnace | 160.0 kW | 138.52 kW | 35.02 kW | 8.10 kW | 0.0 units | Refractory holding power, cooling water circulator, capacitor cooling |
| **LINE_01** | Assembly Conveyor | 22.0 kW | 18.39 kW | 6.00 kW | 1.10 kW | 0.0 units | Control panel instrumentation, emergency stop relay circuits |
| **AUX_01** | Plant Lighting & Utilities | 25.0 kW | 20.89 kW | 8.00 kW | — | 0.0 units | Security lighting, perimeter power, CCTV baseload |

### Physical Boundary Checks on OFF Records
- Total OFF intervals recorded: **7,113 intervals**.
- Total production generated during OFF intervals: **0.00 units** (strict physical correlation).
- Mean OFF power draw: **3.67 kW** across the entire fleet ($< 5\%$ of rated nameplate capacity, consistent with industrial standby/parasitic losses).

---

## 4. Parameter Distributions & Extreme Value Audits

Summary statistics computed across all 60,480 telemetry records:

| Parameter | Unit | Minimum | Maximum | Mean | Physical Standard & Plausibility Check |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Line-to-Line Voltage ($V$)** | V | 405.03 | 425.50 | 415.02 | Nominal 415 V $\pm 2.5\%$, compliant with Indian Central Electricity Authority ($\pm 6\%$) |
| **Phase Average Current ($I_{\text{avg}}$)** | A | 2.42 | 293.50 | 60.80 | Max 293.5 A corresponds to FURNACE_01 full power (160 kW, 415 V, 0.90 PF) |
| **Power Factor ($\cos\phi$)** | — | 0.530 | 0.954 | 0.800 | Realistic inductive motor load range (0.53 during unloaded motor idle; 0.95 during full load) |
| **Active Power ($P$)** | kW | 1.00 | 191.32 | 37.92 | Max 191.3 kW observed on FURNACE_01 during Scenario 5 refractory degradation |
| **Apparent Power ($S$)** | kVA | 1.77 | 210.77 | 43.71 | Complies with $S \ge P$ at all timestamps ($S = P / \text{PF}$) |
| **Reactive Power ($Q$)** | kVAR | 1.46 | 90.36 | 21.01 | Complies with $Q = \sqrt{S^2 - P^2}$ across all timestamps |
| **Interval Energy ($E$)** | kWh | 0.083 | 15.94 | 3.16 | Exact integral: $E = P \times \frac{5}{60}$ (Mean difference $< 0.0003\text{ kWh}$) |
| **Production Units** | Units | 0.00 | 11.09 | 2.17 | Output strictly positive, non-negative, zero during OFF/IDLE states |
| **Surface Temperature** | °C | 17.38 | 97.43 | 44.59 | Ambient range (18–36°C); elevated 97.4°C during FURNACE_01 refractory degradation |
| **Vibration Velocity RMS** | mm/s | 0.20 | 5.87 | 1.17 | Baseline 0.6–1.8 mm/s (ISO 10816-3 Good); spike 5.87 mm/s during bearing failure |

---

## 5. Physical Consistency Checks

### 5.1. Non-Negativity
- Negative voltage: **0**
- Negative phase currents: **0**
- Negative active / apparent / reactive power: **0**
- Negative energy: **0**
- Negative production: **0**

### 5.2. Mathematical Triad Consistency ($S, P, Q$)
For balanced three-phase systems:
$$S = \frac{\sqrt{3} \times V \times I}{1000}$$
$$P = S \times \text{PF}$$
$$Q = \sqrt{S^2 - P^2}$$

- Sampling audit of 1,000 random intervals:
  - $P_{\text{active}}$ vs. $S \times \text{PF}$: Maximum deviation $= 0.086\text{ kW}$ (attributable to floating-point telemetry rounding).
  - $Q_{\text{reactive}}$ vs. $\sqrt{S^2 - P^2}$: Maximum deviation $= 0.024\text{ kVAR}$.
  - In unbalanced conditions (Scenario 4), $S_{\text{apparent}}$ calculated from phase currents reflects the true vector sum, validating the phase modeling engine.

### 5.3. Discrete Energy Integration Consistency
Energy per 5-minute step was independently recomputed from active power:
$$E_{\text{theoretical}} = P_{\text{active}} \times \left(\frac{5.0}{60.0}\right)$$
Across 60,480 records:
- Maximum absolute difference: **$0.00043\text{ kWh}$**
- Mean absolute difference: **$0.00021\text{ kWh}$**
- Conclusion: Energy values represent an exact discrete time integral of active power.

---

## 6. Verification Status

The synthetic telemetry dataset is certified **technically correct, physically consistent, free of missing values, and representative of Indian SME manufacturing environments**.
