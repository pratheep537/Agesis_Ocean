import numpy as np
from filterpy.kalman import KalmanFilter, IMMEstimator
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class DarkVesselIMMTracker:
    def __init__(self, dt=1.0):
        """
        Initializes the Interacting Multiple Model (IMM) Kalman Filter.
        dt: Time step interpolation size (hours).
        """
        # Model 1: Constant Velocity (CV) - Ship follows the shipping lane
        self.kf_cv = KalmanFilter(dim_x=4, dim_z=2)
        self.kf_cv.F = np.array([[1, dt, 0,  0],
                                 [0,  1, 0,  0],
                                 [0,  0, 1, dt],
                                 [0,  0, 0,  1]])
        self.kf_cv.H = np.array([[1, 0, 0, 0],
                                 [0, 0, 1, 0]])
        self.kf_cv.P *= 10
        self.kf_cv.R *= 5
        self.kf_cv.Q = np.eye(4) * 0.001  # Low process noise (stable heading)

        # Model 2: Evasive Maneuver (RW) - Ship performs abrupt turns to dump oil
        self.kf_rw = KalmanFilter(dim_x=4, dim_z=2)
        self.kf_rw.F = np.array([[1, dt, 0,  0],
                                 [0,  1, 0,  0],
                                 [0,  0, 1, dt],
                                 [0,  0, 0,  1]])
        self.kf_rw.H = np.array([[1, 0, 0, 0],
                                 [0, 0, 1, 0]])
        self.kf_rw.P *= 10
        self.kf_rw.R *= 5
        self.kf_rw.Q = np.eye(4) * 0.1  # High process noise (erratic heading)

        # IMM Markov Transition Matrix (95% chance it stays in CV, 5% chance it goes evasive)
        filters = [self.kf_cv, self.kf_rw]
        mu = [0.95, 0.05]
        trans = np.array([[0.95, 0.05],
                          [0.10, 0.90]])

        self.imm = IMMEstimator(filters, mu, trans)
        
    def predict_dark_trajectory(self, start_x, start_y, start_vx, start_vy, missed_steps=12):
        """
        Calculates the kinematic projection of a ship when its AIS transponder is turned off.
        Returns a list of predicted (X, Y) coordinates.
        """
        state_vector = np.array([[start_x], [start_vx], [start_y], [start_vy]])
        
        # CRITICAL FIX: Inject state into the master IMM AND all internal sub-filters
        self.imm.x = state_vector.copy()
        for f in self.imm.filters:
            f.x = state_vector.copy()
        
        predicted_path = []
        logging.info(f"Initiating IMM Dead-Reckoning for {missed_steps} skipped AIS steps...")
        
        for _ in range(missed_steps):
            self.imm.predict()
            predicted_path.append((float(self.imm.x[0, 0]), float(self.imm.x[2, 0])))
            
        return predicted_path

# --- Test Execution Block ---
if __name__ == "__main__":
    logging.info("Initializing IMM Kalman Filter...")
    tracker = DarkVesselIMMTracker(dt=1.0)
    
    # Simulate a ship going dark at Longitude 65.0, Latitude 15.0 
    # traveling at roughly 0.2 degrees per hour.
    simulated_path = tracker.predict_dark_trajectory(
        start_x=65.0, start_y=15.0, 
        start_vx=0.2, start_vy=-0.05, 
        missed_steps=6 # 6 hours of missing AIS data
    )
    
    for i, (lon, lat) in enumerate(simulated_path):
        logging.info(f"Hour {i+1} Ghost Prediction -> Lon: {lon:.4f}, Lat: {lat:.4f}")
        
    logging.info("IMM Matrix calculations stable. Dark AIS interpolation ready.")