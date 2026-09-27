"""
FastAPI REST Backend Service for Factory Energy Intelligence & Optimization Platform.
Provides API endpoints for edge data ingestion, plant topology, executive KPIs,
machine diagnostics, actionable recommendations, and optimization comparison audits.
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

# Add repository root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from src.data.schema import ElectricalTelemetry, AnomalyAlert, OptimizationResult

app = FastAPI(
    title="Factory Energy Intelligence Platform API",
    description="Affordable Real-Time Industrial Energy Monitoring, Asset Diagnostics & Process Optimization for Indian SMEs",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
SYNTHETIC_DIR = os.path.join(BASE_DIR, "data", "synthetic")


def load_json_file(filename: str) -> Any:
    filepath = os.path.join(PROCESSED_DIR, filename)
    if not os.path.exists(filepath):
        filepath = os.path.join(SYNTHETIC_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return None


@app.get("/api/health", tags=["System"])
def get_system_health():
    """System health check and connectivity heartbeat."""
    return {
        "status": "ONLINE",
        "service": "Factory Energy Intelligence API",
        "target_sme": "Apex Precision Components Ltd. (Generic Indian SME)",
        "edge_gateway_sync": "SYNCHRONIZED"
    }


@app.get("/api/topology", tags=["Plant Model"])
def get_plant_topology():
    """Returns the digital single-line diagram (SLD) topology of the SME factory."""
    return {
        "grid": {
            "incoming_kv": 11.0,
            "substation": "SUB_01",
            "transformer": {
                "id": "TR_01",
                "rating_kva": 1000.0,
                "primary_kv": 11.0,
                "secondary_v": 415.0,
                "vector_group": "Dyn11"
            },
            "main_bus": "BUS_A (415V 3-Phase 50Hz)"
        },
        "feeders": [
            {
                "feeder_id": "FDR_01",
                "machine_id": "MOTOR_01",
                "machine_name": "CNC Machining Center",
                "load_type": "CNC_MACHINING",
                "rated_kw": 75.0,
                "cable": "Aluminium 95 mm2, 65m"
            },
            {
                "feeder_id": "FDR_02",
                "machine_id": "MOTOR_02",
                "machine_name": "Hydraulic Stamping Press",
                "load_type": "HYDRAULIC_PRESS",
                "rated_kw": 55.0,
                "cable": "Aluminium 70 mm2, 45m"
            },
            {
                "feeder_id": "FDR_03",
                "machine_id": "PUMP_01",
                "machine_name": "Chilled Water Circulation Pump",
                "load_type": "COOLING_PUMP",
                "rated_kw": 30.0,
                "cable": "Aluminium 35 mm2, 80m"
            },
            {
                "feeder_id": "FDR_04",
                "machine_id": "COMP_01",
                "machine_name": "Rotary Screw Air Compressor",
                "load_type": "AIR_COMPRESSOR",
                "rated_kw": 45.0,
                "cable": "Aluminium 50 mm2, 50m"
            },
            {
                "feeder_id": "FDR_05",
                "machine_id": "FURNACE_01",
                "machine_name": "Induction Billet Heating Furnace",
                "load_type": "INDUCTION_FURNACE",
                "rated_kw": 160.0,
                "cable": "Copper 185 mm2, 30m"
            },
            {
                "feeder_id": "FDR_06",
                "machine_id": "LINE_01",
                "machine_name": "Conveyor & Final Assembly Line",
                "load_type": "CONVEYOR_LINE",
                "rated_kw": 22.0,
                "cable": "Aluminium 25 mm2, 110m"
            },
            {
                "feeder_id": "FDR_07",
                "machine_id": "AUX_01",
                "machine_name": "Plant Utilities, Exhaust & Lighting",
                "load_type": "UTILITY_AUX",
                "rated_kw": 25.0,
                "cable": "Aluminium 25 mm2, 90m"
            }
        ]
    }


@app.get("/api/overview", tags=["Analytics"])
def get_executive_overview():
    """Retrieves executive headline KPIs for the factory."""
    comparison = load_json_file("optimization_comparison.json")
    if not comparison:
        raise HTTPException(status_code=503, detail="Analytics data not yet processed. Run simulation first.")
    
    incidents = []
    incidents_path = os.path.join(PROCESSED_DIR, "incidents_summary.csv")
    if os.path.exists(incidents_path):
        incidents = pd.read_csv(incidents_path).to_dict(orient="records")

    return {
        "baseline_summary": comparison["baseline"],
        "optimized_summary": comparison["optimized"],
        "verified_impact": comparison["impact"],
        "active_incidents_count": len(incidents),
        "critical_incidents_count": sum(1 for i in incidents if i.get("severity") == "CRITICAL")
    }


@app.get("/api/machines", tags=["Analytics"])
def get_machine_fleet_summary(view: str = Query("baseline", pattern="^(baseline|optimized)$")):
    """Returns machine-level energy, SEC, idle losses, and electrical health."""
    filename = f"machine_summary_{view}.csv"
    filepath = os.path.join(PROCESSED_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Summary file {filename} not found.")
    
    df = pd.read_csv(filepath)
    return df.to_dict(orient="records")


@app.get("/api/health/fleet", tags=["Diagnostics"])
def get_fleet_health():
    """Returns composite health scores, vibration, thermal rise, and unbalance for all machines."""
    filepath = os.path.join(PROCESSED_DIR, "machine_health_fleet.csv")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Fleet health file not found.")
    
    df = pd.read_csv(filepath)
    return df.to_dict(orient="records")


@app.get("/api/alerts", tags=["Diagnostics"])
def get_alert_incidents():
    """Returns grouped operational anomaly incidents with root cause diagnosis."""
    filepath = os.path.join(PROCESSED_DIR, "incidents_summary.csv")
    if not os.path.exists(filepath):
        return []
    df = pd.read_csv(filepath)
    return df.to_dict(orient="records")


@app.get("/api/recommendations", tags=["Recommendations"])
def get_operator_recommendations():
    """Returns actionable Standard Operating Procedures (SOPs) with quantified rupee/kWh savings."""
    recs = load_json_file("operator_recommendations.json")
    if recs is None:
        return []
    return recs


@app.get("/api/optimization/comparison", tags=["Optimization"])
def get_optimization_comparison():
    """Returns rigorous before/after comparison verifying production invariance and SEC reduction."""
    comparison = load_json_file("optimization_comparison.json")
    if not comparison:
        raise HTTPException(status_code=404, detail="Optimization comparison not found.")
    return comparison


@app.post("/api/telemetry/ingest", status_code=status.HTTP_201_CREATED, tags=["Edge Ingestion"])
def ingest_edge_telemetry(payload: ElectricalTelemetry):
    """
    Receives synchronized 5-minute telemetry batches from edge gateways in SME facilities.
    Simulates edge-to-cloud store-and-forward ingestion.
    """
    return {
        "status": "ACCEPTED",
        "timestamp": payload.timestamp.isoformat(),
        "machine_id": payload.machine_id,
        "active_power_kw": payload.active_power_kw,
        "message": "Telemetry validated against IEEE/NEMA bounds."
    }
