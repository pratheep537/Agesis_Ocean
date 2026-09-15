import asyncpg
import clickhouse_connect
from urllib.parse import urlparse
from api.config import settings

# Global connection references accessible across the backend architecture
pg_pool = None
ch_client = None

async def init_databases():
    """
    Bootstraps both the PostgreSQL Vault (with PostGIS extension) and 
    the ClickHouse Data Lake using robust URL parsing and credential mapping.
    """
    global pg_pool, ch_client
    
    # ---------------------------------------------------------
    # 1. BOOTSTRAP POSTGRESQL (THE SECURE VAULT)
    # ---------------------------------------------------------
    try:
        pg_pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL, 
            min_size=2, 
            max_size=10
        )
        
        async with pg_pool.acquire() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS flagged_vessels (
                    id SERIAL PRIMARY KEY,
                    mmsi VARCHAR(20) NOT NULL,
                    vessel_name VARCHAR(100),
                    guilt_score NUMERIC(5, 2),
                    speed_knots NUMERIC(5, 2),
                    incident_lat NUMERIC(9, 6),
                    incident_lon NUMERIC(9, 6),
                    flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        print("[DATABASE] 🟢 PostgreSQL Vault Connected & Configured.")
    except Exception as e:
        print(f"[ERROR] 🔴 PostgreSQL connection failed: {e}")

    # ---------------------------------------------------------
    # 2. BOOTSTRAP CLICKHOUSE (THE HIGH-SPEED DATA LAKE)
    # ---------------------------------------------------------
    try:
        # Use urlparse to correctly extract host, port, username, and password
        parsed_url = urlparse(settings.CLICKHOUSE_URL)
        
        ch_client = clickhouse_connect.get_client(
            host=parsed_url.hostname or "localhost",
            port=parsed_url.port or 8123,
            username=parsed_url.username or "default",
            password=parsed_url.password or ""
        )
        
        ch_client.command("""
            CREATE TABLE IF NOT EXISTS raw_ais_telemetry (
                mmsi String,
                timestamp DateTime,
                lat Float32,
                lon Float32,
                sog Float32,
                cog Float32
            ) ENGINE = MergeTree()
            ORDER BY (mmsi, timestamp);
        """)
        print("[DATABASE] 🟢 ClickHouse Data Lake Connected & Configured.")
    except Exception as e:
        print(f"[ERROR] 🔴 ClickHouse connection failed: {e}")

async def close_databases():
    """Safely tears down database connection pools during shutdown."""
    global pg_pool, ch_client
    if pg_pool:
        await pg_pool.close()
        print("[DATABASE] 🛑 PostgreSQL Vault Closed.")
    if ch_client:
        ch_client.close()
        print("[DATABASE] 🛑 ClickHouse Data Lake Closed.")