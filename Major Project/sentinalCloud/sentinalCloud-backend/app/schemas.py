"""
Pydantic models for data validation and serialization.
These models define the shape of all API requests and responses, providing
automatic validation and API documentation.
"""
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field

# --- Alert Schemas ---

class AlertSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class AlertStatus(str, Enum):
    NEW = "new"
    VIEWED = "viewed"
    CLOSED = "closed"

class AlertSchema(BaseModel):
    id: int
    timestamp: datetime
    severity: AlertSeverity
    type: str
    source_ip: str
    status: AlertStatus
    class Config: from_attributes = True

class PaginatedAlertsResponse(BaseModel):
    alerts: List[AlertSchema]
    total: int
    page: int
    limit: int

# --- Detection & Prediction Schemas ---

class DetectionRequest(BaseModel):
    """Defines the structure for a request to the detection endpoint."""
    features: List[List[float]] = Field(
        ...,
        description="A list of feature vectors. Each inner list is one sample.",
        example=[[0.1, 87321, 5, 3, 430, 0.5, ...]]
    )

# --- Post-processing / Enriched Prediction Schemas ---

class EnrichedPredictionSample(BaseModel):
    """Defines the structure for a single, enriched prediction sample."""
    index: int
    label: str
    attack_probability: float = Field(..., description="The final weighted average attack probability.")
    severity: str = Field(..., description="A human-readable severity level (info, low, medium, high).")
    per_model_probs: Dict[str, float] = Field(..., description="A dictionary mapping model names to their probability scores.")
    meta: Optional[Dict[str, Any]] = None

class PredictionSummary(BaseModel):
    """Defines the structure for the summary part of the response."""
    n_samples: int
    n_models: int

class EnrichedPredictionResponse(BaseModel):
    """Defines the final, user-facing structure for the /detect API response."""
    summary: PredictionSummary
    samples: List[EnrichedPredictionSample]

# --- Explainability (SHAP) Schemas ---

class ShapFeatureSchema(BaseModel):
    """Schema for a single feature's contribution in a SHAP explanation."""
    feature: str
    shap_value: float
    sign: str = Field(..., description='"increases_attack" or "reduces_attack"')

class ExplanationResponseSchema(BaseModel):
    """Schema for the final response from the explainability endpoint."""
    method: str
    top_features: List[ShapFeatureSchema]
    raw_shap_values: List[float]
    feature_names: List[str]

# --- Statistics Schemas ---

class SummaryStatsSchema(BaseModel):
    """Schema for the main dashboard KPI stats."""
    total_packets_analyzed: int
    attacks_detected: int
    system_uptime_hours: float
    benign_traffic_gb: float

class TrafficOverTimeDataset(BaseModel):
    label: str
    data: List[int]

class TrafficOverTimeResponse(BaseModel):
    labels: List[str]
    datasets: List[TrafficOverTimeDataset]

class AttackDistributionResponse(BaseModel):
    labels: List[str]
    data: List[int]

# --- Simulation Schemas ---

class SimulateAttackRequest(BaseModel):
    """Defines the structure for a request to the frontend simulation endpoint."""
    type: str = Field("DDoS", description="The type of attack to simulate.")
    intensity: str = Field("high", description="The intensity of the simulated attack.")

class SimulationResponse(BaseModel):
    """Defines the structure for a backend simulation response."""
    message: str
    data: Dict[str, Any]
    source: str

# --- Heuristic Enrichment Schemas ---

class FeatureRowSchema(BaseModel):
    """Defines the expected features for heuristic analysis."""
    dst_port: Optional[int] = -1
    tcp_flags: Optional[str] = ""
    packet_count: Optional[float] = 0.0
    duration: Optional[float] = 0.0
    src_bytes: Optional[float] = 0.0
    dst_bytes: Optional[float] = 0.0

class AttackEnrichmentInfo(BaseModel):
    """Defines the structured output for enriched attack information."""
    attack_type: str
    reason: str
    theory: str
    mitigation_steps: List[str]