from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from api.routers import router as triage_router

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

app = FastAPI(
    title="AEGIS-OCEAN Backend API",
    description="Maritime Intelligence SDE & Spatial Hashing API",
    version="1.0.0"
)

# CRITICAL: Allow CORS so the React frontend on Laptop A can talk to Laptop B
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon. In prod, lock this to specific IPs.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the router
app.include_router(triage_router)

@app.get("/")
async def health_check():
    return {"status": "AEGIS-OCEAN Backend is online and tracking."}

if __name__ == "__main__":
    logging.info("Starting Uvicorn ASGI Server...")
    # Host 0.0.0.0 exposes the server to the local LAN.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)