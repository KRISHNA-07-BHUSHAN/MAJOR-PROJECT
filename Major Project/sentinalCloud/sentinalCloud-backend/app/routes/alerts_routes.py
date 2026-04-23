# src/sentinalCloud-backend/app/routes/alerts_routes.py (Complete & Refined)
"""
API routes for fetching security alerts.
"""
from fastapi import APIRouter, Query, HTTPException
import datetime
from typing import List, Dict, Any # Import types for clarity and validation

router = APIRouter()

# Mock data - dynamically generate timestamps relative to now for freshness
# Use unique string IDs
MOCK_ALERTS_STORE = [
    {"id": "alert_1", "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=1)).isoformat() + "Z", "severity": "High", "type": "DDoS", "source_ip": "198.51.100.12", "status": "new"},
    {"id": "alert_2", "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=2, seconds=15)).isoformat() + "Z", "severity": "Medium", "type": "Port Scan", "source_ip": "203.0.113.55", "status": "new"},
    {"id": "alert_3", "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=5, seconds=30)).isoformat() + "Z", "severity": "Low", "type": "SQL Injection Attempt", "source_ip": "192.0.2.143", "status": "viewed"},
    {"id": "alert_4", "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=8)).isoformat() + "Z", "severity": "High", "type": "Botnet C&C", "source_ip": "198.51.100.201", "status": "new"},
    {"id": "alert_5", "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=11, seconds=50)).isoformat() + "Z", "severity": "Medium", "type": "Malware Beacon", "source_ip": "203.0.113.89", "status": "viewed"},
    {"id": "alert_6", "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=15, seconds=55)).isoformat() + "Z", "severity": "High", "type": "Ransomware Activity", "source_ip": "198.51.100.44", "status": "new"},
    {"id": "alert_7", "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=20)).isoformat() + "Z", "severity": "Low", "type": "Anomalous Login", "source_ip": "192.0.2.210", "status": "viewed"},
    # Add more alerts to test pagination
    {"id": "alert_8", "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=22)).isoformat() + "Z", "severity": "Medium", "type": "XSS Attempt", "source_ip": "198.51.100.12", "status": "new"},
    {"id": "alert_9", "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=25)).isoformat() + "Z", "severity": "High", "type": "DDoS", "source_ip": "203.0.113.55", "status": "new"},
    {"id": "alert_10", "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=28)).isoformat() + "Z", "severity": "Low", "type": "Port Scan", "source_ip": "192.0.2.143", "status": "viewed"},
    {"id": "alert_11", "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=30)).isoformat() + "Z", "severity": "High", "type": "Botnet C&C", "source_ip": "198.51.100.201", "status": "new"},
    {"id": "alert_12", "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=33)).isoformat() + "Z", "severity": "Medium", "type": "Malware Beacon", "source_ip": "203.0.113.89", "status": "viewed"},
]

# --- Route Definition ---
# Register the function for both paths: '/' (relative to prefix) and '' (just the prefix)
@router.get("/", include_in_schema=False) # Handles /api/alerts/
@router.get("")                          # Handles /api/alerts
async def get_alerts(
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    limit: int = Query(10, ge=1, le=100, description="Number of alerts per page (1-100)")
) -> Dict[str, Any]: # Type hint for the response dictionary
    """
    Returns a paginated list of recent security alerts, sorted by most recent first.
    """
    # Sort alerts descending by timestamp to get recent ones first
    # In a real app, the database query would handle sorting and pagination
    sorted_alerts = sorted(MOCK_ALERTS_STORE, key=lambda x: x["timestamp"], reverse=True)

    # Calculate start and end index for pagination
    start_index = (page - 1) * limit
    end_index = start_index + limit

    # Slice the sorted mock data
    paginated_alerts = sorted_alerts[start_index:end_index]

    # Handle cases where the page number is too high
    if start_index >= len(sorted_alerts) and page > 1:
         # Optionally raise an error or return an empty list
         # raise HTTPException(status_code=404, detail=f"Page {page} not found.")
         paginated_alerts = [] # Return empty list for out-of-bounds pages

    # Return the data in a structured response
    return {
        "alerts": paginated_alerts,
        "total": len(sorted_alerts),
        "page": page,
        "limit": limit,
        "totalPages": (len(sorted_alerts) + limit - 1) // limit # Calculate total pages
    }

# You could add other alert-related routes here later, e.g.,
# @router.get("/{alert_id}")
# async def get_alert_details(alert_id: str): ...
#
# @router.patch("/{alert_id}")
# async def update_alert_status(alert_id: str, status_update: dict): ...