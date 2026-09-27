import os
import subprocess

os.makedirs("docs/diagrams", exist_ok=True)

dot_physical = """digraph PhysicalArchitecture {
    graph [
        rankdir="TB",
        nodesep=0.35,
        ranksep=0.45,
        bgcolor="white",
        dpi=300,
        fontname="Arial",
        compound=true,
        pad="0.5,0.5"
    ];
    
    node [
        fontname="Arial",
        fontsize=11,
        shape="box",
        style="filled,rounded",
        margin="0.25,0.18",
        penwidth=1.5
    ];
    
    edge [
        fontname="Arial",
        fontsize=10,
        color="#2B6CB0",
        penwidth=1.6,
        arrowsize=0.85
    ];

    // Title Block
    subgraph cluster_title {
        style="invis";
        TITLE [
            label=<<B><FONT POINT-SIZE="16" COLOR="#1A365D">Physical Plant &amp; Electrical Single-Line Architecture</FONT></B><BR/><FONT POINT-SIZE="11" COLOR="#4A5568">Illustrative Canonical SME Factory Configuration (Reference Plant Simulation) &bull; Apex Precision Components Ltd.</FONT>>,
            shape="plaintext",
            style="none"
        ];
    }

    // Grid & Incomer Hierarchy
    GRID [
        label=<<B>11 kV Utility Grid</B><BR/><FONT POINT-SIZE="10" COLOR="#2D3748">3-Phase 50 Hz &bull; MSEDCL HT-1 Incomer</FONT>>,
        fillcolor="#EBF8FF",
        color="#3182CE"
    ];

    TR [
        label=<<B>1000 kVA Substation Transformer</B><BR/><FONT POINT-SIZE="10" COLOR="#2D3748">11 kV / 415 V &bull; Dyn11 &bull; 800 kVA Contracted Demand Cap</FONT>>,
        fillcolor="#FEFCBF",
        color="#D69E2E"
    ];

    M00 [
        label=<<B>Meter M00: Main Bus Incomer</B><BR/><FONT POINT-SIZE="10" COLOR="#2D3748">Class 0.5S &bull; 3 &times; CTs 1600/5A &bull; Modbus RS-485</FONT>>,
        fillcolor="#E6FFFA",
        color="#319795"
    ];

    BUS [
        label=<<B><FONT POINT-SIZE="13">Main 415 V Distribution Bus (BUS_A) &bull; 1600 A Air Circuit Breaker (ACB)</FONT></B>>,
        shape="box",
        style="filled",
        fillcolor="#2D3748",
        fontcolor="white",
        color="#1A202C",
        width=11.5,
        height=0.45
    ];

    TITLE -> GRID [style="invis"];
    GRID -> TR;
    TR -> M00;
    M00 -> BUS [penwidth=2.5, color="#1A202C"];

    // Feeders Subgraph
    subgraph cluster_feeders {
        style="dashed";
        color="#CBD5E0";
        bgcolor="#F7FAFC";
        label=<<B><FONT POINT-SIZE="12" COLOR="#2D3748">Shop Floor Sub-Distribution &amp; Sub-Metering Layer (Tier-2 Turnkey Instrumentation)</FONT></B>>;
        margin=16;

        // Feeders
        FDR01 [label=<<B>Feeder FDR_01</B><BR/><FONT POINT-SIZE="9.5" COLOR="#4A5568">100A MCCB<br/>50 mm&#178; Cu XLPE (45m)</FONT>>, fillcolor="#EDF2F7", color="#A0AEC0"];
        FDR02 [label=<<B>Feeder FDR_02</B><BR/><FONT POINT-SIZE="9.5" COLOR="#4A5568">80A MCCB<br/>35 mm&#178; Cu XLPE (60m)</FONT>>, fillcolor="#EDF2F7", color="#A0AEC0"];
        FDR03 [label=<<B>Feeder FDR_03</B><BR/><FONT POINT-SIZE="9.5" COLOR="#4A5568">40A MCCB<br/>16 mm&#178; Cu XLPE (35m)</FONT>>, fillcolor="#EDF2F7", color="#A0AEC0"];
        FDR04 [label=<<B>Feeder FDR_04</B><BR/><FONT POINT-SIZE="9.5" COLOR="#4A5568">63A MCCB<br/>25 mm&#178; Cu XLPE (50m)</FONT>>, fillcolor="#EDF2F7", color="#A0AEC0"];
        FDR05 [label=<<B>Feeder FDR_05</B><BR/><FONT POINT-SIZE="9.5" COLOR="#4A5568">250A MCCB<br/>150 mm&#178; Cu XLPE (25m)</FONT>>, fillcolor="#EDF2F7", color="#A0AEC0"];
        FDR06 [label=<<B>Feeder FDR_06</B><BR/><FONT POINT-SIZE="9.5" COLOR="#4A5568">32A MCCB<br/>10 mm&#178; Cu XLPE (70m)</FONT>>, fillcolor="#EDF2F7", color="#A0AEC0"];
        FDR07 [label=<<B>Feeder FDR_07</B><BR/><FONT POINT-SIZE="9.5" COLOR="#4A5568">40A MCCB<br/>16 mm&#178; Cu XLPE (80m)</FONT>>, fillcolor="#EDF2F7", color="#A0AEC0"];

        // Meters
        M01 [label=<<B>Meter M01</B><BR/><FONT POINT-SIZE="9.5" COLOR="#234E52">3 &times; CTs 200/5A<br/>Temp T1 + Vib V1</FONT>>, fillcolor="#E6FFFA", color="#319795"];
        M02 [label=<<B>Meter M02</B><BR/><FONT POINT-SIZE="9.5" COLOR="#234E52">3 &times; CTs 150/5A<br/>Vibration V2</FONT>>, fillcolor="#E6FFFA", color="#319795"];
        M03 [label=<<B>Meter M03</B><BR/><FONT POINT-SIZE="9.5" COLOR="#234E52">3 &times; CTs 100/5A<br/>Class 1.0</FONT>>, fillcolor="#E6FFFA", color="#319795"];
        M04 [label=<<B>Meter M04</B><BR/><FONT POINT-SIZE="9.5" COLOR="#234E52">3 &times; CTs 150/5A<br/>Class 1.0</FONT>>, fillcolor="#E6FFFA", color="#319795"];
        M05 [label=<<B>Meter M05</B><BR/><FONT POINT-SIZE="9.5" COLOR="#234E52">3 &times; CTs 400/5A<br/>Temp T2</FONT>>, fillcolor="#E6FFFA", color="#319795"];
        M06 [label=<<B>Meter M06</B><BR/><FONT POINT-SIZE="9.5" COLOR="#234E52">3 &times; CTs 100/5A<br/>Class 1.0</FONT>>, fillcolor="#E6FFFA", color="#319795"];
        M07 [label=<<B>Meter M07</B><BR/><FONT POINT-SIZE="9.5" COLOR="#234E52">3 &times; CTs 100/5A<br/>Class 1.0</FONT>>, fillcolor="#E6FFFA", color="#319795"];

        // Equipment
        EQ01 [label=<<B>CNC Machining Center</B><BR/><FONT POINT-SIZE="9.5" COLOR="#1A365D">MOTOR_01 &bull; 75 kW</FONT>>, fillcolor="#EBF8FF", color="#3182CE"];
        EQ02 [label=<<B>Hydraulic Stamping Press</B><BR/><FONT POINT-SIZE="9.5" COLOR="#1A365D">MOTOR_02 &bull; 55 kW</FONT>>, fillcolor="#EBF8FF", color="#3182CE"];
        EQ03 [label=<<B>Chilled Water Pump</B><BR/><FONT POINT-SIZE="9.5" COLOR="#1A365D">PUMP_01 &bull; 30 kW</FONT>>, fillcolor="#EDF2F7", color="#4A5568"];
        EQ04 [label=<<B>Rotary Screw Compressor</B><BR/><FONT POINT-SIZE="9.5" COLOR="#1A365D">COMP_01 &bull; 45 kW</FONT>>, fillcolor="#EDF2F7", color="#4A5568"];
        EQ05 [label=<<B>Induction Billet Furnace</B><BR/><FONT POINT-SIZE="9.5" COLOR="#1A365D">FURNACE_01 &bull; 160 kW</FONT>>, fillcolor="#FEEBC8", color="#DD6B20"];
        EQ06 [label=<<B>Conveyor &amp; Assembly Line</B><BR/><FONT POINT-SIZE="9.5" COLOR="#1A365D">LINE_01 &bull; 22 kW</FONT>>, fillcolor="#EBF8FF", color="#3182CE"];
        EQ07 [label=<<B>Plant Utilities &amp; Lighting</B><BR/><FONT POINT-SIZE="9.5" COLOR="#1A365D">AUX_01 &bull; 25 kW</FONT>>, fillcolor="#EDF2F7", color="#4A5568"];
    }

    // Bus to Feeders
    BUS -> FDR01;
    BUS -> FDR02;
    BUS -> FDR03;
    BUS -> FDR04;
    BUS -> FDR05;
    BUS -> FDR06;
    BUS -> FDR07;

    // Feeders to Meters
    FDR01 -> M01;
    FDR02 -> M02;
    FDR03 -> M03;
    FDR04 -> M04;
    FDR05 -> M05;
    FDR06 -> M06;
    FDR07 -> M07;

    // Meters to Equipment
    M01 -> EQ01;
    M02 -> EQ02;
    M03 -> EQ03;
    M04 -> EQ04;
    M05 -> EQ05;
    M06 -> EQ06;
    M07 -> EQ07;

    // Process & Output Convergence
    PROC [
        label=<<B>Factory Manufacturing Process &bull; Transmission Components Line</B><BR/><FONT POINT-SIZE="10" COLOR="#2D3748">Billet Heating &rarr; Forging / Stamping &rarr; Precision CNC Turning &rarr; Final Assembly</FONT>>,
        fillcolor="#F0FFF4",
        color="#38A169",
        width=8.0
    ];

    OUT [
        label=<<B><FONT POINT-SIZE="13">Finished Production Output: 131,324.1 Units / Month</FONT></B><BR/><FONT POINT-SIZE="10.5" COLOR="#276749"><B>Strictly Invariant Constraint: &Delta;Q = 0.0 units (100% Protected, Zero Throttle)</B></FONT>>,
        fillcolor="#C6F6D5",
        color="#22543D",
        penwidth=2.2,
        width=8.5
    ];

    EQ01 -> PROC [color="#38A169", penwidth=2.0];
    EQ02 -> PROC [color="#38A169", penwidth=2.0];
    EQ05 -> PROC [color="#38A169", penwidth=2.0];
    EQ06 -> PROC [color="#38A169", penwidth=2.0];

    // Utilities to Process (Dashed service support)
    EQ03 -> PROC [style="dashed", color="#718096", label="Cooling"];
    EQ04 -> PROC [style="dashed", color="#718096", label="Pneumatics"];
    EQ07 -> PROC [style="dashed", color="#718096", label="Facility"];

    PROC -> OUT [color="#22543D", penwidth=2.5];
}
"""

with open("scratch/physical.dot", "w", encoding="utf-8") as f:
    f.write(dot_physical)

print("Wrote scratch/physical.dot")
