from pydantic import BaseModel
from typing import List, Dict, Any

class TriageRequest(BaseModel):
    slick_boundary_coords: List[List[float]] # [[lat, lon], [lat, lon], ...]
    u_curr: float
    v_curr: float
    u_wind: float
    v_wind: float
    drift_hours: float = 6.0

class SuspectVessel(BaseModel):
    vessel_id: int
    triage_score: float
    lat: float
    lon: float
    sog: float
    cog: float
    gap_hr: float

class TriageResponse(BaseModel):
    status: str
    latency_ms: int
    suspect_count: int
    top_suspects: List[SuspectVessel]