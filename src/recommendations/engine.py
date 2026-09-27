"""
Industrial Recommendation Engine.
Translates detected anomalies, electrical metrics, and machine health deficits into
concrete, prioritized, quantified Standard Operating Procedures (SOPs) for SME plant operators.
Answers: WHAT happened? WHY it matters? WHAT should the operator do? WHAT could be saved?
Dynamically updates all rupee and CO2 savings when TariffConfig or EmissionConfig change.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
from ..config import TariffConfig, EmissionConfig


class RecommendationEngine:
    def __init__(
        self,
        tariff_per_kwh: Optional[float] = None,
        co2_factor: Optional[float] = None,
        tariff_config: Optional[TariffConfig] = None,
        emission_config: Optional[EmissionConfig] = None
    ):
        self.tariff_config = tariff_config or TariffConfig(
            normal_rate_inr=tariff_per_kwh if tariff_per_kwh is not None else 7.80
        )
        self.emission_config = emission_config or EmissionConfig(
            grid_emission_factor_kg_per_kwh=co2_factor if co2_factor is not None else 0.716
        )
        
        # Effective blend rate for general maintenance loss calculations
        self.tariff = self.tariff_config.normal_rate_inr
        self.co2_factor = self.emission_config.grid_emission_factor_kg_per_kwh

    def generate_recommendations(
        self,
        df_incidents: pd.DataFrame,
        fleet_health_df: Optional[pd.DataFrame] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates actionable, quantified engineering recommendations from incident logs and health scores.
        All financial savings (INR) and environmental savings (CO2) update dynamically.
        """
        recs = []
        rec_counter = 1

        # 1. Generate from incident records if available
        if not df_incidents.empty:
            for _, inc in df_incidents.iterrows():
                mid = str(inc["machine_id"])
                atype = str(inc["anomaly_type"])
                sev = str(inc["severity"])
                obs_val = inc["mean_observed_value"]
                metric = inc["metric_name"]
                tot_loss = inc["estimated_loss_inr"]
                dur = inc["duration_hours"]

                if atype == "EXCESSIVE_IDLE_CONSUMPTION":
                    kwh_saved_monthly = round(obs_val * 4.0 * 25, 1)  # 4 idle hrs/day, 25 working days
                    inr_saved_monthly = round(kwh_saved_monthly * self.tariff_config.normal_rate_inr, 2)
                    co2_saved_monthly = round(kwh_saved_monthly * self.co2_factor, 1)

                    recs.append({
                        "rec_id": f"REC-{rec_counter:03d}",
                        "machine_id": mid,
                        "category": "IDLE_ENERGY_REDUCTION",
                        "priority": "HIGH" if sev == "CRITICAL" else "MEDIUM",
                        "what_happened": f"{mid} observed running unloaded at {obs_val} kW for {dur} hours during break/night periods with zero production.",
                        "why_it_matters": f"Unnecessary idle operation dissipates energy into unloaded friction and air blow-off. At ₹{self.tariff_config.normal_rate_inr:.2f}/kWh, idle energy losses cost ~₹{inr_saved_monthly:,.0f}/month.",
                        "operator_action": "1. Verify auto-shutdown timer setting on machine PLC (set to 5 min idle cutoff). 2. Conduct ultrasonic acoustic leak audit on shop-floor air drop lines.",
                        "estimated_monthly_kwh_saving": kwh_saved_monthly,
                        "estimated_monthly_inr_saving": inr_saved_monthly,
                        "estimated_monthly_co2_kg_saving": co2_saved_monthly,
                        "sec_impact": "Directly reduces numerator in SEC (kWh/unit), reducing machine SEC by 8% to 15%."
                    })
                    rec_counter += 1

                elif atype in ["MACHINE_EFFICIENCY_DEGRADATION", "ENERGY_ANOMALY"]:
                    excess_kw = max(2.0, obs_val * 0.15)
                    kwh_saved_monthly = round(excess_kw * 16.0 * 25, 1)  # 2 shifts/day
                    inr_saved_monthly = round(kwh_saved_monthly * self.tariff_config.normal_rate_inr, 2)
                    co2_saved_monthly = round(kwh_saved_monthly * self.co2_factor, 1)

                    recs.append({
                        "rec_id": f"REC-{rec_counter:03d}",
                        "machine_id": mid,
                        "category": "MECHANICAL_EFFICIENCY_MAINTENANCE",
                        "priority": "HIGH",
                        "what_happened": f"{mid} active power is +{obs_val}% above the expected production-normalized baseline while output remains unchanged.",
                        "why_it_matters": f"Excessive electrical draw without production gain indicates internal mechanical friction, bearing drag, or thermal losses, wasting ~₹{inr_saved_monthly:,.0f}/month and risking unpredicted line stoppage.",
                        "operator_action": "1. Schedule bearing regreasing and inspect drive belt tension. 2. Perform vibration spectrum check for 1X/2X shaft misalignment frequencies. 3. Check motor air intake cowl for debris.",
                        "estimated_monthly_kwh_saving": kwh_saved_monthly,
                        "estimated_monthly_inr_saving": inr_saved_monthly,
                        "estimated_monthly_co2_kg_saving": co2_saved_monthly,
                        "sec_impact": "Restores baseline machine SEC from degraded state."
                    })
                    rec_counter += 1

                elif atype == "LOW_POWER_FACTOR":
                    inr_saved_monthly = round(4500.0 * (self.tariff_config.normal_rate_inr / 7.80), 2)  # Avoided DISCOM penalty
                    recs.append({
                        "rec_id": f"REC-{rec_counter:03d}",
                        "machine_id": mid,
                        "category": "POWER_FACTOR_OPTIMIZATION",
                        "priority": "HIGH",
                        "what_happened": f"Power factor on {mid} dropped to {obs_val}, well below the {self.tariff_config.pf_penalty_threshold} DISCOM penalty threshold.",
                        "why_it_matters": f"Low power factor draws heavy reactive current (kVAR), inflates apparent kVA demand, increases I2R cable heating, and triggers a {self.tariff_config.pf_penalty_rate_pct}% utility surcharge on monthly billing.",
                        "operator_action": "1. Inspect APFC panel fuse links and contactor switching for FDR_02/04. 2. Verify microfarad capacitance of power capacitors using LCR meter. 3. Replace blown delta cells.",
                        "estimated_monthly_kwh_saving": 250.0,
                        "estimated_monthly_inr_saving": inr_saved_monthly,
                        "estimated_monthly_co2_kg_saving": round(250.0 * self.co2_factor, 1),
                        "sec_impact": "Reduces distribution feeder cable losses and eliminates DISCOM kVA penalty."
                    })
                    rec_counter += 1

                elif atype == "PHASE_IMBALANCE":
                    loss_saving_kwh = round(120.0, 1)
                    recs.append({
                        "rec_id": f"REC-{rec_counter:03d}",
                        "machine_id": mid,
                        "category": "ELECTRICAL_BALANCE",
                        "priority": "HIGH" if sev == "CRITICAL" else "MEDIUM",
                        "what_happened": f"Phase current imbalance observed at {obs_val}% (exceeds 5.0% NEMA standard limit).",
                        "why_it_matters": "Phase unbalance produces negative sequence currents, inducing heavy rotor eddy-current heating. A 5% voltage unbalance can require a 25% motor derating or causes winding insulation failure.",
                        "operator_action": "1. Check incoming MCC terminal lug torque with calibrated torque wrench. 2. Measure phase-to-phase contact resistance across starter contactor. 3. Balance auxiliary 1-phase loads across bus phases.",
                        "estimated_monthly_kwh_saving": loss_saving_kwh,
                        "estimated_monthly_inr_saving": round(loss_saving_kwh * self.tariff_config.normal_rate_inr, 2),
                        "estimated_monthly_co2_kg_saving": round(loss_saving_kwh * self.co2_factor, 1),
                        "sec_impact": "Prevents motor thermal derating and reduces feeder Joule heating."
                    })
                    rec_counter += 1

        # 2. General Tariff Load Shifting Recommendation (Calculated dynamically from TariffConfig)
        diff = self.tariff_config.peak_to_offpeak_differential
        monthly_shifted_kwh = 160.0 * 0.75 * 4.0 * 25.0  # 12,000 kWh/month typical batch heating
        shifted_saving_inr = round(monthly_shifted_kwh * max(0.0, diff), 2)

        if diff > 0.0:
            rec_what = (
                f"Induction Billet Furnace (160 kW) operates during evening Peak Tariff slot "
                f"({self.tariff_config.peak_start}:00 to {self.tariff_config.peak_end}:00 at ₹{self.tariff_config.peak_rate_inr:.2f}/kWh)."
            )
            rec_why = (
                f"Peak power costs ₹{self.tariff_config.peak_rate_inr:.2f}/kWh vs ₹{self.tariff_config.off_peak_rate_inr:.2f}/kWh Off-Peak night rate "
                f"(₹{diff:.2f}/kWh differential). Shifting batch preheating to Night Shift saves ~₹{shifted_saving_inr:,.0f}/month."
            )
            rec_action = (
                f"Shift batch billet preheating schedule from {self.tariff_config.peak_start}:00–{self.tariff_config.peak_end}:00 to Night Shift "
                f"({self.tariff_config.off_peak_start}:00–{self.tariff_config.off_peak_end}:00). Production throughput is 100% invariant."
            )
            rec_sec = "SEC remains invariant (same kWh and units), but electricity cost per unit produced drops substantially."
        else:
            rec_what = (
                f"Induction Billet Furnace (160 kW) scheduled during evening slot with peak rate ₹{self.tariff_config.peak_rate_inr:.2f}/kWh "
                f"and off-peak rate ₹{self.tariff_config.off_peak_rate_inr:.2f}/kWh."
            )
            rec_why = (
                f"No price differential exists between peak and off-peak tariffs (Δ = ₹{diff:.2f}/kWh). "
                f"Schedule load shifting produces zero financial benefit under flat or inverted tariffs."
            )
            rec_action = "Maintain current operational schedule. Tariff shifting is not economically justified under current utility rates."
            rec_sec = "SEC and cost remain invariant."

        recs.append({
            "rec_id": f"REC-{rec_counter:03d}",
            "machine_id": "FURNACE_01",
            "category": "TOD_TARIFF_LOAD_SHIFTING",
            "priority": "HIGH" if diff > 0.0 else "LOW",
            "what_happened": rec_what,
            "why_it_matters": rec_why,
            "operator_action": rec_action,
            "estimated_monthly_kwh_saving": 0.0,  # Cost saving without energy reduction!
            "estimated_monthly_inr_saving": shifted_saving_inr,
            "estimated_monthly_co2_kg_saving": 0.0,
            "sec_impact": rec_sec
        })

        return recs
