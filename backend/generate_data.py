import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_cadastre_compliant_ais():
    print("[FORGE] 🔨 Generating SIH-Compliant Marine Cadastre Synthetic AIS...")
    os.makedirs("data", exist_ok=True)
    
    INCIDENT_TIME = datetime.strptime("2019-09-15 12:00:00", "%Y-%m-%d %H:%M:%S")
    num_innocent = 5000
    np.random.seed(42)
    
    df_innocent = pd.DataFrame({
        "mmsi": np.random.randint(100000000, 999999999, num_innocent).astype(str),
        "vessel_name": ["UNKNOWN_VESSEL"] * num_innocent,
        "imo": np.random.randint(1000000, 9999999, num_innocent).astype(str),
        "vessel_type": np.random.choice(["Cargo", "Tanker", "Fishing", "Passenger"], num_innocent),
        "BaseDateTime": [INCIDENT_TIME - timedelta(hours=np.random.uniform(0, 12)) for _ in range(num_innocent)],
        "lat": np.random.uniform(-20.6, -20.2, num_innocent),
        "lon": np.random.uniform(57.5, 58.0, num_innocent),
        "sog": np.random.uniform(0.5, 15.0, num_innocent),
        "cog": np.random.uniform(0.0, 360.0, num_innocent),
        "gap_hr": np.random.uniform(0.1, 4.0, num_innocent)
    })
    
    df_guilty = pd.DataFrame({
        "mmsi": ["353136000"],
        "vessel_name": ["MV WAKASHIO"],
        "imo": ["9337119"],
        "vessel_type": ["Tanker"],
        "BaseDateTime": [INCIDENT_TIME],
        "lat": [-20.437],
        "lon": [57.745],
        "sog": [3.2],       
        "cog": [110.0],     
        "gap_hr": [0.5]     
    })
    
    df_final = pd.concat([df_innocent, df_guilty]).sample(frac=1).reset_index(drop=True)
    
    file_path = "data/wakashio_ais.parquet"
    df_final.to_parquet(file_path, engine="pyarrow")
    
    print(f"[FORGE] 🟢 Vault sealed. {len(df_final)} Marine Cadastre compliant ships saved.")

if __name__ == "__main__":
    generate_cadastre_compliant_ais()