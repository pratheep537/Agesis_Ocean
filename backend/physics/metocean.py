import requests
import math
import logging
from typing import Tuple, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def calculate_uv_vectors(speed: float, direction_degrees: float) -> Tuple[float, float]:
    """
    Converts meteorological speed and direction into U (East/West) and V (North/South) vectors.
    """
    rad = math.radians(direction_degrees)
    u_vector = -speed * math.sin(rad)
    v_vector = -speed * math.cos(rad)
    return u_vector, v_vector

def fetch_live_metocean(lat: float, lon: float) -> Dict[str, float]:
    """
    Fetches real-time wind and ocean current data for a specific coordinate.
    """
    logging.info(f"Fetching live metocean telemetry for Coordinates: {lat}, {lon}")
    
    marine_url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&current=ocean_current_velocity,ocean_current_direction"
    wind_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=wind_speed_10m,wind_direction_10m"

    try:
        marine_res = requests.get(marine_url, timeout=5).json()
        wind_res = requests.get(wind_url, timeout=5).json()

        current_speed = marine_res['current']['ocean_current_velocity'] # km/h
        current_dir = marine_res['current']['ocean_current_direction'] # degrees
        
        wind_speed = wind_res['current']['wind_speed_10m'] # km/h
        wind_dir = wind_res['current']['wind_direction_10m'] # degrees

        u_current, v_current = calculate_uv_vectors(current_speed, current_dir)
        u_wind, v_wind = calculate_uv_vectors(wind_speed, wind_dir)

        # Normalize velocity (Approx: 1 degree latitude = 111 km) for SDE coordinates
        km_to_deg = 1 / 111.0

        return {
            "u_current": u_current * km_to_deg,
            "v_current": v_current * km_to_deg,
            "u_wind": u_wind * km_to_deg,
            "v_wind": v_wind * km_to_deg
        }

    except Exception as e:
        logging.warning(f"Metocean API failed/timed out. Injecting fallback physics constants. Error: {e}")
        return {"u_current": -0.002, "v_current": -0.0015, "u_wind": -0.04, "v_wind": 0.02}

# --- Test Execution Block ---
if __name__ == "__main__":
    # Test for a coordinate in the Arabian Sea
    env = fetch_live_metocean(15.0, 65.0)
    logging.info(f"Physics Environment Vectors: {env}")