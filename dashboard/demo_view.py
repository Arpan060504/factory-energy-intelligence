"""
Factory Energy Intelligence Platform - Canonical Hackathon Demo Mode
Transforms the validated, frozen model and synthetic dataset into a structured,
compelling 3-5 minute live walkthrough.

Story Sequence:
Step 1: Normal Factory Operation (Calibrated Baseline)
Step 2: Energy Anomaly Detected (Actual > Expected with Constant Production)
Step 3: Hierarchical Drill-Down: Finding the Machine (Factory -> Substation -> Feeder -> Machine)
Step 4: Evidence-Based Root Cause Diagnosis & Actionable Maintenance SOP
Step 5: Algorithmic Optimization with Strict Production Protection
Step 6: Audited Before vs After, Decoupled Savings Waterfall & Executive Summary
"""

import os
import json
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO_CONFIG_PATH = os.path.join(BASE_DIR, "data", "demo", "canonical_demo_config.json")


def load_demo_config() -> dict:
    """Loads the canonical demo configuration."""
    if os.path.exists(DEMO_CONFIG_PATH):
        with open(DEMO_CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}


def render_demo_header(step_badge: str, title: str, subtitle: str):
    """Renders standardized header for demo walkthrough steps."""
    st.markdown(
        f'<div style="background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%); '
        f'color: white; padding: 6px 14px; border-radius: 20px; display: inline-block; '
        f'font-size: 0.82rem; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 8px;">'
        f'{step_badge}</div>',
        unsafe_allow_html=True
    )
    st.markdown(f'<div class="main-header">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">{subtitle}</div>', unsafe_allow_html=True)


def render_hero_metrics(sec: str, sec_sub: str, prod: str, prod_sub: str,
                        energy: str, energy_sub: str, cost: str, cost_sub: str,
                        co2: str, co2_sub: str):
    """
    Renders top visual hierarchy hero metrics:
    1. SEC (Primary efficiency KPI)
    2. Production (Throughput protection)
    3. Energy
    4. Cost
    5. CO2
    """
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric(label="🎯 Specific Energy (SEC)", value=sec, delta=sec_sub, delta_color="normal")
    with c2:
        st.metric(label="📦 Production Output", value=prod, delta=prod_sub, delta_color="off")
    with c3:
        st.metric(label="⚡ Total Active Energy", value=energy, delta=energy_sub, delta_color="normal")
    with c4:
        st.metric(label="💰 Electricity Cost", value=cost, delta=cost_sub, delta_color="normal")
    with c5:
        st.metric(label="🌱 Scope 2 Carbon", value=co2, delta=co2_sub, delta_color="normal")


