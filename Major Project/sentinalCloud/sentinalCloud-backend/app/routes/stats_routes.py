"""
API routes for serving aggregated statistical data for the dashboard.
"""
import random
from datetime import datetime, timedelta
from fastapi import APIRouter

from app.schemas import (
    SummaryStatsSchema,
    TrafficOverTimeResponse,
    AttackDistributionResponse
)

router = APIRouter(
    prefix="/stats",
    tags=["Statistics"]
)

@router.get("/summary", response_model=SummaryStatsSchema)
async def get_summary_stats():
    """Provides key summary statistics for the main dashboard display."""
    return {
        "total_packets_analyzed": random.randint(1_500_000, 2_000_000),
        "attacks_detected": random.randint(350, 500),
        "system_uptime_hours": 72.5,
        "benign_traffic_gb": round(random.uniform(80.0, 120.0), 2)
    }

@router.get("/traffic-over-time", response_model=TrafficOverTimeResponse)
async def get_traffic_over_time():
    """Provides time-series data for traffic volume for the last 12 hours."""
    labels = []
    benign_data = []
    attack_data = []
    now = datetime.now()
    
    for i in range(12, 0, -1):
        timestamp = now - timedelta(hours=i)
        labels.append(timestamp.strftime("%H:%M"))
        benign_data.append(random.randint(5000, 15000) - (i * 200))
        attack_data.append(random.randint(100, 500) + (i * random.randint(10, 30)))
        
    return {
        "labels": labels,
        "datasets": [
            {"label": "Benign Traffic", "data": benign_data},
            {"label": "Malicious Traffic", "data": attack_data}
        ]
    }

@router.get("/attack-distribution", response_model=AttackDistributionResponse)
async def get_attack_distribution():
    """Provides data on the distribution of different attack types."""
    data = {
        "DDoS": random.randint(150, 200),
        "Port Scan": random.randint(80, 120),
        "Botnet C&C": random.randint(50, 75),
        "SQL Injection": random.randint(20, 40),
        "Other": random.randint(10, 25)
    }
    return {
        "labels": list(data.keys()),
        "data": list(data.values())
    }