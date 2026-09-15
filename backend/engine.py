import numpy as np
import h3
import pandas as pd
import time

def execute_vectorized_triage_pipeline(
    slick_boundary_coords: np.ndarray, 
    u_curr: float, v_curr: float, u_wind: float, v_wind: float, 
    ais_dataframe: pd.DataFrame, 
    drift_hours: float = 6.0, n_particles: int = 2000, dt_hours: float = 0.5, eta_error: float = 0.30
) -> list:
    
    start_time = time.time()
    
    # ---------------------------------------------------------
    # 1. STOCHASTIC ADVECTION (FP16 Memory Optimization)
    # ---------------------------------------------------------
    min_lat, min_lon = np.min(slick_boundary_coords, axis=0)
    max_lat, max_lon = np.max(slick_boundary_coords, axis=0)
    
    # Force float16 to slash memory complexity by 75%
    particles = np.column_stack((
        np.random.uniform(min_lat, max_lat, n_particles),
        np.random.uniform(min_lon, max_lon, n_particles)
    )).astype(np.float16)
    
    km_per_deg = 111.32
    u_drift_deg = -((u_curr + 0.03 * u_wind) * 3.6) / km_per_deg
    v_drift_deg = -((v_curr + 0.03 * v_wind) * 3.6) / km_per_deg
    
    # Vectorized SDE Time Steps (No particle loops)
    steps = int(drift_hours / dt_hours)
    for _ in range(steps):
        # Calculate stochastic diffusion
        noise = np.random.normal(0, 1, (n_particles, 2)).astype(np.float16)
        sigma = eta_error * np.sqrt(u_drift_deg**2 + v_drift_deg**2)
        
        particles[:, 0] += (v_drift_deg * dt_hours + noise[:, 0] * sigma * np.sqrt(dt_hours))
        particles[:, 1] += (u_drift_deg * dt_hours + noise[:, 1] * sigma * np.sqrt(dt_hours))

    # ---------------------------------------------------------
    # 2. THE VECTORIZED PRE-FILTER (Bypassing the Pandas Apply Bottleneck)
    # ---------------------------------------------------------
    p_min_lat, p_min_lon = np.min(particles, axis=0)
    p_max_lat, p_max_lon = np.max(particles, axis=0)

    # O(1) Vectorized slice: Instantly drop any ship not physically near the envelope
    candidates = ais_dataframe[
        (ais_dataframe['lat'] >= p_min_lat - 0.1) & (ais_dataframe['lat'] <= p_max_lat + 0.1) &
        (ais_dataframe['lon'] >= p_min_lon - 0.1) & (ais_dataframe['lon'] <= p_max_lon + 0.1)
    ].copy()

    if candidates.empty: 
        return [], int((time.time() - start_time) * 1000)

    # ---------------------------------------------------------
    # 3. DIRECT PARTICLE HASHING & INTERSECTION
    # ---------------------------------------------------------
    # Now we only run the H3 hash on the surviving ships, taking milliseconds instead of seconds
    h3_search_set = {
        h3.str_to_int(h3.latlng_to_cell(float(lat), float(lon), res=7)) 
        for lat, lon in particles
    }
    
    # List comprehension is significantly faster than pandas .apply() for C-bindings
    candidates['h3_int'] = [
        h3.str_to_int(h3.latlng_to_cell(lat, lon, res=7)) 
        for lat, lon in zip(candidates['lat'], candidates['lon'])
    ]
    
    suspects = candidates[candidates['h3_int'].isin(h3_search_set)].copy()

    if suspects.empty: 
        return [], int((time.time() - start_time) * 1000)

    # ---------------------------------------------------------
    # 4. KINEMATIC PCA TRIAGE (Untouched - Brilliant Math)
    # ---------------------------------------------------------
    centered = slick_boundary_coords - np.mean(slick_boundary_coords, axis=0)
    _, eigvecs = np.linalg.eigh(np.cov(centered, rowvar=False))
    slick_angle = np.degrees(np.arctan2(eigvecs[1, -1], eigvecs[0, -1])) % 180

    sog = suspects['sog'].values
    gap = suspects['gap_hr'].values
    cog = suspects['cog'].values
    
    phi_sog = np.where((sog >= 2.0) & (sog <= 5.0), 1.0, np.exp(-((sog - 3.5)**2) / 4.5))
    phi_gap = np.minimum(gap / 2.0, 1.0)
    phi_align = (1.0 + np.cos(2 * np.radians(cog - slick_angle))) / 2.0
    
    suspects['triage_score'] = (0.45 * phi_sog) + (0.45 * phi_gap) + (0.10 * phi_align)
    
    top_results = suspects.sort_values(by='triage_score', ascending=False).to_dict('records')
    latency = int((time.time() - start_time) * 1000)
    
    return top_results, latency