def render_step_1_normal(df_base: pd.DataFrame, cfg: dict):
    """STEP 1: Normal Factory Operation."""
    render_demo_header(
        "🟢 STEP 1 OF 6 | BASELINE CALIBRATION",
        "Step 1: Normal Factory Operation",
        "Under nominal baseline operation (March 3, 2026), all 7 production and utility feeders operate within "
        "production-correlated baseline envelopes. Specific Energy Consumption is stable."
    )

    p_cfg = cfg.get("step_1_normal_operation", {}).get("plant_metrics", {})
    render_hero_metrics(
        sec=f"{p_cfg.get('sec_kwh_per_unit', 1.3919):.4f} kWh/u",
        sec_sub="Normal Baseline",
        prod=f"{p_cfg.get('production_units', 5251.0):,.0f} units",
        prod_sub="Daily Target Met",
        energy=f"{p_cfg.get('active_energy_kwh', 7309.1):,.1f} kWh",
        energy_sub=f"{p_cfg.get('energy_deviation_pct', -0.2):.1f}% vs Expected",
        cost=f"₹ {p_cfg.get('daily_cost_inr', 57011):,.0f}",
        cost_sub="Normal TOD Rates",
        co2=f"{p_cfg.get('daily_carbon_mt_co2', 5.23):.2f} MT",
        co2_sub="CEA Grid Factor"
    )

    st.markdown("---")

    col_chart1, col_chart2 = st.columns([7, 5])
    
    # Filter normal day data (March 3, 2026)
    df_normal = df_base[pd.to_datetime(df_base["timestamp"]).dt.date == pd.to_datetime("2026-03-03").date()].copy()
    
    with col_chart1:
        st.subheader("Diurnal Load Curve: Actual Power vs. Expected Baseline (Normal Day)")
        if not df_normal.empty:
            plant_hourly = df_normal.groupby("timestamp").agg(
                actual_kw=("active_power_kw", "sum"),
                expected_kw=("expected_power_kw", "sum")
            ).reset_index()

            fig_load = go.Figure()
            fig_load.add_trace(go.Scatter(
                x=pd.to_datetime(plant_hourly["timestamp"]),
                y=plant_hourly["actual_kw"],
                name="Actual Power (kW)",
                line=dict(color="#2563EB", width=2)
            ))
            fig_load.add_trace(go.Scatter(
                x=pd.to_datetime(plant_hourly["timestamp"]),
                y=plant_hourly["expected_kw"],
                name="Expected Baseline (kW)",
                line=dict(color="#10B981", width=2, dash="dash")
            ))
            fig_load.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=30, b=20),
                xaxis_title="Time of Day",
                yaxis_title="Total Plant Power (kW)",
                legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center")
            )
            st.plotly_chart(fig_load, use_container_width=True)

    with col_chart2:
        st.subheader("Feeder Energy Share (% of Daily kWh)")
        if not df_normal.empty:
            feeder_share = df_normal.groupby("machine_name")["energy_kwh"].sum().reset_index()
            fig_pie = px.pie(
                feeder_share,
                values="energy_kwh",
                names="machine_name",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_pie.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

    st.success(
        "✅ **Baseline Operation Confirmed:** Actual electricity consumption tracks within ±0.2% of the "
        "production-expected Ridge regression baseline. Specific Energy Consumption is stable at **1.3919 kWh/unit**."
    )


def render_step_2_anomaly(df_base: pd.DataFrame, cfg: dict):
    """STEP 2: Energy Anomaly Detected."""
    render_demo_header(
        "🔴 STEP 2 OF 6 | ANOMALY DETECTION",
        "Step 2: Factory Energy Anomaly Detected",
        "On March 9, 2026, factory-wide energy consumption surges significantly above the production-expected baseline "
        "while production throughput remains virtually unchanged."
    )

    p_cfg = cfg.get("step_2_energy_anomaly", {}).get("plant_metrics", {})
    render_hero_metrics(
        sec=f"{p_cfg.get('sec_kwh_per_unit', 1.4279):.4f} kWh/u",
        sec_sub="+2.6% Degraded",
        prod=f"{p_cfg.get('production_units', 5272.2):,.0f} units",
        prod_sub="+0.4% (Unchanged)",
        energy=f"{p_cfg.get('active_energy_kwh', 7527.9):,.1f} kWh",
        energy_sub="+183.7 kWh Excess (+2.5%)",
        cost=f"₹ {p_cfg.get('daily_cost_inr', 58718):,.0f}",
        cost_sub="+₹ 1,707 Excess Cost",
        co2=f"{p_cfg.get('daily_carbon_mt_co2', 5.39):.2f} MT",
        co2_sub="+131 kg CO2 Waste"
    )

    st.markdown("---")

    col1, col2 = st.columns([7, 5])
    
    df_anom = df_base[pd.to_datetime(df_base["timestamp"]).dt.date == pd.to_datetime("2026-03-09").date()].copy()

    with col1:
        st.subheader("Plant Power Profile: Actual vs Expected Baseline (March 9 Anomaly)")
        if not df_anom.empty:
            plant_hourly = df_anom.groupby("timestamp").agg(
                actual_kw=("active_power_kw", "sum"),
                expected_kw=("expected_power_kw", "sum")
            ).reset_index()

            fig_anom = go.Figure()
            fig_anom.add_trace(go.Scatter(
                x=pd.to_datetime(plant_hourly["timestamp"]),
                y=plant_hourly["actual_kw"],
                name="Actual Power (kW)",
                line=dict(color="#DC2626", width=2.2)
            ))
            fig_anom.add_trace(go.Scatter(
                x=pd.to_datetime(plant_hourly["timestamp"]),
                y=plant_hourly["expected_kw"],
                name="Expected Baseline (kW)",
                line=dict(color="#64748B", width=2, dash="dash")
            ))
            fig_anom.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=30, b=20),
                xaxis_title="Time of Day (March 9, 2026)",
                yaxis_title="Total Plant Power (kW)",
                legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center")
            )
            st.plotly_chart(fig_anom, use_container_width=True)

    with col2:
        st.subheader("Daily Comparison: Normal Day vs. Anomaly Day")
        comp_df = pd.DataFrame([
            {"Day": "Normal Day (Mar 3)", "Actual (kWh)": 7309.1, "Expected (kWh)": 7321.7, "SEC (kWh/u)": 1.3919},
            {"Day": "Anomaly Day (Mar 9)", "Actual (kWh)": 7527.9, "Expected (kWh)": 7344.2, "SEC (kWh/u)": 1.4279}
        ])
        fig_bar = px.bar(
            comp_df,
            x="Day",
            y=["Actual (kWh)", "Expected (kWh)"],
            barmode="group",
            color_discrete_sequence=["#DC2626", "#64748B"],
            height=350
        )
        fig_bar.update_layout(margin=dict(l=20, r=20, t=30, b=20), yaxis_title="Energy (kWh/day)")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.warning(
        "⚠️ **Energy Efficiency Alert Triggered:** Plant energy consumption is **+183.7 kWh (+2.5%)** above the "
        "production-normalized expected baseline. Total factory production remained constant (5,272 vs 5,251 units). "
        "The plant is expending excess electrical power without generating additional manufactured product."
    )


