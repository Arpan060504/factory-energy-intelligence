# Factory Energy Intelligence & Optimization Platform
## Final Cyber-Physical System Architecture

**Document Version:** 1.0 (Frozen Release)  
**Target Beneficiary:** Indian SME Manufacturing Facilities (Automotive, Machining, Forging, Plastics)  
**Standard Compliance:** IEC 61557-12 (Power Metering), ISO 50001 (Energy Management), ISO 10816-3 (Vibration Severity), CEA India Grid Standards  

---

## 1. End-to-End System Architecture Overview

The platform uses a modular, four-tier cyber-physical architecture designed for industrial robustness, offline survivability, and low capital expenditure.

```mermaid
flowchart TD
    subgraph Tier1["TIER 1: PHYSICAL MEASUREMENT & SENSING LAYER"]
        CT["Split-Core CTs (Class 0.5S)"]
        PT["Voltage Taps (415V 3-Phase)"]
        RTD["Surface PT100 RTDs (Temp)"]
        ACC["3-Axis Accelerometers (Vibration)"]
        MTR["3-Phase Multi-Function Smart Meters<br/>(RS485 Modbus RTU, Class 1.0)"]
        
        CT --> MTR
        PT --> MTR
    end

    subgraph Tier2["TIER 2: INDUSTRIAL EDGE COMPUTING LAYER"]
        GW["Industrial DIN-Rail Edge Gateway<br/>(Linux OS, Quad-Core ARM)"]
        MB_POLL["Modbus RTU Polling Engine (5-Min Interval)"]
        VAL["Data Schema & Physical Validation Engine"]
        RING_BUF["Local SQLite Circular Ring Buffer<br/>(45-Day Offline Store-and-Forward)"]
        EDGE_ALERT["Edge Screening Heuristic<br/>(Immediate Overload / Sensor Lost)"]
        
        MTR -- RS485 Shielded Bus --> MB_POLL
        RTD -- 4-20mA / IO --> GW
        ACC -- Modbus / IO --> GW
        MB_POLL --> VAL
        VAL --> RING_BUF
        VAL --> EDGE_ALERT
    end

    subgraph Tier3["TIER 3: CORE ANALYTICS & OPTIMIZATION LAYER"]
        API["FastAPI High-Performance REST Gateway"]
        MQTT_BROKER["Secure MQTT Broker (TLS 1.3)"]
        BASE_ENG["Ridge Regression Energy Baseline Engine<br/>(Production-Normalized R² = 0.985)"]
        DIAG_ENG["Triangulated Physical Diagnostic Engine<br/>(ISO 10816 + NEMA + Joule Law)"]
        OPT_ENG["Three-Tier Production-Protected Optimizer<br/>(Idle + TOD Shifting + Mechanical)"]
        COST_CALC["Time-of-Day Tariff & CO2 Carbon Engine"]
        
        RING_BUF -- TLS / HTTPS / MQTT --> MQTT_BROKER
        MQTT_BROKER --> API
        API --> BASE_ENG
        BASE_ENG --> DIAG_ENG
        DIAG_ENG --> OPT_ENG
        OPT_ENG --> COST_CALC
    end

    subgraph Tier4["TIER 4: ENTERPRISE INTEGRATION & DASHBOARD"]
        DASH["Streamlit Reactive Executive Cockpit<br/>(Demo Mode + 8-Page Engineering Platform)"]
        ERP["Factory ERP / Production Registers<br/>(SAP B1 / Tally / Manual Entry)"]
        PLC["Shopfloor PLC / Compressor Interlock Relay"]
        
        COST_CALC --> DASH
        ERP -- REST JSON / CSV --> BASE_ENG
        OPT_ENG -- Modbus TCP / Dry Contact Relay --> PLC
    end
```

---

## 2. Generic SME Plant Electrical Topology

The electrical single-line diagram (SLD) reflects typical Indian SME distribution (11 kV utility grid stepped down to 415 V via a dedicated distribution transformer). Measurements are captured at the main bus and all feeder levels.

