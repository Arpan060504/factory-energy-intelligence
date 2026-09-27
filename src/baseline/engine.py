"""
Explainable Production-Normalized Energy Baseline Engine.
Builds transparent, auditable statistical baseline models relating machine power consumption
to production throughput, operational state, and operating hours.
"""

import os
import json
import logging
from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge

logger = logging.getLogger("BaselineEngine")


class BaselineModel:
    """
    Transparent production-normalized baseline model for a single machine or the full plant:
        P_expected(t) = beta_0 + beta_state * is_running(t) + beta_idle * is_idle(t) + beta_prod * prod_rate(t)
    """
    def __init__(self, machine_id: str):
        self.machine_id = machine_id
        self.intercept_: float = 0.0
        self.coef_running_: float = 0.0
        self.coef_idle_: float = 0.0
        self.coef_prod_rate_: float = 0.0
        self.is_trained: bool = False
        self.r2_score_: float = 0.0
        self.rmse_: float = 0.0

    def fit(self, df_machine: pd.DataFrame) -> "BaselineModel":
        # Filter training data to healthy baseline periods (e.g., ground_truth_anomaly == 'NONE')
        # If ground_truth_anomaly is present, train on clean data; else use full sample
        clean_df = df_machine
        if "ground_truth_anomaly" in df_machine.columns:
            clean_df = df_machine[df_machine["ground_truth_anomaly"] == "NONE"]
            if len(clean_df) < 50:
                clean_df = df_machine

        # Feature matrix: [is_running, is_idle, production_rate]
        is_running = (clean_df["machine_status"] == "RUNNING").astype(float).values
        is_idle = ((clean_df["machine_status"] == "IDLE") | (clean_df["idle_flag"] == 1)).astype(float).values
        prod_rate = clean_df["production_rate"].fillna(0.0).values

        X = np.column_stack([is_running, is_idle, prod_rate])
        y = clean_df["active_power_kw"].values

        model = Ridge(alpha=1.0)
        model.fit(X, y)

        self.intercept_ = float(model.intercept_)
        self.coef_running_ = float(model.coef_[0])
        self.coef_idle_ = float(model.coef_[1])
        self.coef_prod_rate_ = float(model.coef_[2])
        self.is_trained = True

        # Validation stats
        y_pred = model.predict(X)
        ss_tot = np.sum((y - np.mean(y))**2)
        ss_res = np.sum((y - y_pred)**2)
        self.r2_score_ = float(1.0 - (ss_res / (ss_tot + 1e-9)))
        self.rmse_ = float(np.sqrt(np.mean((y - y_pred)**2)))

        return self

    def predict_power(self, df_machine: pd.DataFrame) -> np.ndarray:
        if not self.is_trained:
            raise RuntimeError(f"BaselineModel for {self.machine_id} is not trained.")

        is_running = (df_machine["machine_status"] == "RUNNING").astype(float).values
        is_idle = ((df_machine["machine_status"] == "IDLE") | (df_machine["idle_flag"] == 1)).astype(float).values
        prod_rate = df_machine["production_rate"].fillna(0.0).values

        X = np.column_stack([is_running, is_idle, prod_rate])
        pred_p = self.intercept_ + X[:, 0] * self.coef_running_ + X[:, 1] * self.coef_idle_ + X[:, 2] * self.coef_prod_rate_
        return np.maximum(0.05, pred_p)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "machine_id": self.machine_id,
            "intercept_kw": round(self.intercept_, 3),
            "coef_running_kw": round(self.coef_running_, 3),
            "coef_idle_kw": round(self.coef_idle_, 3),
            "coef_production_rate": round(self.coef_prod_rate_, 4),
            "r2_score": round(self.r2_score_, 4),
            "rmse_kw": round(self.rmse_, 3)
        }


class FactoryBaselineEngine:
    """
    Manages baselines across all machines and evaluates deviations.
    """
    def __init__(self, models_dir: Optional[str] = None):
        self.models_dir = models_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models"
        )
        os.makedirs(self.models_dir, exist_ok=True)
        self.machine_models: Dict[str, BaselineModel] = {}

    def train_all(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        results = {}
        for mid, group in df.groupby("machine_id"):
            model = BaselineModel(str(mid)).fit(group)
            self.machine_models[str(mid)] = model
            results[str(mid)] = model.to_dict()

        # Save model coefficients
        coeff_path = os.path.join(self.models_dir, "baseline_coefficients.json")
        with open(coeff_path, "w") as f:
            json.dump(results, f, indent=2)

        return results

    def compute_deviations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates expected power, expected energy, and deviations for every record.
        """
        df_out = df.copy()
        
        # If models not trained, train now
        if not self.machine_models:
            self.train_all(df)

        expected_power = np.zeros(len(df_out))
        for mid, model in self.machine_models.items():
            mask = (df_out["machine_id"] == mid)
            if mask.any():
                expected_power[mask] = model.predict_power(df_out[mask])

        df_out["expected_power_kw"] = np.round(expected_power, 2)
        
        # Interval hours (5 min = 5/60)
        dt_hours = 5.0 / 60.0
        df_out["expected_energy_kwh"] = np.round(df_out["expected_power_kw"] * dt_hours, 4)
        
        # Deviations
        df_out["power_deviation_kw"] = np.round(df_out["active_power_kw"] - df_out["expected_power_kw"], 2)
        df_out["energy_deviation_kwh"] = np.round(df_out["energy_kwh"] - df_out["expected_energy_kwh"], 4)
        
        # Deviation %
        safe_expected = np.maximum(0.1, df_out["expected_power_kw"])
        df_out["power_deviation_pct"] = np.round(
            (df_out["power_deviation_kw"] / safe_expected) * 100.0, 2
        )

        return df_out
