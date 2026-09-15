from database import connection

async def log_guilty_vessel(guilty_ship: dict):
    """
    Securely writes the flagged suspect vessel into the PostgreSQL PostGIS Vault.
    """
    pool_to_use = connection.pg_pool

    if not pool_to_use:
        print("[ERROR] 🔴 Cannot log vessel: PostgreSQL pool is uninitialized.")
        return

    try:
        async with pool_to_use.acquire() as conn:
            await conn.execute("""
                INSERT INTO flagged_vessels (mmsi, vessel_name, guilt_score, speed_knots, incident_lat, incident_lon)
                VALUES ($1, $2, $3, $4, $5, $6);
            """,
                guilty_ship.get("mmsi"),
                guilty_ship.get("vessel_name"),
                guilty_ship.get("triage_score"),
                guilty_ship.get("sog"),
                guilty_ship.get("lat"),
                guilty_ship.get("lon")
            )
        print(f"[DATABASE] 🟢 Successfully secured MMSI {guilty_ship.get('mmsi')} in PostgreSQL Vault.")
    except Exception as e:
        print(f"[ERROR] 🔴 Failed to log guilty vessel to PostgreSQL: {e}")

def blast_telemetry_to_clickhouse(ais_entries: list):
    """
    Blasts raw AIS telemetry batches into ClickHouse Data Lake at high velocity.
    """
    if not connection.ch_client or not ais_entries:
        return
    
    try:
        data_rows = [
            (
                str(e.get('mmsi', '0')),
                str(e.get('BaseDateTime', '2026-09-15 12:00:00')),
                float(e.get('lat', 0.0)),
                float(e.get('lon', 0.0)),
                float(e.get('sog', 0.0)),
                float(e.get('cog', 0.0))
            )
            for e in ais_entries
        ]
        connection.ch_client.insert('raw_ais_telemetry', data_rows, column_names=['mmsi', 'timestamp', 'lat', 'lon', 'sog', 'cog'])
    except Exception as e:
        print(f"[ERROR] 🔴 ClickHouse ingestion error: {e}")