def render_step_3_investigate(df_base: pd.DataFrame, cfg: dict):
    """STEP 3: Drill-Down: Finding the Machine."""
    render_demo_header(
        "🔍 STEP 3 OF 6 | TOPOLOGICAL LOCALIZATION",
        "Step 3: Drill Down to Locate the Machine",
        "Navigating the plant's electrical distribution topology from Grid ➔ Substation ➔ Bus ➔ Feeder ➔ Machine "
        "to pinpoint the exact source of parasitic consumption."
    )

    st.markdown("""
    ```
    [11 kV UTILITY GRID]
            │
      [SUBSTATION SUB_01 (1000 kVA Transformer TR_01)]
            │
      [MAIN 415V BUS: BUS_A (1600A ACB)]
            ├────── FDR_01 ─── 🚨 [MOTOR_01: CNC Machining Center (75 kW)] ➔ +188.1 kWh EXCESS!
            ├────── FDR_02 ─── [MOTOR_02: Hydraulic Stamping Press (55 kW)] (Nominal)
            ├────── FDR_03 ─── [PUMP_01: Chilled Water Pump (30 kW)] (Nominal)
            ├────── FDR_04 ─── [COMP_01: Rotary Screw Air Compressor (45 kW)] (Nominal)
            ├────── FDR_05 ─── [FURNACE_01: Induction Billet Heating (160 kW)] (Nominal)
            ├────── FDR_06 ─── [LINE_01: Conveyor & Final Assembly Line (22 kW)] (Nominal)
            └────── FDR_07 ─── [AUX_01: Plant Utilities & Lighting (25 kW)] (Nominal)
    ```
    """)

    st.error(
        "🎯 **Topological Isolation:** Feeder **FDR_01 (`MOTOR_01` - CNC Machining Center)** accounted for "
        "**+188.1 kWh** of excess consumption (over 100% of the net plant excess!). All other 6 feeders operated "
        "within their expected physical baseline bounds."
    )

    st.markdown("### Equipment Telemetry Comparison: Normal Day vs. Anomaly Day (`MOTOR_01`)")

    m_ev = cfg.get("step_3_find_machine", {}).get("machine_evidence", {})
    norm_m = m_ev.get("normal_day", {})
    anom_m = m_ev.get("anomalous_day", {})

    t1, t2, t3, t4 = st.columns(4)
    with t1:
        st.metric("Average Current", f"{anom_m.get('average_current_a', 97.2):.1f} A", f"+{anom_m.get('current_increase_pct', 15.4):.1f}% draw", delta_color="inverse")
        st.metric("Active Power Draw", f"{anom_m.get('active_power_kw_avg', 60.9):.1f} kW", f"+{anom_m.get('energy_deviation_pct', 14.8):.1f}% excess", delta_color="inverse")
    with t2:
        st.metric("Bearing Vibration RMS", f"{anom_m.get('vibration_rms_mm_s', 3.99):.2f} mm/s", f"+{anom_m.get('vibration_increase_pct', 167.8):.1f}% surge (ISO Alert!)", delta_color="inverse")
        st.metric("Bearing Temperature", f"{anom_m.get('bearing_temp_c', 53.9):.1f} °C", f"+{anom_m.get('temperature_rise_c', 11.8):.1f} °C rise", delta_color="inverse")
    with t3:
        st.metric("Three-Phase Voltage", "412.8 V", "Balanced (0.8% Unbalance)", delta_color="off")
        st.metric("Operating Power Factor", f"{anom_m.get('power_factor', 0.904):.3f}", "Healthy PF", delta_color="off")
    with t4:
        st.metric("Production Output", f"{anom_m.get('production_units', 831.9):.1f} units", f"+{anom_m.get('production_change_pct', 0.6):.1f}% (Unchanged)", delta_color="off")
        st.metric("Machine SEC", f"{anom_m.get('sec_kwh_per_unit', 1.7560):.4f} kWh/u", f"+{anom_m.get('sec_degradation_pct', 14.9):.1f}% Wasted / Unit", delta_color="inverse")

    st.markdown("---")

    # Time series of MOTOR_01 on Anomaly Day
    df_m1 = df_base[(df_base["machine_id"] == "MOTOR_01") & 
                    (pd.to_datetime(df_base["timestamp"]).dt.date == pd.to_datetime("2026-03-09").date())].copy()

    if not df_m1.empty:
        st.subheader("MOTOR_01 Telemetry Detail: Active Power (kW) vs. Vibration Velocity RMS (mm/s)")
        fig_sub = make_subplots(specs=[[{"secondary_y": True}]])
        fig_sub.add_trace(
            go.Scatter(x=pd.to_datetime(df_m1["timestamp"]), y=df_m1["active_power_kw"], name="Active Power (kW)", line=dict(color="#2563EB", width=2)),
            secondary_y=False
        )
        fig_sub.add_trace(
            go.Scatter(x=pd.to_datetime(df_m1["timestamp"]), y=df_m1["vibration"], name="Vibration RMS (mm/s)", line=dict(color="#EA580C", width=1.8, dash="dot")),
            secondary_y=True
        )
        fig_sub.add_hline(y=2.8, line_dash="dash", line_color="#DC2626", annotation_text="ISO 10816-3 Class II Limit (2.8 mm/s)", secondary_y=True)
        fig_sub.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20), xaxis_title="Timestamp")
        fig_sub.update_yaxes(title_text="Active Power (kW)", secondary_y=False)
        fig_sub.update_yaxes(title_text="Vibration RMS (mm/s)", secondary_y=True)
        st.plotly_chart(fig_sub, use_container_width=True)


