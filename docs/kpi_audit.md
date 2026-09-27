# Comprehensive Master KPI Audit & Cross-System Reconciliation

## 1. Master KPI Reconciliation Table

This table consolidates every major key performance indicator (KPI) across the **Factory Energy Intelligence & Optimization Platform**, establishing its mathematical definition, underlying telemetry or configuration source, verified value under standard baseline parameters, and its exact presentation location across the Streamlit operational cockpit.

| KPI Metric Name | Primary Source Code | Mathematical Formulation / Derivation | Verified Operational Value | Dashboard Presentation Location | Cross-Page Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Total Active Energy** | `src/energy/analytics.py` & `df["energy_kwh"]` | $E_{\text{total}} = \sum_{i=1}^{N} P_i \times \Delta t$ | **191,138.7 kWh** (30-day baseline) | • Page 1: Executive Cockpit (Top Metric 1)<br>• Page 2: Energy Analytics (Feeder Table Sum)<br>• Page 6: Optimization Studio (Baseline Bar) | **STRICTLY CONSISTENT** (Matches to 1 decimal place across all 3 pages) |
| **Total Production Output** | `df["production_units"]` | $Q_{\text{total}} = \sum_{i=1}^{N} \text{units}_i$ | **131,324.1 units** (30-day total) | • Page 1: Executive Cockpit (Demand sub-panel)<br>• Page 2: Energy Analytics (Summary Table)<br>• Page 6: Before vs After (Invariance Banner) | **STRICTLY INVARIANT** (Baseline = 131,324.1; Optimized = 131,324.1; $\Delta = 0.0$) |
| **Specific Energy Consumption (SEC)** | `src/energy/analytics.py` | $\text{SEC} = \frac{E_{\text{total}}}{Q_{\text{total}}}$ | **1.4555 kWh/unit** (Baseline) | • Page 1: Executive Cockpit (Top Metric 2)<br>• Page 2: Energy Analytics (Summary Table)<br>• Page 6: Before vs After (Baseline Metric) | **STRICTLY CONSISTENT** ($1.4555\text{ kWh/u}$ across all pages) |
| **Optimized SEC** | `src/optimization/optimizer.py` | $\text{SEC}_{\text{opt}} = \frac{E_{\text{opt}}}{Q_{\text{base}}}$ | **1.2120 kWh/unit** (Optimized) | • Page 6: Optimization Studio (Audited Metric 2) | **VERIFIED** |
| **Absolute Energy Reduction** | `src/optimization/optimizer.py` | $\Delta E = E_{\text{base}} - E_{\text{opt}}$ | **31,973.1 kWh** (16.73% reduction) | • Page 1: Executive Cockpit (Delta Tag)<br>• Page 6: Optimization Studio (Metric 1) | **STRICTLY CONSISTENT** |
| **SEC Improvement (%)** | `src/optimization/optimizer.py` | $\Delta\text{SEC}\% = \left(\frac{\text{SEC}_{\text{base}} - \text{SEC}_{\text{opt}}}{\text{SEC}_{\text{base}}}\right) \times 100$ | **16.73 %** | • Page 1: Executive Cockpit (Delta Tag)<br>• Page 6: Optimization Studio (Audited Metric 2) | **STRICTLY CONSISTENT** (Directly calculated from simulation, never hardcoded) |
| **Baseline Electricity Bill** | `src/energy/cost_model.py` | $\sum E_t R_t + \text{Demand} + \text{PF\_Adj}$ | **₹ 19,40,446** (Monthly at ₹5.20/7.80/11.50) | • Page 1: Executive Cockpit (Top Metric 3)<br>• Page 7: Business Model (Sensitivity Base) | **STRICTLY CONSISTENT** |
| **Optimized Electricity Bill** | `src/energy/cost_model.py` | $\sum E_{t,\text{opt}} R_t + \text{Demand}_{\text{opt}} + \text{PF\_Adj}_{\text{opt}}$ | **₹ 15,78,857** (Monthly optimized) | • Page 6: Optimization Studio (Audited Metric 3) | **VERIFIED** |
| **Monthly Cost Savings** | `src/optimization/optimizer.py` | $\Delta\text{Cost} = \text{Bill}_{\text{base}} - \text{Bill}_{\text{opt}}$ | **₹ 361,588** (18.63% savings) | • Page 1: Executive Cockpit (Delta Tag)<br>• Page 6: Optimization Studio (Metric 3)<br>• Page 7: Business Model (Top Metric 3) | **STRICTLY CONSISTENT** (Synchronized reactive variable across all pages) |
| **Recorded Peak Demand** | `df["apparent_power_kva"]` | $\max(S_t)$ across all 5-min intervals | **464.2 kVA** (Utilization: 58.0% of 800 kVA) | • Page 1: Executive Cockpit (Demand Sub-panel)<br>• Page 6: Optimization Studio (Audited Metric 4) | **VERIFIED** |
| **Peak Demand Reduction** | `src/optimization/optimizer.py` | $\Delta S_{\text{peak}} = S_{\text{peak,base}} - S_{\text{peak,opt}}$ | **12.7 kVA** (2.73% peak shaving) | • Page 6: Optimization Studio (Audited Metric 4) | **VERIFIED** |
| **Baseline Scope 2 Emissions** | `src/emissions/carbon.py` | $E_{\text{base}} \times 0.716\text{ kg/kWh} / 1000$ | **136.86 MT CO2** (136,855.3 kg) | • Page 1: Executive Cockpit (Top Metric 4)<br>• Page 6: Optimization Studio | **STRICTLY CONSISTENT** |
| **Avoided CO2 Emissions** | `src/emissions/carbon.py` | $\Delta E_{\text{physical}} \times 0.716 / 1000$ | **22.89 MT CO2** (22,892.7 kg) | • Page 1: Executive Cockpit (Delta Tag)<br>• Page 5: SOP Cumulative Potential<br>• Page 6: Optimization Studio (Metric 5) | **STRICTLY CONSISTENT** |
| **Turnkey Hardware CAPEX** | `docs/business_model.md` & `dashboard/app.py` | 8x Smart Meters + 24x CTs + Gateway + Sensors + Enclosure + Commissioning | **₹ 1,52,150** (~$1,830 USD) | • Page 7: Business Model (Top Metric 1 & BOM Table) | **VERIFIED & AUDITED** |
| **Annual Software OPEX** | `docs/business_model.md` & `dashboard/app.py` | Cloud telemetry + SaaS license + Annual calibration | **₹ 36,000 / yr** (₹ 3,000 / month) | • Page 7: Business Model (Top Metric 2) | **VERIFIED** |
| **Annualized Net Savings** | `dashboard/app.py` | $(\Delta\text{Cost} \times 12) - \text{OPEX}_{\text{annual}}$ | **₹ 43,03,056 / yr** | • Page 7: Business Model (Year 1 Projections) | **VERIFIED** |
| **Simple Payback Period** | `src/config.py` & `dashboard/app.py` | $\frac{\text{CAPEX}}{\text{Net Monthly Savings}} \times 30\text{ days}$ | **13 Days (0.42 Months)** | • Page 7: Business Model (Top Metric 4) | **VERIFIED** (Calculated dynamically, never hardcoded) |

