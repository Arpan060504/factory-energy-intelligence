"""
Machine Health Assessment Module.
Computes an auditable, transparent composite health index (0 - 100) based on
current deviation, power deviation, thermal rise, vibration RMS, and phase unbalance.

DISCLAIMER / ENGINEERING HONESTY:
This score is an engineering heuristic model assumption for maintenance prioritization.
It is NOT an OEM-certified failure probability or remaining useful life (RUL) prediction.
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd


class MachineHealthEngine:
    def __init__(
        self,
        weight_current: float = 0.20,
        weight_power: float = 0.25,
        weight_temp: float = 0.25,
        weight_vib: float = 0.20,
        weight_imbalance: float = 0.10
    ):
        self.w_i = weight_current
        self.w_p = weight_power
        self.w_t = weight_temp
        self.w_v = weight_vib
        self.w_imb = weight_imbalance

    def calculate_record_health_score(self, row: pd.Series) -> Dict[str, Any]:
        """
        Calculates instantaneous health score (0 to 100) for a single telemetry record.
        """
        status = str(row.get("machine_status", "RUNNING"))
        
        if status == "OFF":
            return {
                "health_score": 100.0,
                "health_status": "NORMAL",
                "message": "Equipment de-energized. System in normal standby."
            }

        p_dev = abs(float(row.get("power_deviation_pct", 0.0)))
        pen_p = float(np.clip((p_dev - 5.0) * 3.0, 0.0, 100.0)) if p_dev > 5.0 else 0.0

        temp = float(row.get("temperature", 40.0))
        pen_t = float(np.clip((temp - 48.0) * 3.5, 0.0, 100.0)) if temp > 48.0 else 0.0

        vib = float(row.get("vibration", 1.5))
        pen_v = float(np.clip((vib - 2.5) * 28.0, 0.0, 100.0)) if vib > 2.5 else 0.0

        imb = float(row.get("current_imbalance_pct", 1.5))
        pen_imb = float(np.clip((imb - 4.5) * 8.0, 0.0, 100.0)) if imb > 4.5 else 0.0

        pen_i = pen_p * 0.9

        total_penalty = (
            self.w_i * pen_i +
            self.w_p * pen_p +
            self.w_t * pen_t +
            self.w_v * pen_v +
            self.w_imb * pen_imb
        )

        health_score = round(max(5.0, min(100.0, 100.0 - total_penalty)), 1)

        if health_score >= 80.0:
            status_label = "NORMAL"
            msg = "Operating parameters within standard manufacturer tolerance."
        elif health_score >= 60.0:
            status_label = "WARNING"
            msg = "Possible mechanical/electrical issue detected. Inspection recommended."
        else:
            status_label = "CRITICAL"
            msg = "Significant operational degradation detected. Maintenance inspection required."

        return {
            "health_score": health_score,
            "health_status": status_label,
            "message": msg,
            "penalty_power": round(pen_p, 1),
            "penalty_temp": round(pen_t, 1),
            "penalty_vib": round(pen_v, 1),
            "penalty_imbalance": round(pen_imb, 1)
        }

    def evaluate_fleet_health(self, df_with_baseline: pd.DataFrame) -> pd.DataFrame:
        """
        Fast vectorized computation of rolling 24-hour health score and latest status for every machine.
        """
        results = []
        df = df_with_baseline.copy()
        
        for mid, group in df.groupby("machine_id"):
            group = group.sort_values("timestamp")
            recent_group = group.tail(288)  # Last 24 hours
            latest_row = group.iloc[-1]
            latest_health = self.calculate_record_health_score(latest_row)

            # Vectorized health computation for recent 288 samples
            p_dev = np.abs(recent_group["power_deviation_pct"].fillna(0.0).values)
            pen_p = np.clip((p_dev - 5.0) * 3.0, 0.0, 100.0)

            temp = recent_group["temperature"].values
            pen_t = np.clip((temp - 48.0) * 3.5, 0.0, 100.0)

            vib = recent_group["vibration"].values
            pen_v = np.clip((vib - 2.5) * 28.0, 0.0, 100.0)

            imb = recent_group["current_imbalance_pct"].values
            pen_imb = np.clip((imb - 4.5) * 8.0, 0.0, 100.0)

            pen_i = pen_p * 0.9

            is_off = (recent_group["machine_status"] == "OFF").values
            total_penalty = (
                self.w_i * pen_i +
                self.w_p * pen_p +
                self.w_t * pen_t +
                self.w_v * pen_v +
                self.w_imb * pen_imb
            )
            scores = np.where(is_off, 100.0, np.clip(100.0 - total_penalty, 5.0, 100.0))
            avg_24h_score = round(float(np.mean(scores)), 1)

            results.append({
                "machine_id": mid,
                "machine_name": latest_row.get("machine_name", mid),
                "feeder_id": latest_row.get("feeder_id", "FDR_01"),
                "machine_type": latest_row.get("machine_type", "GENERIC"),
                "latest_health_score": latest_health["health_score"],
                "rolling_24h_health_score": avg_24h_score,
                "health_status": latest_health["health_status"],
                "diagnostic_message": latest_health["message"],
                "current_temperature_c": latest_row.get("temperature", 0.0),
                "current_vibration_mms": latest_row.get("vibration", 0.0),
                "current_imbalance_pct": latest_row.get("current_imbalance_pct", 0.0),
                "power_deviation_pct": latest_row.get("power_deviation_pct", 0.0)
            })

        return pd.DataFrame(results).sort_values("latest_health_score").reset_index(drop=True)
