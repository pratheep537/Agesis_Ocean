# AEGIS-OCEAN: Maritime Intelligence System

**AEGIS-OCEAN** is a high-performance, defensible maritime intelligence platform designed for autonomous oil spill detection and dark vessel tracking. It synthesizes satellite computer vision, reverse-time physics simulations, and military-grade kinematic tracking into a single tactical dashboard.

## 🚀 Core Architecture

* **The Scout/Sniper AI Cascade:** A dual-stage neural network (Basic U-Net for triage, Swin-UNet for precise geometry extraction) that filters satellite SAR imagery to isolate anomalous oil slicks.
* **Euler-Maruyama Drift Engine:** A vectorized Stochastic Differential Equation (SDE) physics engine that ingests live Open-Meteo wind and ocean current data to calculate the reverse trajectory of oil spills.
* **O(1) Spatial Hashing:** Utilizes the Uber H3 geospatial indexing system (Resolution 7) to quantize probability envelopes into an instantly queryable hexadecimal grid.
* **IMM Kalman Filter:** Tracks "dark vessels" (ships with disabled AIS transponders) using an Interacting Multiple Model (Constant Velocity + Random Walk) to mathematically correlate evasive maneuvers with the SDE physics output.

## 🛠️ Tech Stack

* **Frontend:** React, Vite, TailwindCSS, Mapbox GL JS, H3-js, Axios
* **Backend:** Python, FastAPI, PyTorch, NumPy, FilterPy, Uvicorn

## ⚙️ Installation & Execution

### 1. Backend (Physics & AI Engine)
``` bash
cd backend
python -m venv venv
# Activate virtual environment (Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python main.py
```
### 2. Frontend (Tactical Dashboard)
```bash
cd frontend
npm install
npm run dev
```

The Mapbox UI will boot on http://localhost:5173.

Developed for SIH Hackathon 2026.

### Step 3: Execute the Git Reset
Now that those files are created in the root folder, run your Git sequence to push them up and lock everything down:

```powershell
git add .gitignore README.md
git commit -m "docs: added master gitignore and tactical readme"
git push origin v1
```