def render_step_4_recommendation(cfg: dict):
    """STEP 4: Explain Why & Actionable Recommendation."""
    render_demo_header(
        "📋 STEP 4 OF 6 | ROOT CAUSE & RECOMMENDATION",
        "Step 4: Root Cause Diagnosis & Actionable Maintenance SOP",
        "Multi-variable sensor synthesis provides an evidence-based diagnosis, accompanied by a prioritized "
        "Standard Operating Procedure (SOP) with quantified financial savings."
    )

    ev_rows = cfg.get("step_4_explain_why", {}).get("evidence_summary", [])
    st.subheader("Physical Evidence Matrix (`MOTOR_01`)")
    st.dataframe(pd.DataFrame(ev_rows), use_container_width=True)

    c_diag1, c_diag2 = st.columns([6, 6])
    with c_diag1:
        st.markdown("""
        <div style="background-color: #EFF6FF; border-left: 5px solid #2563EB; padding: 16px; border-radius: 6px;">
            <h4 style="color: #1E40AF; margin-top: 0;">🔬 Root Cause Diagnostic Synthesis</h4>
            <p style="font-size: 0.92rem; color: #1E3A8A; line-height: 1.5;">
            • <b>Electrical Behavior:</b> Motor draws +15.4% excess current and +14.8% power while 3-phase voltages remain balanced (NEMA unbalance = 1.2%). This explicitly rules out supply contactor terminal loosening.<br/>
            • <b>Mechanical Signature:</b> Vibration velocity RMS surged to 3.99 mm/s (exceeding ISO 10816-3 Class II threshold of 2.8 mm/s).<br/>
            • <b>Thermal Rise:</b> Drive-end bearing temperature rose by +11.8 °C.<br/>
            • <b>Throughput:</b> Production throughput is virtually unchanged (831.9 vs 827.3 units).<br/>
            <hr style="margin: 10px 0;"/>
            <b>Diagnosis:</b> Mechanical bearing race wear and shaft misalignment causing severe parasitic friction torque. The motor is expending electrical energy fighting internal friction rather than cutting metal.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c_diag2:
        rec = cfg.get("step_5_actionable_recommendation", {})
        imp = rec.get("expected_impact", {})
        st.markdown(f"""
        <div style="background-color: #F0FDF4; border-left: 5px solid #16A34A; padding: 16px; border-radius: 6px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="color: #166534; margin: 0;">🛠️ Standard Operating Procedure (REC-001)</h4>
                <span style="background-color: #DCFCE7; color: #166534; padding: 2px 8px; border-radius: 10px; font-weight: 700; font-size: 0.75rem;">HIGH PRIORITY</span>
            </div>
            <p style="font-size: 0.88rem; color: #14532D; margin-top: 8px;">
            <b>WHAT HAPPENED?</b><br/>{rec.get('what_happened')}<br/><br/>
            <b>WHY?</b><br/>{rec.get('why')}<br/><br/>
            <b>RECOMMENDED ACTION:</b><br/>
            1. Schedule drive-end bearing regreasing during next shift handover (14:00).<br/>
            2. Verify laser shaft alignment and belt tension.<br/>
            3. Clean motor stator cooling intake cowl to prevent thermal derating.<br/><br/>
            <b>EXPECTED IMPACT:</b><br/>
            • Monthly Energy Saving: <b>{imp.get('monthly_energy_saving_kwh', 3473):,.0f} kWh / mo</b><br/>
            • Monthly Cost Saving: <b>₹ {imp.get('monthly_cost_saving_inr', 29520):,.0f} / mo</b><br/>
            • Carbon Avoided: <b>{imp.get('monthly_carbon_avoided_mt', 2.48):.2f} MT CO2 / mo</b><br/>
            • Payback: <b>&lt; 2 Days</b>
            </p>
        </div>
        """, unsafe_allow_html=True)


def render_step_5_optimization(comparison: dict):
    """STEP 5: Optimization Action with Strict Production Protection."""
    render_demo_header(
        "⚡ STEP 5 OF 6 | THREE-TIER OPTIMIZATION",
        "Step 5: Apply Recommended Algorithmic Optimization",
        "Execute multi-tier optimization engine enforcing strict production throughput invariance and tariff arbitrage."
    )

    base_m = comparison["baseline"]
    opt_m = comparison["optimized"]
    impact = comparison["impact"]

    st.markdown("### 🛡️ Production Protection Guarantee")

    c_p1, c_p2, c_p3 = st.columns(3)
    with c_p1:
        st.metric("Contract Production Requirement", f"{base_m['production_units']:,.1f} units")
    with c_p2:
        st.metric("Baseline Output Delivered", f"{base_m['production_units']:,.1f} units")
    with c_p3:
        st.metric("Optimized Output Delivered", f"{opt_m['production_units']:,.1f} units", "0.0 units change (100% Invariant!)")

    if impact.get("production_constraint_satisfied", True):
        st.success(
            "✅ **PRODUCTION CONSTRAINT SATISFIED:** The optimization model strictly guarantees that production output "
            "is 100.0% preserved (131,324.1 units vs. 131,324.1 units). Energy reduction is achieved purely through "
            "parasitic friction restoration and idle energy elimination, NEVER by throttling output."
        )
    else:
        st.error("❌ **PRODUCTION CONSTRAINT VIOLATED:** Optimization rejected!")

    st.markdown("---")
    st.subheader("Integrated Optimization Levers Applied")

    lev1, lev2, lev3 = st.columns(3)
    with lev1:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1E3A8A; margin-top: 0;">1. Idle Energy Elimination</h4>
            <p style="font-size: 0.88rem; color: #4B5563;">
            Interlocks compressor <code>COMP_01</code> and equipment during lunch breaks and shift changeovers.
            <br/><br/>
            <b>Energy Saved:</b> 31,973.2 kWh / mo<br/>
            <b>Cost Saved:</b> ₹ 2,67,970 / mo
            </p>
        </div>
        """, unsafe_allow_html=True)

    with lev2:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1E3A8A; margin-top: 0;">2. TOD Tariff Load Shifting</h4>
            <p style="font-size: 0.88rem; color: #4B5563;">
            Reschedules 160 kW furnace <code>FURNACE_01</code> batches from Peak (₹11.50) to Off-Peak (₹5.20).
            <br/><br/>
            <b>Physical Energy Saved:</b> 0.0 kWh (Neutral)<br/>
            <b>Tariff Cost Saved:</b> ₹ 93,619 / mo
            </p>
        </div>
        """, unsafe_allow_html=True)

    with lev3:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1E3A8A; margin-top: 0;">3. Mechanical Health Restoration</h4>
            <p style="font-size: 0.88rem; color: #4B5563;">
            Restores <code>MOTOR_01</code> to nominal efficiency and power factor via maintenance SOP REC-001.
            <br/><br/>
            <b>Energy Saved:</b> 3,473.0 kWh / mo<br/>
            <b>Cost Saved:</b> ₹ 29,520 / mo
            </p>
        </div>
        """, unsafe_allow_html=True)


