from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

# Import our custom modules
from schemas import TriageRequest, TriageResponse
from mock_data import get_mock_ais_dataframe
from engine import execute_vectorized_triage_pipeline

app = FastAPI(title="AEGIS-OCEAN Enterprise Triage Engine")

# Allow Pod 3 (React) to connect without CORS blocking
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/triage", response_model=TriageResponse)
async def run_triage(request: TriageRequest):
    # 1. Parse input
    coords_array = np.array(request.slick_boundary_coords)
    center_lat, center_lon = np.mean(coords_array, axis=0)
    
    # 2. In a real run, Vimal's pipeline calls the DB here.
    # We are using the mock generator so the backend always works for demo day.
    mock_ais_df = get_mock_ais_dataframe(center_lat=center_lat, center_lon=center_lon, num_ships=500)
    
    # 3. Fire the God-Mode Engine
    results, processing_time = execute_vectorized_triage_pipeline(
        slick_boundary_coords=coords_array,
        u_curr=request.u_curr,
        v_curr=request.v_curr,
        u_wind=request.u_wind,
        v_wind=request.v_wind,
        ais_dataframe=mock_ais_df,
        drift_hours=request.drift_hours
    )
    
    # 4. Return Top 3 matches
    return {
        "status": "success",
        "latency_ms": processing_time,
        "suspect_count": len(results),
        "top_suspects": results[:3] 
    }