# Factory Energy Intelligence & Optimization Platform - System Architecture

## 1. Executive Summary & Vision

The **Factory Energy Intelligence & Optimization Platform** is an industrial-grade energy analytics, diagnostics, and process optimization system tailored specifically for Indian Small and Medium-sized Enterprises (SMEs). 

Indian manufacturing SMEs operate under tight margins, high Time-of-Day (TOD) industrial tariffs (₹5.00 to ₹12.00+ / kWh), grid voltage fluctuations, and strict production delivery deadlines. Most energy tools in the market are either expensive enterprise EMS suites requiring dedicated energy managers or generic IoT dashboards displaying raw current and kWh without actionable engineering recommendations.

This platform bridges that gap by implementing an automated 7-step engineering intelligence chain:

```mermaid
flowchart TD
    M["1. MEASURE (Sub-metering, CTs, V, I, PF, Edge Gateway)"] --> U["2. UNDERSTAND (Power Flow, Baseline, SEC Modeling)"]
    U --> D["3. DETECT (Rules, Rolling Deviations, Outlier Z-Scores)"]
    D --> DIAG["4. DIAGNOSE (Root Cause Analysis: Motor, Idle, Imbalance)"]
    DIAG --> R["5. RECOMMEND (Specific SOP & Corrective Actions)"]
    R --> O["6. OPTIMIZE (Idle Reduction, TOD Tariff Load Shifting)"]
    O --> V["7. VERIFY SAVINGS (Before vs. After SEC & Throughput Audit)"]
```

The platform continuously answers the **Five Core SME Questions**:
1. **WHERE** is electrical energy being consumed? (Feeder/machine level disaggregation)
2. **IS** the consumption normal or abnormal? (Production-adjusted baseline comparison)
3. **WHY** is abnormal consumption occurring? (Root cause diagnostics: idle run, phase unbalance, degradation)
4. **WHAT** action should the plant engineer/operator take? (Contextual, quantified recommendations)
5. **DID** the action actually reduce Specific Energy Consumption (SEC) without degrading production throughput? (Rigorous before/after verification)

---

## 2. Factory Electrical Single-Line Topology

The generic Indian SME manufacturing facility (e.g., auto-component machining & heat treatment plant) receives power at 11 kV from the state distribution utility (DISCOM), stepped down to 415 V via a 1000 kVA distribution transformer.

```mermaid
flowchart TD
    Grid["11 kV Utility Grid (DISCOM)"] --> Incomer["11 kV Substation Incomer / VCB"]
    Incomer --> TR["Distribution Transformer TR_01 (11 kV / 415 V, 1000 kVA, Dyn11)"]
    TR --> MDB["Main 415V Low Voltage Bus (BUS_A) - 1600A Air Circuit Breaker"]
    
    MDB --> F01["Feeder FDR_01: CNC Machining Center (MOTOR_01, 75 kW)"]
    MDB --> F02["Feeder FDR_02: Hydraulic Stamping Press (MOTOR_02, 55 kW)"]
    MDB --> F03["Feeder FDR_03: Chilled Water Circulation Pump (PUMP_01, 30 kW)"]
    MDB --> F04["Feeder FDR_04: Screw Air Compressor (COMP_01, 45 kW)"]
    MDB --> F05["Feeder FDR_05: Induction Billet Heater / Furnace (FURNACE_01, 160 kW)"]
    MDB --> F06["Feeder FDR_06: Conveyor & Final Assembly Line (LINE_01, 22 kW)"]
    MDB --> F07["Feeder FDR_07: Auxiliary Plant Utilities & Lighting (AUX_01, 25 kW)"]
    MDB --> APFC["Feeder FDR_08: APFC Capacitor Bank (250 kVAR Automatic Bank)"]
```

---

## 3. End-to-End Data Pipeline Architecture

```mermaid
flowchart LR
    subgraph Floor["Shop Floor & Field Sensors"]
        Meters["Digital Multifunction Meters (MFMs) + CTs"]
        VibTemp["Vibration & Surface Temp Sensors"]
        PLC["PLC Cycle / Part Counters"]
    end

    subgraph Edge["Affordable Edge Gateway (Raspberry Pi / Industrial PC)"]
        Modbus["RS-485 Modbus RTU / TCP Master"]
        LocalBuffer["Local SQLite Buffer & Circular Cache"]
        EdgeRules["Edge Anomaly Detection & L1 Health Engine"]
    end

    subgraph Backend["Central Processing & Analytics Service"]
        Ingest["Data Ingestion & Integrity Validation API"]
        BaselineEngine["Energy Baseline & SEC Engine"]
        DiagEngine["Rule & Statistical Diagnostics Engine"]
        OptEngine["Idle & TOU Scheduling Optimizer"]
    end

    subgraph Presentation["User Touchpoints"]
        UI["Streamlit Interactive Operations Dashboard"]
        RestAPI["FastAPI REST Endpoints"]
        Alerts["Operator Notification Stream"]
    end

    Meters -->|RS-485 / Modbus| Modbus
    VibTemp -->|4-20mA / IO-Link| Modbus
    PLC -->|Digital Pulse / MQTT| Modbus
    Modbus --> LocalBuffer
    LocalBuffer --> EdgeRules
    LocalBuffer -->|Store & Forward (MQTT/HTTPS)| Ingest
    Ingest --> BaselineEngine
    Ingest --> DiagEngine
    BaselineEngine --> OptEngine
    DiagEngine --> UI
    OptEngine --> UI
    Ingest --> RestAPI
    DiagEngine --> Alerts
```

