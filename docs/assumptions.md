# Engineering Assumptions & Mathematical Formulations

This document provides transparent, auditable engineering assumptions, mathematical formulations, and parameters used throughout the **Factory Energy Intelligence & Optimization Platform**.

In accordance with strict engineering honesty, **all models, estimated values, coefficients, and simulated savings are explicitly documented**.

---

## 1. Electrical Engineering Reference Calculations

### 1.1 Balanced Three-Phase Power
For three-phase AC power systems with line-to-line voltage $V_L$ (V) and line current $I_L$ (A):

$$\text{Apparent Power (kVA): } S = \frac{\sqrt{3} \times V_L \times I_L}{1000}$$

$$\text{Active Power (kW): } P = \frac{\sqrt{3} \times V_L \times I_L \times \text{PF}}{1000}$$

$$\text{Reactive Power (kVAR): } Q = \sqrt{S^2 - P^2} = \frac{\sqrt{3} \times V_L \times I_L \times \sin(\arccos(\text{PF}))}{1000}$$

$$\text{Power Factor: } \text{PF} = \frac{P}{S} = \cos(\theta)$$

### 1.2 Discrete Energy Consumption
Energy $E$ (kWh) across discrete observation intervals with step duration $\Delta t$ hours (for 5-minute sampling, $\Delta t = \frac{5}{60} = 0.08333\text{ h}$):

$$E = \sum_{i=1}^{N} P_i \times \Delta t$$

### 1.3 Phase Current Imbalance
Phase current imbalance indicates uneven single-phase loading, loose terminations, or failing motor windings. 

The average phase current is:
$$I_{\text{avg}} = \frac{I_r + I_y + I_b}{3}$$

We use the standard NEMA (National Electrical Manufacturers Association) MG-1 definition:
$$\text{Current Imbalance (\%) } = \frac{\max(|I_r - I_{\text{avg}}|, |I_y - I_{\text{avg}}|, |I_b - I_{\text{avg}}|)}{I_{\text{avg}}} \times 100$$

*Operating Thresholds:*
- Normal: $\le 5\%$
- Warning (Investigation recommended): $5\% < \text{Imbalance} \le 10\%$
- Critical (Motor derating or shutdown required to avoid winding insulation breakdown): $> 10\%$

### 1.4 Feeder Cable Loss Estimation
Cable losses are Joule heating losses ($I^2R$) along the distribution run from the main bus to the machine terminal.

$$P_{\text{loss}} (\text{kW}) = \frac{3 \times I_{\text{avg}}^2 \times R_{\text{cable}}}{1000}$$

Where the single-conductor resistance $R_{\text{cable}}$ is:
$$R_{\text{cable}} = \rho_{T} \times \frac{L}{A}$$

**Conductor Parameters (Explicit Model Settings):**
- Conductor Material: Aluminium (standard industrial armored XLPE cables in Indian distribution) or Copper
- Base Resistivity at $20^\circ\text{C}$:
  - Aluminium: $\rho_{20} = 0.0282\ \Omega\cdot\text{mm}^2/\text{m}$
  - Copper: $\rho_{20} = 0.0175\ \Omega\cdot\text{mm}^2/\text{m}$
- Temperature Coefficient ($\alpha$):
  - Aluminium: $\alpha = 0.00403\ /^\circ\text{C}$
  - Copper: $\alpha = 0.00393\ /^\circ\text{C}$
- Operating Conductor Temperature Assumption: $T_{\text{op}} = 50^\circ\text{C}$ (calibrated against ambient temperature):
  $$\rho_{50} = \rho_{20} \times [1 + \alpha(50 - 20)] \approx 0.0316\ \Omega\cdot\text{mm}^2/\text{m}\text{ (Aluminium)}$$

> [!IMPORTANT]
> **Labeling Notice**: Cable losses computed in this platform are **estimated theoretical calculations** based on nameplate cable geometry ($L, A$) and measured current $I$. They are never represented as directly measured sensor losses.

---

## 2. Core Manufacturing KPI: Specific Energy Consumption (SEC)

The primary energy productivity metric across Indian industrial SMEs is **Specific Energy Consumption**:

$$\text{SEC} = \frac{\text{Total Active Energy Consumed (kWh)}}{\text{Total Good Production Output (Units)}}$$

$$\text{Units: } \text{kWh / unit produced (or kWh / ton)}$$

### 2.1 Baseline vs. Optimized SEC Comparison
To prevent false claims of energy savings achieved by simply idling machines or reducing throughput, all optimization interventions must enforce production invariance or improvement:

$$\text{Production Constraint: } \text{Production}_{\text{optimized}} \ge \text{Production}_{\text{baseline}}$$

$$\text{SEC Improvement (\%) } = \left( \frac{\text{SEC}_{\text{baseline}} - \text{SEC}_{\text{optimized}}}{\text{SEC}_{\text{baseline}}} \right) \times 100$$

$$\text{Absolute Energy Reduction (kWh) } = E_{\text{baseline}} - E_{\text{optimized}}$$

---

## 3. Energy Baseline Model

Rather than black-box neural networks that cannot be audited by SME plant engineers, the platform implements an **Explainable Production-Normalized Baseline Model**:

