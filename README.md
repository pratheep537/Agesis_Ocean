# Agesis Ocean

Aegis Ocean is a maritime intelligence backend for detecting, reconstructing, and triaging possible oil-spill incidents using satellite imagery, AIS telemetry, and geospatial physics.

It combines:
- FastAPI for the backend service layer
- PostgreSQL/PostGIS for secure vessel records
- ClickHouse for high-speed raw telemetry ingestion
- NumPy and physics-based SDE time-reversal modeling
- H3 spatial indexing and kinematic scoring to rank suspect vessels

## How it works

1. The system polls Copernicus Sentinel imagery for suspicious ocean anomalies.
2. When an anomaly is detected, it runs a stochastic differential equation (SDE) backtrace to estimate the likely spill origin.
3. The app loads nearby AIS ship records from the local parquet dataset.
4. It filters ships using spatial bounds and H3 hex cells.
5. It computes a weighted suspicion score based on speed, time gap, and alignment.
6. The top suspect is stored in PostgreSQL for auditing and review.

## Project structure

- `backend/` - Python backend service
- `backend/main.py` - FastAPI application entry point and autonomous loop
- `backend/api/` - external data connectors and settings
- `backend/database/` - database initialization and CRUD
- `backend/physics/` - SDE and vessel triage logic
- `backend/generate_data.py` - synthetic AIS data generator
- `docker-compose.yml` - local Postgres and ClickHouse services

## Prerequisites

Before running the project, install:
- Docker Desktop
- Python 3.10+
- Git

## Setup

### 1. Start the database services

From the project root:

```bash
docker compose up -d
```

This starts:
- PostgreSQL on `localhost:5434`
- ClickHouse on `localhost:8123`

### 2. Create a Python environment

```bash
cd backend
python -m venv venv
```

On Windows PowerShell:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify the `.env` file

The project expects the following local secrets file in the backend folder:

```env
CDSE_CLIENT_ID="your-copernicus-client-id"
CDSE_CLIENT_SECRET="your-copernicus-client-secret"
CMEMS_KEY="your-cmems-key"
DATABASE_URL="postgresql://postgres:sih2026@localhost:5434/aegis_ocean"
CLICKHOUSE_URL="clickhouse://default:sih2026@localhost:8123/default"
H3_RESOLUTION=7
WINDAGE_COEFF=0.03
PARTICLE_COUNT=2000
```

### 5. Generate AIS data (if needed)

```bash
cd backend
python generate_data.py
```

### 6. Run the app

```bash
cd backend
uvicorn main:app --reload
```

Then open:

- `http://127.0.0.1:8000`

## Notes

- The project is built for local demo/testing and demonstration workflows.
- The app is designed to keep running in a background autonomous loop, continuously scanning and triaging.
- The included `.env` file is intentionally committed here because this repository is private and the credentials are local-only.

## Typical workflow

- Start Docker services
- Generate parquet AIS data
- Start the FastAPI app
- Watch the backend logs for detection and triage output
- Check PostgreSQL for flagged vessel entries

## License

This project is intended for internal/demo use and is configured for this repository's local development workflow.
