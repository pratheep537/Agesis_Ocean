from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

# Import the core engines we just built
from physics.engine import ReverseDriftEngine
from physics.imm_tracker import DarkVesselIMMTracker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

router = APIRouter()
physics_engine = ReverseDriftEngine(num_particles=2000, h3_resolution=7)
imm_tracker = DarkVesselIMMTracker(dt=1.0)

class TriageRequest(BaseModel):
    chip_id: str
    center_lat: float
    center_lon: float

class TriageResponse(BaseModel):
    status: str
    slick_detected: bool
    h3_origin_hexagons: dict
    top_suspects: list

@router.post("/api/v1/triage", response_model=TriageResponse)
async def run_triage_pipeline(payload: TriageRequest):
    logging.info(f"--- INCOMING TRIAGE REQUEST FOR CHIP {payload.chip_id} ---")
    
    # 1. AI CASCADE SIMULATION
    # In a full production run, we load the basic_unet.py and swin_unet.py here.
    # For now, we simulate the AI extracting a centroid from the provided coordinates.
    logging.info("Scout/Sniper Cascade activated...")
    slick_lat = payload.center_lat + 0.01  # Simulated offset extracted by Sniper
    slick_lon = payload.center_lon - 0.01

    # 2. PHYSICS ENGINE SDE
    logging.info("Executing Reverse Drift SDE...")
    probability_map = physics_engine.calculate_origin_probability(slick_lat, slick_lon, hours_back=6)
    
    # Get top 3 hexes for the JSON response
    top_hexes = {hex_id: count for hex_id, count in probability_map.most_common(3)}

    # 3. DARK VESSEL IMM MATCHING (Simulated DB Fetch)
    logging.info("Fetching historical AIS from PostGIS and extrapolating Dark Vessels...")
    
    # Simulating a dark vessel whose IMM dead-reckoned path intersects our top H3 hex
    top_hex_id = list(top_hexes.keys())[0]
    
    mock_suspect = {
        "mmsi": "419000123",
        "vessel_name": "GHOST_TANKER_7",
        "intersection_hex": top_hex_id,
        "historical_path": [
            [64.0, 14.5], # Ship starting position
            [64.5, 14.8],
            [65.0, 15.0], # Drives directly through the oil slick
            [65.5, 15.3]  # Current live position of the ship
        ],
        "kinematic_guilt_scores": {
            "phi_gap": 0.92,
            "phi_sog": 0.85,
            "phi_align": 0.98,
            "magic_pipe_flagged": True
        }
    }

    return TriageResponse(
        status="success",
        slick_detected=True,
        h3_origin_hexagons=top_hexes,
        top_suspects=[mock_suspect]
    )