$$P_{\text{expected}}(t) = P_{\text{standby}} + \beta_1 \cdot \text{State}(t) + \beta_2 \cdot \text{ProductionRate}(t) + \epsilon$$

Where:
- $P_{\text{standby}}$: Measured fixed baseline power when machine is energized but not processing (auxiliaries, hydraulics, electronics)
- $\beta_1$: Active machine operational offset
- $\beta_2$: Incremental power coefficient per unit produced per hour
- Rolling Baseline: Rolling 7-day median filter during verified healthy periods to track seasonal and operational drift.

**Energy Deviation:**
$$\Delta P (t) = P_{\text{actual}}(t) - P_{\text{expected}}(t)$$
$$\text{Deviation (\%) } = \left( \frac{P_{\text{actual}}(t) - P_{\text{expected}}(t)}{P_{\text{expected}}(t)} \right) \times 100$$

---

## 4. Machine Health Score Formulation

The health index provides early warning of electro-mechanical deterioration.

> [!WARNING]
> **Transparency Declaration**: The Machine Health Score is an **algorithmic composite heuristic** calibrated from physical deviation indicators. It is not an OEM-certified remaining useful life (RUL) prediction.

$$\text{Health Score} = 100 - \left( w_I \cdot D_I + w_P \cdot D_P + w_T \cdot D_T + w_V \cdot D_V + w_{\text{imb}} \cdot D_{\text{imb}} \right)$$

Where each component penalty $D_x$ is normalized between 0 and 100:
- $D_I$: Current deviation beyond rated baseline
- $D_P$: Active power excess above expected production baseline
- $D_T$: Surface temperature rise above ambient ($\Delta T = T_{\text{equip}} - T_{\text{ambient}}$ exceeding $25^\circ\text{C}$)
- $D_V$: Vibration RMS deviation above baseline nominal ($> 2.8\text{ mm/s}$ based on ISO 10816-3 Class II medium machines)
- $D_{\text{imb}}$: Current imbalance penalty

Weights: $w_I = 0.20, w_P = 0.25, w_T = 0.25, w_V = 0.20, w_{\text{imb}} = 0.10$.

**Classification:**
- **HEALTHY (Normal)**: Score $\ge 80$
- **WARNING (Degradation Suspected)**: $60 \le \text{Score} < 80$
- **CRITICAL (Inspection Required)**: Score $< 60$

---

## 5. Industrial Tariff Model (Time of Day - TOD)

Based on typical Indian State Electricity Regulatory Commission (e.g., MSEDCL, BESCOM, UGVCL, TANGEDCO) industrial HT-2 tariffs:

| Tariff Slot | Hours (24-hr format) | Active Energy Charge (₹ / kWh) | Description |
|---|---|---|---|
| **Off-Peak (Night)** | 22:00 - 06:00 (8 hrs) | ₹ 5.20 | Night incentive zone |
| **Normal (Day)** | 06:00 - 18:00 (12 hrs) | ₹ 7.80 | Standard working day rate |
| **Peak (Evening)** | 18:00 - 22:00 (4 hrs) | ₹ 11.50 | High grid stress surcharge |

**Contract Demand & Penalty:**
- Contract Demand: $800\text{ kVA}$
- Demand Charge: ₹ 375 / kVA / month (billed on max demand or 85% of contract demand, whichever is higher)
- Low Power Factor Penalty: Surcharge of $1.5\%$ on total bill for every $0.01$ drop below $0.90\text{ lag}$.
- High Power Factor Incentive: Credit of $0.5\%$ on energy charges for maintaining $\text{PF} > 0.95$.

---

## 6. Carbon Emissions Baseline

Based on the **Central Electricity Authority (CEA), Government of India - CO2 Baseline Database for the Indian Power Sector (Version 19.0)**:

$$\text{Grid Emission Factor } = 0.716\text{ kg CO}_2\text{ / kWh}$$

$$\text{Carbon Emissions (kg CO}_2) = \text{Active Energy (kWh)} \times 0.716$$

$$\text{Emissions in Metric Tonnes: } \text{MT CO}_2 = \frac{\text{Emissions (kg)}}{1000}$$

---

## 7. SME Hardware BOM & Financial Assumptions

| Item | Component | Quantity | Unit Cost (₹) | Total Cost (₹) |
|---|---|---|---|---|
| 1 | 3-Phase Multi-Function Smart Meters (RS-485 Modbus) | 8 | ₹ 6,500 | ₹ 52,000 |
| 2 | Split-core Current Transformers (CTs) Class 0.5S | 24 | ₹ 850 | ₹ 20,400 |
| 3 | Industrial Edge Gateway (Quad-core, RS485, DIN rail) | 1 | ₹ 22,000 | ₹ 22,000 |
| 4 | Surface Temp (PT100) & Vibration Sensors | 4 | ₹ 4,500 | ₹ 18,000 |
| 5 | Installation, Cabling, Control Panel Enclosure | Lump | ₹ 25,000 | ₹ 25,000 |
| 6 | Commissioning & Baseline Calibration | Lump | ₹ 15,000 | ₹ 15,000 |
| **Total Capex** | | | | **₹ 1,52,400** (~$1,850 USD) |

- Annual Software SaaS & Support Subscription: ₹ 36,000 / year (₹ 3,000 / month)
- Projected Simple Payback Period: **3 to 6 months** (demonstrated in Business Model).
