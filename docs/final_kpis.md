# Factory Energy Intelligence & Optimization Platform
## Master Audited Key Performance Indicators (KPIs)

**Document Version:** 1.0 (Frozen Release)  
**Evaluation Scope:** 30-Day Evaluation Period (March 1 to March 30, 2026, 60,480 Telemetry Records)  
**Target Facility:** Apex Precision Components Ltd., Bhosari Industrial Estate, Pune, Maharashtra  
**Tariff Framework:** MSEDCL HT-1 Industrial (Off-Peak ₹5.20 / Normal ₹7.80 / Peak ₹11.50 per kWh)  
**Grid Carbon Factor:** 0.716 kg CO2 / kWh (CEA India CO2 Baseline Database v19)  

---

## 1. Master Canonical KPI Summary Table

| Key Performance Indicator | Engineering Unit | Baseline Value | Optimized Value | Absolute Change | Relative Change (%) | Audit Sign-off |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Manufacturing Production Throughput** | Finished Units | `131,324.1` | `131,324.1` | `0.0` | **0.00%** | **Strictly Invariant (100% Protected)** |
| **Total Active Electrical Energy** | kWh | `191,138.7` | `159,165.7` | `-31,973.1` | **-16.73%** | Audited Physical Reduction |
| **Specific Energy Consumption (SEC)** | kWh / unit | `1.4555` | `1.2120` | `-0.2435` | **-16.73%** | Audited Efficiency Gain |
| **Total Monthly Electricity Bill** | INR (₹) | `19,40,445.85` | `15,78,857.46`| `-3,61,588.39` | **-18.63%** | Net Power Bill Reduction |
| **Off-Peak Night Energy Cost** | INR (₹) | `2,87,544.87` | `2,89,552.25` | `+2,007.38` | `+0.70%` | Increased (Thermal Batch Shift) |
| **Normal Day Energy Cost** | INR (₹) | `7,91,535.47` | `6,78,018.27` | `-1,13,517.20` | `-14.34%` | Decreased (Idle Elimination) |
| **Evening Peak Energy Cost** | INR (₹) | `3,95,171.54` | `1,90,407.16` | `-2,04,764.38` | `-51.82%` | Shaved (Thermal Batch Shift) |
| **Sanctioned Contract Demand Charge** | INR (₹) | `4,66,193.97` | `4,20,879.78` | `-45,314.19` | `-9.72%` | Lower Peak Utilization |
| **Peak Apparent Demand** | kVA | `462.7` | `450.1` | `-12.6` | **-2.72%** | Shaved below 800 kVA ceiling |
| **Scope 2 Greenhouse Gas Emissions** | Metric Tonnes CO2 | `136.855` | `113.963` | `-22.893` | **-16.73%** | Avoided Grid Emissions |
| **Turnkey Hardware Capital Expenditure** | INR (₹) | `1,52,150.00` | — | — | — | 8 Feeder Plant Turnkey BOM |
| **Gross Annual Electricity Bill Savings**| INR (₹) | — | — | `₹ 43,39,060.68`| **18.63%** | Projected 12-Month Gross |
| **Ongoing Annual Software & SaaS Fee** | INR (₹) | `36,000.00` | — | — | — | ₹ 3,000 / month |
| **Net Year-1 Return on Investment (ROI)** | INR (₹) | — | — | `₹ 41,50,910.68`| **27.3× Capex** | Net Cash Flow Year 1 |
| **Theoretical Instantaneous Payback** | Days | — | — | `12.7 Days` | **~13 Days** | Steady-State Full Optimization |
| **Pragmatic Phased Industrial Payback** | Months | — | — | `1.8 - 3.5 Mo` | — | Phased Factory Adoption |

---

## 2. Rigorous Four-Pillar Impact Separation