```mermaid
graph TD
    GRID["11 kV UTILITY GRID (MSEDCL / State Discom)"] --> TR["1000 kVA Substation Transformer<br/>(11 kV / 415 V, Vector Dyn11, %Z = 5.0%)"]
    TR --> MTR_MAIN["Meter M00: Main Bus Incomer<br/>(Class 0.5S CT, Class 0.5 Meter)"]
    MTR_MAIN --> BUS["MAIN 415V DISTRIBUTION BUS: BUS_A<br/>(1600A Air Circuit Breaker ACB)"]

    BUS --> FDR1["FDR_01 (100A MCCB)<br/>3.5C 50mm² Cu XLPE (45m)"]
    BUS --> FDR2["FDR_02 (80A MCCB)<br/>3.5C 35mm² Cu XLPE (60m)"]
    BUS --> FDR3["FDR_03 (40A MCCB)<br/>3.5C 16mm² Cu XLPE (35m)"]
    BUS --> FDR4["FDR_04 (63A MCCB)<br/>3.5C 25mm² Cu XLPE (50m)"]
    BUS --> FDR5["FDR_05 (250A MCCB)<br/>3.5C 150mm² Cu XLPE (25m)"]
    BUS --> FDR6["FDR_06 (32A MCCB)<br/>3.5C 10mm² Cu XLPE (70m)"]
    BUS --> FDR7["FDR_07 (40A MCCB)<br/>3.5C 16mm² Cu XLPE (80m)"]

    FDR1 --> MTR1["Meter M01: Digital Meter<br/>+ Vibration + Temp"]
    FDR2 --> MTR2["Meter M02: Digital Meter<br/>+ Vibration"]
    FDR3 --> MTR3["Meter M03: Digital Meter<br/>(Phase Imbalance Alert)"]
    FDR4 --> MTR4["Meter M04: Digital Meter<br/>(Idle Interlock Relay)"]
    FDR5 --> MTR5["Meter M05: Digital Meter<br/>(TOD Batch Shift)"]
    FDR6 --> MTR6["Meter M06: Digital Meter"]
    FDR7 --> MTR7["Meter M07: Digital Meter"]

    MTR1 --> MOT1["MOTOR_01: CNC Machining Center (75 kW)"]
    MTR2 --> MOT2["MOTOR_02: Hydraulic Stamping Press (55 kW)"]
    MTR3 --> PUMP1["PUMP_01: Chilled Water Pump (30 kW)"]
    MTR4 --> COMP1["COMP_01: Rotary Screw Compressor (45 kW)"]
    MTR5 --> FURN1["FURNACE_01: Induction Billet Heater (160 kW)"]
    MTR6 --> LINE1["LINE_01: Assembly & Conveyor (22 kW)"]
    MTR7 --> AUX1["AUX_01: Plant Utilities & Lighting (25 kW)"]

    MOT1 --> PROD["MANUFACTURING PROCESS<br/>(Automotive Transmission Components)"]
    MOT2 --> PROD
    FURN1 --> PROD
    LINE1 --> PROD
    PROD --> OUTPUT["FINISHED PRODUCTION OUTPUT<br/>(131,324.1 Units / Month)"]
```

---

## 3. Physical Architecture & Hardware Specification

| Hardware Subsystem | Component Description | Specifications | Target Vendor / Cost |
| :--- | :--- | :--- | :--- |
| **Energy Sub-Metering** | 3-Phase Multi-Function Meters (Qty: 8) | True RMS V, I, kW, kVA, kVAR, PF, THD, RS485 Modbus RTU, Class 1.0 | Schneider EasyLogic PM2120 / Selec MFM384 (₹6,500/unit) |
| **Current Sensors** | Split-Core CTs (Qty: 24) | Class 0.5S, 100A to 400A primary, 5A secondary, snap-on retrofittable | Rishabh Instruments / Selec (₹850/unit) |
| **Temperature Sensors** | Surface PT100 RTDs (Qty: 4) | Magnetic surface mount, $-50^\circ\text{C}$ to $+200^\circ\text{C}$, 3-wire Class A | Selec / Radix (₹1,500/unit) |
| **Vibration Sensors** | Industrial Piezoelectric Accelerometers (Qty: 4) | 3-axis velocity RMS ($10\text{–}1000\text{ Hz}$), Modbus / analog output, ISO 10816 compliant | IFM Efector / CTC Industrial (₹3,000/unit) |
| **Edge Gateway** | Industrial DIN-Rail Gateway (Qty: 1) | Quad-Core ARM Cortex-A53, 2GB RAM, 16GB eMMC, Dual RS485, GbE, WiFi, Watchdog | Advantech WISE-710 / Waveshare CM4 (₹22,000) |
| **Enclosure & Cabling** | Industrial Control Panel & Wiring | IP65 sheet steel enclosure, 24V DC DIN power supply, shielded twisted-pair Belden 9841 | Rittal / Polycab (₹24,750) |

---

## 4. Edge Computing Architecture (Offline Survivability)

```mermaid
flowchart LR
    subgraph RS485_Bus["RS485 Modbus RTU Daisy-Chain"]
        M1["Meter 1"] --- M2["Meter 2"] --- M3["..."] --- M8["Meter 8"]
    end

    subgraph Edge_Gateway["Industrial Edge Gateway (WISE-710)"]
        DRIVER["Modbus Master Driver (libmodbus / PyModbus)"]
        VAL["Sanity & Range Checker<br/>(V > 300V, I >= 0, NaN Dropped)"]
        PRE["Sensor Loss Pre-Screening<br/>(I_min < 0.5A & I_max > 15A)"]
        SQLITE[("SQLite Ring Buffer<br/>45-Day Retention")]
        SYNC["Sync Daemon (HTTPS / MQTT with Backoff)"]
    end

    RS485_Bus --> DRIVER
    DRIVER --> VAL
    VAL --> PRE
    PRE --> SQLITE
    SQLITE --> SYNC
    SYNC --> CLOUD["Cloud / Central Analytics Service"]
```