---

## 4. Edge-Computing Resilience for Indian SME Environments

Many SME manufacturing clusters in India (e.g., Peenya, Bhosari, Sanand, Ambattur) experience periodic broadband outages and electrical transients. The architecture incorporates:

1. **Store-and-Forward SQLite Buffer**: High-frequency 5-minute electrical telemetry is buffered locally on flash storage (up to 30 days retention).
2. **Local Anomaly Screening**: Safety-critical thresholds (current imbalance >15%, phase loss, extreme power factor dip <0.75, thermal limit exceedance) trigger immediate edge audio-visual alerts without cloud dependency.
3. **Resilient Synchronization**: Upon network restoration, data is batched, compressed, and synchronized with deduplication guarantees.

```mermaid
sequenceDiagram
    participant M as Field MFM Meter
    participant E as Edge Gateway Buffer
    participant D as Edge Rule Engine
    participant C as Central Server

    M->>E: Polled readings every 5 min (V, I, PF, kW, kWh)
    E->>D: Stream instantaneous reading
    alt Imbalance > 15% or Severe Dip
        D->>E: Trigger Local Relay / Edge Alert
    end
    alt Network Online
        E->>C: Push batch JSON payload
        C-->>E: Acknowledge sync (commit cursor)
    else Network Offline
        E->>E: Retain in SQLite local backlog
        Note over E: Normal plant operations unaffected
    end
```

---

## 5. Analytics & Diagnostics Workflow

The analytics engine processes discrete synchronized intervals ($\Delta t = 5\text{ min} = 0.0833\text{ hr}$):

```mermaid
flowchart TD
    Raw["Raw Synchronized Telemetry"] --> Val["Data Integrity & Range Check"]
    Val --> Physics["Three-Phase Electrical Calculations (P, Q, S, PF, Imbalance, Cable Loss)"]
    Physics --> Agg["Aggregations (Hourly, Daily, Machine, Feeder, Substation)"]
    
    Agg --> Base["Production-Normalized Baseline Model: Expected_kW = f(State, Rate, Prod)"]
    Base --> Dev["Deviation Calculation: Actual_kW - Expected_kW, SEC = kWh / Units"]
    
    Dev --> RuleCheck{"Condition Rule Checks"}
    RuleCheck -->|P > Expected and Prod const| Anom1["Motor Mechanical Degradation Alert"]
    RuleCheck -->|P > Standby and Prod = 0| Anom2["Compressor / Machine Idle Energy Alert"]
    RuleCheck -->|PF < 0.85| Anom3["Low Power Factor / Tariff Penalty Alert"]
    RuleCheck -->|I_unbalance > 8%| Anom4["Three-Phase Current Imbalance Alert"]
    
    Anom1 --> Diag["Diagnostic Engine: Root Cause + Severity (Normal, Warning, Critical)"]
    Anom2 --> Diag
    Anom3 --> Diag
    Anom4 --> Diag
    
    Diag --> Rec["Recommendation Engine: Actionable SOP + Quantified Savings (₹, kWh, CO2)"]
```

---

## 6. Optimization Workflow

```mermaid
flowchart TD
    subgraph Inputs
        BasePlan["Baseline Production Plan & Shift Schedule"]
        TOU["State DISCOM TOU Tariff Structure (Peak, Normal, Off-Peak)"]
        IdleLog["Detected Idle Energy Profiles & Machine Dependencies"]
    end

    subgraph Optimization
        A["1. Idle Energy Elimination: Auto-standby & Interlocking"]
        B["2. Flexible Load Shifting: Move batch thermal/pumping loads out of Peak window"]
        C["3. Peak Shaving: Flatten coincident maximum demand (kVA)"]
    end

    subgraph Constraints
        C1["Production Quota Requirement (Units >= Target)"]
        C2["Process Sequence Dependencies (Furnace -> Press -> Machining)"]
        C3["Worker Shift Windows & Maximum Machine Capacity"]
    end

    Inputs --> Optimization
    Constraints -.-> Optimization
    Optimization --> Eval["Rigorous Before/After Simulation"]
    Eval --> Verified["Audited Metrics: Energy (kWh), SEC (kWh/unit), Cost (₹), Demand (kVA), CO2 (kg)"]
```

---

## 7. Deployment Architecture (Scalability Path)

The deployment model scales gracefully from single-machine trial to enterprise multi-site operations:

* **Stage 1 (Single Production Cell Pilot)**: 1 Gateway, 5 Meters, local dashboard. Validates sensor accuracy and demonstrates quick-win idle savings within 14 days.
* **Stage 2 (Single Factory Deployment)**: 15-30 Meters across all feeders, full MDB monitoring, local edge server running FastAPI + SQLite + Streamlit.
* **Stage 3 (Multi-Site SME Cluster)**: Centralized cloud database (PostgreSQL/TimescaleDB), multi-tenant plant benchmarking, cross-facility SEC leaderboards.