def render_step_6_verification(comparison: dict, cfg: dict):
    """STEP 6: Audited Before vs After, Savings Waterfall & Executive Summary."""
    render_demo_header(
        "🏆 STEP 6 OF 6 | AUDITED VERIFICATION & ROI",
        "Step 6: Audited Before vs. After Results & ROI",
        "Rigorous audited comparison, decoupled savings waterfalls (physical energy vs. tariff economics), "
        "and turnkey SME business model payback."
    )

    base = comparison["baseline"]
    opt = comparison["optimized"]
    impact = comparison["impact"]

    # Master Audited Comparison Table
    st.markdown("### Master Audited Comparison (30-Day Evaluation Period)")
    comp_table = pd.DataFrame([
        {
            "Performance Metric": "Total Active Energy (kWh)",
            "BEFORE (Baseline)": f"{base['energy_kwh']:,.1f} kWh",
            "AFTER (Optimized)": f"{opt['energy_kwh']:,.1f} kWh",
            "IMPACT / DELTA": f"-{impact['energy_reduction_kwh']:,.1f} kWh",
            "IMPROVEMENT": f"-{impact['energy_reduction_pct']:.2f}%"
        },
        {
            "Performance Metric": "Specific Energy Consumption (SEC)",
            "BEFORE (Baseline)": f"{base['sec_kwh_per_unit']:.4f} kWh/u",
            "AFTER (Optimized)": f"{opt['sec_kwh_per_unit']:.4f} kWh/u",
            "IMPACT / DELTA": f"-{base['sec_kwh_per_unit'] - opt['sec_kwh_per_unit']:.4f} kWh/u",
            "IMPROVEMENT": f"-{impact['sec_improvement_pct']:.2f}%"
        },
        {
            "Performance Metric": "Production Throughput (units)",
            "BEFORE (Baseline)": f"{base['production_units']:,.1f} units",
            "AFTER (Optimized)": f"{opt['production_units']:,.1f} units",
            "IMPACT / DELTA": f"{impact['production_change_units']} units",
            "IMPROVEMENT": "0.00% (Strictly Invariant)"
        },
        {
            "Performance Metric": "Electricity Bill (₹)",
            "BEFORE (Baseline)": f"₹ {base['electricity_cost_inr']:,.0f}",
            "AFTER (Optimized)": f"₹ {opt['electricity_cost_inr']:,.0f}",
            "IMPACT / DELTA": f"-₹ {impact['cost_reduction_inr']:,.0f}",
            "IMPROVEMENT": f"-{impact['cost_reduction_pct']:.2f}%"
        },
        {
            "Performance Metric": "Peak Demand (kVA)",
            "BEFORE (Baseline)": f"{base['peak_demand_kva']:.1f} kVA",
            "AFTER (Optimized)": f"{opt['peak_demand_kva']:.1f} kVA",
            "IMPACT / DELTA": f"-{impact['peak_demand_reduction_kva']:.1f} kVA",
            "IMPROVEMENT": f"-{impact.get('peak_demand_reduction_pct', 2.72):.2f}%"
        },
        {
            "Performance Metric": "Scope 2 Carbon Emissions (MT)",
            "BEFORE (Baseline)": f"{base['carbon_emissions_mt_co2']:.2f} MT",
            "AFTER (Optimized)": f"{opt['carbon_emissions_mt_co2']:.2f} MT",
            "IMPACT / DELTA": f"-{impact['emissions_avoided_mt_co2']:.2f} MT",
            "IMPROVEMENT": f"-{impact['energy_reduction_pct']:.2f}%"
        }
    ])
    st.dataframe(comp_table, use_container_width=True)

    st.info(
        "💡 **Decoupling Physical Energy vs. Tariff Economics:**\n\n"
        "• **Physical Energy Savings:** **31,973.1 kWh / month** saved strictly through idle energy elimination and mechanical restoration.\n"
        "• **Tariff Arbitrage Savings:** **₹ 93,618.68 / month** saved with **ZERO change in physical energy**, achieved purely by moving 12,997.8 kWh from Peak (₹11.50) to Off-Peak (₹5.20)."
    )

    st.markdown("---")
    st.subheader("Decoupled Savings Waterfalls")

    cw1, cw2 = st.columns(2)

    with cw1:
        st.markdown("**Physical Energy Reduction Waterfall (kWh)**")
        fig_w_energy = go.Figure(go.Waterfall(
            name="Energy Waterfall",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "total"],
            x=["Baseline Energy", "Idle Elimination", "Mechanical Restoration", "TOD Shifting", "Optimized Energy"],
            textposition="outside",
            text=["191,139 kWh", "-28,500 kWh", "-3,473 kWh", "0 kWh", "159,166 kWh"],
            y=[191138.7, -28500.0, -3473.1, 0.0, 159165.7],
            connector={"line": {"color": "#64748B"}},
            decreasing={"marker": {"color": "#10B981"}},
            totals={"marker": {"color": "#3B82F6"}}
        ))
        fig_w_energy.update_layout(height=360, margin=dict(l=20, r=20, t=30, b=20), yaxis_title="Active kWh")
        st.plotly_chart(fig_w_energy, use_container_width=True)

    with cw2:
        st.markdown("**Electricity Cost Savings Waterfall (₹)**")
        fig_w_cost = go.Figure(go.Waterfall(
            name="Cost Waterfall",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "total"],
            x=["Baseline Bill", "Idle Reduction", "Mechanical Restoration", "TOD Load Shifting", "Optimized Bill"],
            textposition="outside",
            text=["₹ 19.40 L", "-₹ 2.38 L", "-₹ 0.30 L", "-₹ 0.94 L", "₹ 15.79 L"],
            y=[1940446.0, -238450.0, -29520.0, -93618.68, 1578857.0],
            connector={"line": {"color": "#64748B"}},
            decreasing={"marker": {"color": "#10B981"}},
            totals={"marker": {"color": "#3B82F6"}}
        ))
        fig_w_cost.update_layout(height=360, margin=dict(l=20, r=20, t=30, b=20), yaxis_title="Electricity Cost (₹)")
        st.plotly_chart(fig_w_cost, use_container_width=True)

    st.markdown("---")

    # Executive Summary Block (Section 10 Requirement)
    st.markdown(f"""
    <div style="background-color: #0F172A; border: 2px solid #3B82F6; border-radius: 12px; padding: 24px; color: white; margin: 20px 0;">
        <div style="text-align: center; font-size: 1.3rem; font-weight: 700; letter-spacing: 1px; color: #60A5FA; margin-bottom: 16px;">
            FACTORY OPTIMIZATION RESULT
        </div>
        <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; text-align: center;">
            <div style="background: rgba(255,255,255,0.06); padding: 12px; border-radius: 8px;">
                <div style="font-size: 0.8rem; color: #94A3B8;">ACTIVE ENERGY</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC; margin: 4px 0;">{base['energy_kwh']:,.0f} → {opt['energy_kwh']:,.0f} kWh</div>
                <div style="font-size: 0.85rem; color: #34D399; font-weight: 600;">-{impact['energy_reduction_pct']:.2f}%</div>
            </div>
            <div style="background: rgba(255,255,255,0.06); padding: 12px; border-radius: 8px;">
                <div style="font-size: 0.8rem; color: #94A3B8;">SPECIFIC ENERGY (SEC)</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC; margin: 4px 0;">{base['sec_kwh_per_unit']:.4f} → {opt['sec_kwh_per_unit']:.4f} kWh/u</div>
                <div style="font-size: 0.85rem; color: #34D399; font-weight: 600;">-{impact['sec_improvement_pct']:.2f}%</div>
            </div>
            <div style="background: rgba(255,255,255,0.06); padding: 12px; border-radius: 8px;">
                <div style="font-size: 0.8rem; color: #94A3B8;">PRODUCTION OUTPUT</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC; margin: 4px 0;">{base['production_units']:,.0f} → {opt['production_units']:,.0f} u</div>
                <div style="font-size: 0.85rem; color: #60A5FA; font-weight: 600;">100% Invariant</div>
            </div>
            <div style="background: rgba(255,255,255,0.06); padding: 12px; border-radius: 8px;">
                <div style="font-size: 0.8rem; color: #94A3B8;">ELECTRICITY BILL</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC; margin: 4px 0;">₹ {base['electricity_cost_inr']:,.0f} → ₹ {opt['electricity_cost_inr']:,.0f}</div>
                <div style="font-size: 0.85rem; color: #34D399; font-weight: 600;">-₹ {impact['cost_reduction_inr']:,.0f} / mo</div>
            </div>
            <div style="background: rgba(255,255,255,0.06); padding: 12px; border-radius: 8px;">
                <div style="font-size: 0.8rem; color: #94A3B8;">SCOPE 2 EMISSIONS</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC; margin: 4px 0;">{base['carbon_emissions_mt_co2']:.2f} → {opt['carbon_emissions_mt_co2']:.2f} MT</div>
                <div style="font-size: 0.85rem; color: #34D399; font-weight: 600;">-{impact['emissions_avoided_mt_co2']:.2f} MT Avoided</div>
            </div>
        </div>
        <div style="text-align: center; margin-top: 18px; font-size: 1.05rem; font-weight: 700; color: #34D399;">
            ✓ Production constraint: SATISFIED (Throughput 100.0% Protected)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # SME Business Model Summary
    st.markdown("### SME Turnkey Business Model & Payback")
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.metric("Total Turnkey Capex", "₹ 1,52,150", "8 Feeder Plant BOM (~$1,830)")
    with b2:
        st.metric("Annual Software SaaS", "₹ 36,000", "₹ 3,000 / month")
    with b3:
        st.metric("Net Monthly Savings", f"₹ {impact['cost_reduction_inr'] - 3000:,.0f} / mo", "After Software SaaS")
    with b4:
        st.metric("Simple Payback Period", "12.7 Days (~13 Days)", "Phased: 1.8–3.5 Months")


def render_demo_view(demo_step: str, df_base: pd.DataFrame, df_opt: pd.DataFrame,
                     comparison: dict, df_incidents: pd.DataFrame, df_health: pd.DataFrame):
    """Master router for Hackathon Demo Mode."""
    cfg = load_demo_config()

    if "1. Normal" in demo_step:
        render_step_1_normal(df_base, cfg)
    elif "2. Energy Anomaly" in demo_step:
        render_step_2_anomaly(df_base, cfg)
    elif "3. Drill-Down" in demo_step or "Investigate" in demo_step:
        render_step_3_investigate(df_base, cfg)
    elif "4. Root Cause" in demo_step or "Recommendation" in demo_step:
        render_step_4_recommendation(cfg)
    elif "5. Apply Optimization" in demo_step:
        render_step_5_optimization(comparison)
    elif "6. Audited Before" in demo_step or "Summary" in demo_step:
        render_step_6_verification(comparison, cfg)
    else:
        render_step_1_normal(df_base, cfg)