### Key Edge Characteristics:
1. **Zero-Data-Loss Store-and-Forward:** Telemetry is written immediately to a local SQLite database with indexing on `timestamp` and `machine_id`. If shopfloor WiFi or 4G LTE disconnects for hours or weeks, the gateway continues sampling and logging uninterrupted.
2. **Schema & Sanity Validation:** Raw ADC counts and Modbus registers are converted to IEEE 754 floats and validated against physical domain bounds:
   - $300\text{ V} \le V_{\text{line}} \le 480\text{ V}$
   - $0.0\text{ A} \le I \le 1200\text{ A}$
   - $0.10 \le \text{PF} \le 1.00$
3. **Sensor Loss Pre-Screening:** Edge rule traps open CT loops or disconnected leads (`DATA_QUALITY_CURRENT_SENSOR_LOST`) locally before corrupted numbers propagate upstream.

---

## 5. Cloud & Central Analytics Architecture

```mermaid
flowchart TD
    subgraph Ingestion["Ingestion Layer"]
        MQTT_IN["MQTT Ingestion Broker (EMQX / Mosquitto TLS)"]
        API_IN["FastAPI HTTP Webhook Receiver"]
    end

    subgraph Storage["Persistent Storage"]
        TS_DB[("PostgreSQL + TimescaleDB<br/>(Time-Series Hypertables)")]
        META_DB[("Metadata Database<br/>(Plant Topology, Asset Limits)")]
    end

    subgraph Microservices["Analytics & Optimization Microservices"]
        CALC_SRV["Electrical & Cable Loss Calculation Service"]
        REG_SRV["Ridge Regression Baseline Trainer & Predictor"]
        ANOM_SRV["Anomaly Scanner & Incident Aggregator"]
        DIAG_SRV["Multi-Variable Diagnostic Triage Engine"]
        OPT_SRV["Constrained Production Optimization Solver"]
    end

    subgraph Presentation["User & API Presentation Layer"]
        ST_APP["Streamlit Interactive Cockpit (Port 8501)"]
        REST_OUT["FastAPI OpenAPI Endpoints (Port 8000)"]
    end

    MQTT_IN --> TS_DB
    API_IN --> TS_DB
    TS_DB --> CALC_SRV
    META_DB --> CALC_SRV
    CALC_SRV --> REG_SRV
    REG_SRV --> ANOM_SRV
    ANOM_SRV --> DIAG_SRV
    DIAG_SRV --> OPT_SRV
    OPT_SRV --> ST_APP
    OPT_SRV --> REST_OUT
```

---

## 6. Enterprise Integration Architecture

The platform provides bidirectional interfaces for existing SME manufacturing software:

```mermaid
sequenceDiagram
    participant ERP as Factory ERP / MES (SAP B1 / Tally)
    participant Platform as Energy Intelligence Platform
    participant PLC as Compressor / Machine PLC
    participant Supervisor as Plant Electrical Supervisor

    ERP->>Platform: Daily Production Count (e.g. 5,251 units / shift)
    Platform->>Platform: Compute Production-Normalized Expected Baseline (Ridge)
    Platform->>Platform: Detect FDR_01 Power Excess (+14.8%) with Zero Throughput Gain
    Platform->>Platform: Synthesize Root Cause (Bearing Wear & Misalignment)
    Platform->>Supervisor: Emit High-Priority SOP Alert (REC-001) via Dashboard & SMS
    Platform->>Platform: Solve Constrained Schedule (Shift Furnace to Night Slot)
    Platform->>PLC: Send Digital Output: Interlock COMP_01 during 13:00 Lunch Break
    Supervisor->>Platform: Acknowledge Bearing Regreasing at 14:00 Handover
    Platform->>Platform: Verify Baseline Restoration & Audit Invariant Production Output
```

### Integration Protocols:
- **ERP Integration:** REST API endpoint `/api/production/batch` accepts JSON payloads containing piece counts, work order numbers, and rejection rates. Fallback: manual CSV upload on the dashboard.
- **SCADA / PLC Interlocking:** Standard Modbus TCP client on the edge gateway connects directly to Allen-Bradley, Siemens S7-1200, or Delta PLCs to actuate compressor unloader solenoids or HVAC chiller setback relays.
- **Maintenance Alerting:** Webhook dispatch to Telegram, WhatsApp Business API, and automated maintenance ticketing systems.
