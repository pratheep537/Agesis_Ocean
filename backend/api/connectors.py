import httpx
import pandas as pd
import os
from datetime import datetime, timedelta
from api.config import settings

class TelemetryClient:
    """
    Handles all external and local telemetry acquisition.
    Bridges ESA Copernicus CDSE satellite feeds with sovereign Marine Cadastre AIS vaults.
    """
    def __init__(self):
        self.cdse_token = None
        self.token_expiry = datetime.min
        self.cdse_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
        self.cdse_catalog_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

    async def _get_cdse_token(self) -> str:
        """
        Authenticates with the European Space Agency (ESA) Copernicus Data Space Ecosystem
        and caches the OAuth2 token until expiration.
        """
        if datetime.utcnow() < self.token_expiry and self.cdse_token:
            return self.cdse_token

        payload = {
            "grant_type": "client_credentials",
            "client_id": settings.CDSE_CLIENT_ID,
            "client_secret": settings.CDSE_CLIENT_SECRET
        }
        
        async with httpx.AsyncClient() as client:
            print("[API] 🔐 Requesting new Copernicus Auth Token...")
            res = await client.post(self.cdse_token_url, data=payload)
            res.raise_for_status()
            data = res.json()
            self.cdse_token = data["access_token"]
            # Set expiry 30 seconds early as a safety buffer
            self.token_expiry = datetime.utcnow() + timedelta(seconds=data.get("expires_in", 300) - 30)
            return self.cdse_token

    async def fetch_sentinel_image(self, polygon_wkt: str, hours_back: int = 48):
        """
        Polls the ESA Copernicus OData catalog for the latest Sentinel-1 GRD 
        SAR imagery intersecting the given polygon region.
        """
        token = await self._get_cdse_token()
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)
        time_filter = (
            f"ContentDate/Start gt {start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')} "
            f"and ContentDate/Start lt {end_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')}"
        )
        
        odata_filter = (
            f"?$filter=Collection/Name eq 'SENTINEL-1' "
            f"and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'GRD') "
            f"and OData.CSC.Intersects(area=geography'SRID=4326;{polygon_wkt}') "
            f"and {time_filter}&$top=1"
        )
        
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient() as client:
            print("[API] 🛰️ Scanning ESA Grid for Sentinel-1 acquisitions...")
            res = await client.get(self.cdse_catalog_url + odata_filter, headers=headers)
            
            if res.status_code == 200:
                values = res.json().get("value", [])
                if values:
                    product_name = values[0].get('Name')
                    print(f"[API] 🟢 Image Found: {product_name}")
                    return values[0]
                else:
                    print("[API] ⚪ No new passes found in target envelope.")
                    return None
            else:
                print(f"[ERROR] 🔴 CDSE Query Failed with status code: {res.status_code}")
                return None

    async def fetch_ais_telemetry(self, min_lat: float, max_lat: float, min_lon: float, max_lon: float):
        """
        Queries the sovereign Marine Cadastre compliant Parquet vault for historical 
        vessel trajectories matching the spatial bounding box of the incident.
        """
        print("[API] 🚢 Accessing Sovereign AIS Parquet Vault...")
        file_path = "data/wakashio_ais.parquet"
        
        if os.path.exists(file_path):
            # Read parquet using high-performance C-engine
            df = pd.read_parquet(file_path)
            
            # Filter rows strictly within the requested geographic bounding box
            spatial_filtered = df[
                (df['lat'] >= min_lat) & (df['lat'] <= max_lat) &
                (df['lon'] >= min_lon) & (df['lon'] <= max_lon)
            ].copy()
            
            entries = spatial_filtered.to_dict(orient="records")
            print(f"[API] 🟢 Loaded {len(entries)} commercial ship tracks within target sector.")
            return entries
        else:
            print("[WARNING] 🟡 Parquet vault empty or missing. Please run python generate_data.py!")
            return []

# Instantiate the global singleton client
telemetry_client = TelemetryClient()