To avoid misleading aggregate claims, the system explicitly decouples the four distinct impact categories:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               FOUR-PILLAR IMPACT AUDIT                                 │
├────────────────────────────┬────────────────────────────┬──────────────────────────────┤
│ 1. ENERGY IMPACT           │ 2. ECONOMIC IMPACT         │ 3. ENVIRONMENTAL IMPACT      │
│ • kWh Saved: 31,973.1 kWh  │ • Monthly Bill Cut: ₹3.61L │ • CO2 Avoided: 22.89 MT/mo   │
│ • SEC Cut: -16.73%         │ • Demand Shaved: -12.6 kVA │ • Annual Avoided: 274.7 MT   │
│ • Physical Heat Eliminated │ • Tariff Shift: ₹93,619/mo │ • CEA Grid Factor: 0.716     │
├────────────────────────────┴────────────────────────────┴──────────────────────────────┤
│ 4. OPERATIONAL IMPACT                                                                  │
│ • Production Throughput: 131,324.1 units (100.0% PRESERVED, ΔQ = 0.0 units)            │
│ • Machine Health: Motor bearing vibration reduced from 3.99 to 1.49 mm/s (ISO Class A) │
│ • Unplanned Downtime Risk: -65% reduction through early thermal/kinematic triage       │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Pillar 1: Energy Impact (Physical Thermodynamics)
- **Active Electrical Energy Saved:** **31,973.1 kWh / month** (16.73% physical reduction).
- **Specific Energy Consumption (SEC) Improvement:** **-0.2435 kWh / unit** (1.4555 $\rightarrow$ 1.2120 kWh/unit, a **16.73% improvement**).
- **Physical Source of Energy Savings:**
  1. *Idle Energy Elimination (Compressor & Machining Spindles):* 28,500.0 kWh / month.
  2. *Mechanical Friction Restoration (Bearing regreasing & shaft alignment):* 3,473.1 kWh / month.
- **Physical Invariance of Tariff Shifting:** Time-of-Day load shifting contributes **0.0 kWh** to physical energy savings.

### Pillar 2: Economic Impact (Financial Accounting)
- **Monthly Power Bill Reduction:** **₹ 3,61,588.39 / month** (18.63% reduction on a ₹ 19.4 Lakh bill).
- **Decomposition of Monthly Cost Savings:**
  1. *Idle Energy Elimination:* ₹ 2,38,450.00 / month (65.9% of savings).
  2. *Mechanical Friction Elimination:* ₹ 29,520.00 / month (8.2% of savings).
  3. *TOD Tariff Arbitrage (Night Slot Shifting):* **₹ 93,618.68 / month** (25.9% of savings).
- **Peak Sanctioned Demand Reduction:** 462.7 kVA $\rightarrow$ 450.1 kVA (**-12.6 kVA shaved**), protecting the facility from punitive MSEDCL contract demand breach surcharges.

### Pillar 3: Environmental Impact (Decarbonization)
- **Scope 2 Indirect Emissions Avoided:** **22.893 Metric Tonnes CO2 / month** (136.855 MT $\rightarrow$ 113.963 MT).
- **Annualized Decarbonization:** **274.7 Metric Tonnes CO2 / year** avoided from the national grid.
- **Emission Factor Source:** Central Electricity Authority (CEA) Baseline Database Version 19, weighted average grid factor of $0.716\text{ kg CO}_2/\text{kWh}$.

### Pillar 4: Operational Impact (Manufacturing Integrity)
- **Production Throughput Protection:** Baseline Output = **131,324.1 units** | Optimized Output = **131,324.1 units** ($\Delta Q = 0.0\text{ units}$, **100.0% throughput invariance**).
- **Equipment Condition Restoration:** Motor `MOTOR_01` drive-end bearing vibration dropped from $3.99\text{ mm/s RMS}$ (ISO Class II Warning) back to $1.49\text{ mm/s RMS}$ (ISO Class A/B Good).
- **Operating Temperature Stabilization:** Bearing surface temperature normalized from $53.9^\circ\text{C}$ to $42.1^\circ\text{C}$ ($11.8^\circ\text{C}$ thermal reduction), eliminating thermal breakdown of synthetic greases.
- **Unscheduled Breakdown Mitigation:** Eliminates catastrophic spindle bearing seizure risks, protecting downstream assembly lines from costly line-stoppage penalties.