---

## 2. Reconciling Payback: Instantaneous vs. Practical Implementation

The discrepancy between the initial 3–6 month payback rule of thumb in preliminary documentation and the calculated 13-day simple payback is explained as follows:

1. **Calculated Instantaneous Payback (13 Days)**:
   - Evaluates the steady-state scenario where all 3 optimization levers (idle interlocks, TOD furnace shifting, and APFC power factor correction) operate simultaneously across the entire 30-day dataset.
   - On a ₹19.4 Lakh monthly baseline power bill, saving 18.63% yields ₹3.61 Lakhs/month. Dividing the modest ₹1.52 Lakh hardware Capex by ₹3.61 Lakhs/month produces **0.42 months (12.7 days)**.

2. **Practical Real-World SME Rollout (3 to 6 Months)**:
   - In actual shop-floor practice, an SME rolls out interventions in stages:
     - *Month 1*: Passive monitoring and baseline characterization (₹0 savings).
     - *Month 2*: Operator SOP adoption and manual idle shutoffs (50% savings realized).
     - *Months 3–6*: Automated PLC interlocks on compressors and shift rescheduling of induction furnaces.
   - When factoring in phased implementation and conservative 5% to 10% SEC gains (as modeled in the Page 7 Sensitivity Table), the practical payback spans **1.8 to 3.5 months**.

Both figures are fully defensible when properly qualified.
