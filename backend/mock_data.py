import pandas as pd
import numpy as np

def get_mock_ais_dataframe(center_lat: float, center_lon: float, num_ships: int = 500) -> pd.DataFrame:
    """
    Generates a synthetic swarm of ships around the oil slick area.
    This simulates what Pod 1 (Vimal) will eventually pull from Global Fishing Watch.
    """
    # Scatter ships within roughly 1 degree (~111km) of the slick
    lats = np.random.uniform(center_lat - 1.0, center_lat + 1.0, num_ships)
    lons = np.random.uniform(center_lon - 1.0, center_lon + 1.0, num_ships)
    
    # Generate realistic ship behaviors
    sogs = np.random.uniform(0.0, 15.0, num_ships) # Speeds from 0 to 15 knots
    cogs = np.random.uniform(0.0, 360.0, num_ships) # Headings
    gaps = np.random.exponential(1.5, num_ships) # AIS blackout times (dark fleet)
    
    # Inject one "Guilty" ship that perfectly matches our physics model parameters
    # Let's put it exactly at the slick origin, moving at 3.5 knots, heading 45 deg, with a 4 hour AIS gap
    lats[0], lons[0] = center_lat + 0.1, center_lon + 0.1 
    sogs[0], cogs[0], gaps[0] = 3.5, 45.0, 4.0
    
    df = pd.DataFrame({
        'vessel_id': np.arange(1000, 1000 + num_ships),
        'lat': lats,
        'lon': lons,
        'sog': sogs,
        'cog': cogs,
        'gap_hr': gaps
    })
    
    return df