"""
Three-Phase Industrial Electrical Engineering Calculations.
Implements standard IEEE/NEMA equations for power, power factor, phase current imbalance,
discrete energy integrals, and conductor Joule dissipation (cable loss) models.
"""

import math
from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd

# Conductor physical properties at 20 deg C (Ohm * mm2 / m)
CONDUCTOR_PROPERTIES = {
    "ALUMINIUM": {
        "rho_20": 0.0282,
        "alpha": 0.00403,
        "description": "EC Grade Aluminium (IS 398 / IS 7098)"
    },
    "COPPER": {
        "rho_20": 0.0175,
        "alpha": 0.00393,
        "description": "Electrolytic Tough Pitch Copper (IS 694 / IS 1554)"
    }
}


def calculate_conductor_resistance(
    length_m: float,
    cross_section_mm2: float,
    material: str = "ALUMINIUM",
    operating_temp_c: float = 50.0
) -> float:
    """
    Calculates single-conductor DC/AC resistance (Ohms) at operating temperature.
    
    Formula:
        rho_T = rho_20 * [1 + alpha * (T - 20)]
        R = rho_T * (L / A)
    
    NOTE: This is a physical model assumption for distribution feeder loss estimation,
    not a direct sensor measurement.
    """
    mat = material.upper()
    if mat not in CONDUCTOR_PROPERTIES:
        raise ValueError(f"Unknown conductor material '{material}'. Choose 'ALUMINIUM' or 'COPPER'.")
    
    props = CONDUCTOR_PROPERTIES[mat]
    rho_t = props["rho_20"] * (1.0 + props["alpha"] * (operating_temp_c - 20.0))
    r_single = rho_t * (length_m / cross_section_mm2)
    return float(r_single)


def calculate_three_phase_power(
    voltage_line_v: float,
    current_line_a: float,
    power_factor: float
) -> Dict[str, float]:
    """
    Calculates 3-phase balanced power parameters:
    - Apparent Power S (kVA) = sqrt(3) * V_L * I_L / 1000
    - Active Power P (kW) = sqrt(3) * V_L * I_L * PF / 1000
    - Reactive Power Q (kVAR) = sqrt(S^2 - P^2)
    """
    pf_clamped = max(0.01, min(1.0, power_factor))
    s_kva = (math.sqrt(3.0) * voltage_line_v * current_line_a) / 1000.0
    p_kw = s_kva * pf_clamped
    q_kvar = math.sqrt(max(0.0, s_kva**2 - p_kw**2))
    
    return {
        "apparent_power_kva": round(s_kva, 3),
        "active_power_kw": round(p_kw, 3),
        "reactive_power_kvar": round(q_kvar, 3),
        "power_factor": round(pf_clamped, 3)
    }


def calculate_phase_imbalance(
    i_r: float,
    i_y: float,
    i_b: float
) -> Dict[str, float]:
    """
    Calculates 3-phase current imbalance according to NEMA MG-1 standard:
        I_avg = (I_r + I_y + I_b) / 3
        Imbalance (%) = max(|I_phase - I_avg|) / I_avg * 100
        
    Classification:
    - <= 5%: Normal
    - 5% to 10%: Warning
    - > 10%: Critical (Motor derating or inspection required)
    """
    i_avg = (i_r + i_y + i_b) / 3.0
    if i_avg <= 0.001:
        return {
            "average_current": 0.0,
            "imbalance_pct": 0.0,
            "severity": "NORMAL"
        }
    
    max_dev = max(abs(i_r - i_avg), abs(i_y - i_avg), abs(i_b - i_avg))
    imbalance_pct = (max_dev / i_avg) * 100.0
    
    if imbalance_pct <= 5.0:
        severity = "NORMAL"
    elif imbalance_pct <= 10.0:
        severity = "WARNING"
    else:
        severity = "CRITICAL"
        
    return {
        "average_current": round(i_avg, 2),
        "imbalance_pct": round(imbalance_pct, 2),
        "severity": severity
    }


def estimate_feeder_cable_loss(
    current_avg_a: float,
    resistance_ohm: float
) -> float:
    """
    Estimates 3-phase line Joule dissipation loss in kW:
        P_loss (kW) = 3 * I_avg^2 * R / 1000
    
    CRITICAL TRANSPARENCY NOTICE:
    This is an estimated engineering calculation based on cable geometry and
    measured current, NOT a measured loss.
    """
    p_loss_kw = (3.0 * (current_avg_a**2) * resistance_ohm) / 1000.0
    return float(round(p_loss_kw, 4))


def calculate_discrete_energy(
    power_kw_series: pd.Series,
    interval_hours: float
) -> float:
    """
    Discrete energy integral:
        E (kWh) = sum(P_i * Delta_t)
    """
    return float(round(power_kw_series.sum() * interval_hours, 4))
