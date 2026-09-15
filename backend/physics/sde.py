import numpy as np
import time
from api.config import settings

def run_time_reversal(lat: float, lon: float, hours_back: float = 12.0) -> dict:
    """
    Advanced Euler-Maruyama Stochastic Differential Equation (SDE) Time-Reversal Engine.
    Simulates multi-step backward advection and stochastic turbulent diffusion 
    for oil slick forensic reconstruction.
    
    Physics Model:
        dX = - [ U(x,y) + (alpha * W_wind) ] dt + sqrt(2 * K * |dt|) * dW
    """
    start_time = time.time()
    print(f"[PHYSICS] ⚛️ Initializing Advanced SDE Engine ({settings.PARTICLE_COUNT} particles, {hours_back}h backtrace)...")
    
    np.random.seed(42)
    n_particles = settings.PARTICLE_COUNT
    n_steps = 60  # Resolution of time steps over the backtrace window
    
    # Total time in seconds, split into negative time steps for backward integration
    total_time_sec = hours_back * 3600.0
    dt = - (total_time_sec / n_steps) 
    
    # Initialize particle cloud precisely at the detected satellite spill anomaly coordinates
    # Shape: (n_particles, 2) -> [latitude, longitude]
    particles = np.column_stack((
        np.full(n_particles, lat),
        np.full(n_particles, lon)
    ))
    
    # Add initial spatial uncertainty corresponding to pixel resolution of Sentinel-1 SAR (~10 meters / ~0.0001 deg)
    particles += np.random.normal(0, 0.0005, size=particles.shape)
    
    # Environmental Mock Vectors for the Region (e.g., Western Indian Ocean / Mauritius Sector)
    # Prevailing current velocity vector [Eastward m/s, Northward m/s]
    current_u = 0.35  
    current_v = -0.15 
    
    # Prevailing wind vector components (m/s)
    wind_u = 4.2
    wind_v = 2.1
    
    # Effective drift vector combining currents and windage coefficient (alpha)
    alpha = settings.WINDAGE_COEFF
    drift_u = current_u + (alpha * wind_u)
    drift_v = current_v + (alpha * wind_v)
    
    # Conversion factor: meters to degrees latitude/longitude roughly at equator/subtropics
    # 1 degree latitude ~= 111,320 meters
    meters_to_deg_lat = 1.0 / 111320.0
    meters_to_deg_lon = 1.0 / (111320.0 * np.cos(np.radians(lat)))
    
    # Horizontal eddy diffusion coefficient (m^2/s) for open ocean turbulence
    K_diffusion = 12.5 
    diffusion_scale = np.sqrt(2.0 * K_diffusion * abs(dt))
    
    # ---------------------------------------------------------
    # EULER-MARUYAMA NUMERICAL INTEGRATION LOOP (BACKWARD IN TIME)
    # ---------------------------------------------------------
    for _ in range(n_steps):
        # 1. Deterministic Advection component (scaled to degrees per timestep)
        d_lat_adv = drift_v * dt * meters_to_deg_lat
        d_lon_adv = drift_u * dt * meters_to_deg_lon
        
        # 2. Stochastic Diffusion component (Wiener process / Brownian motion via normal distribution)
        # Vectorized across all particles simultaneously (Zero loops over individual particles)
        rand_lat = np.random.normal(0, 1, n_particles) * diffusion_scale * meters_to_deg_lat
        rand_lon = np.random.normal(0, 1, n_particles) * diffusion_scale * meters_to_deg_lon
        
        # 3. Update particle coordinate matrix
        particles[:, 0] += d_lat_adv + rand_lat
        particles[:, 1] += d_lon_adv + rand_lon

    # Compute statistical centroid of the backtraced particle envelope
    centroid = [float(np.mean(particles[:, 0])), float(np.mean(particles[:, 1]))]
    
    latency = int((time.time() - start_time) * 1000)
    print(f"[PHYSICS] 🟢 Advanced SDE envelope computed for {n_particles} particles in {latency}ms.")
    print(f"[PHYSICS] 📍 Backtraced Origin Centroid -> Lat: {centroid[0]:.4f}, Lon: {centroid[1]:.4f}")
    
    return {
        "particles_raw": particles,
        "centroid": centroid,
        "hours_back": hours_back,
        "particle_count": n_particles
    }