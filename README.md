### 🌊 AEGIS-OCEAN: Maritime Triage Engine

This is the core backend engine for the AEGIS-OCEAN hackathon project. It processes Sentinel-1 SAR-detected oil slicks, simulates backward trajectories using stochastic differential equations (Euler-Maruyama), and utilizes O(1) Uber H3 spatial hashing to instantly filter and score candidate AIS vessel data. 

### ⚠️ Prerequisites

* **Python 3.10, 3.11, or 3.12** is strictly required.
* *Do not use Python 3.13 or newer.* Newer versions currently lack pre-compiled C-extension wheels for scipy and h3, which will cause installation failures and binary mismatches.

### ⚙️ Local Installation Setup

### 1. Clone the repository and navigate to the backend folder

```bash
git clone [https://github.com/pratheep537/Agesis_Ocean.git](https://github.com/pratheep537/Agesis_Ocean.git)
cd AGEIS_OCEAN/backend
```

Use code with caution.

### 2. Create a Virtual Environment

Create an isolated environment to prevent dependency conflicts. (If you are on Windows and have multiple Python versions, force it to use a stable version like 3.10 or 3.12). 

```bash

# Windows
py -3.12 -m venv .venv

```
Use code with caution.

### 3. Activate the Virtual Environment

You must activate this environment every time you open a new terminal. 

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```
Use code with caution.

### 4. Install Dependencies

Ensure your virtual environment is active (you should see (.venv) in your terminal prompt), then install the stack: 

```bash
pip install --no-cache-dir -r requirements.txt
```
Use code with caution.

*(Note: We use --no-cache-dir to prevent localized Pydantic/Rust core corruption).* 

### 🚀 Running the Engine

Start the FastAPI local development server: 

```bash
uvicorn main:app --reload
```
Use code with caution.

### 🧪 Testing the API

Once the server is running, open your browser and navigate to the interactive Swagger UI:
👉 http://127.0.0.1:8000/docs 

You can test the POST /api/v1/triage endpoint using the following synthetic payload. This simulates a 4-point oil slick polygon, ERA5T metocean currents, and 6 hours of drift time: 

```json

{
  "slick_boundary_coords": [
    [15.12, 70.08],
    [15.12, 70.12],
    [15.08, 70.12],
    [15.08, 70.08]
  ],
  "u_curr": 0.2,
  "v_curr": -0.1,
  "u_wind": 5.5,
  "v_wind": 2.0,
  "drift_hours": 6.0
}
```
Use code with caution.

The engine will return a 200 OK response with the Top 3 suspect vessels ranked by their kinematic triage score (speed viability, dark fleet gaps, and heading alignment).
