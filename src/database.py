import sqlite3
import pandas as pd
from typing import Optional

default_db_path = "data/weather_alerts.db"

def get_connection(db_path: str = default_db_path) -> sqlite3.Connection:
    " Creates and returns a connection to the SQLite database. "
    conn = sqlite3.connect(db_path)
    " Enables foreign key constraint enforcement in SQLite. "
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path: str = default_db_path) -> None:
    """
    Initializes relational schema with two tables:
    1. alerts: Stores event attributes (Primary Key: alert_id)
    2. alert_areas: Maps alert_id to regional areas (Foreign Key)
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            alert_id TEXT PRIMARY KEY,
            event TEXT,
            severity TEXT,
            urgency TEXT,
            certainty TEXT,
            headline TEXT,
            effective TEXT,
            expires TEXT,
            duration_hours REAL,
            ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert_areas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id TEXT,
            area_code TEXT,
            FOREIGN KEY (alert_id) REFERENCES alerts(alert_id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()

def save_alerts_to_db(df_alerts: pd.DataFrame, df_areas: pd.DataFrame, db_path: str = default_db_path) -> None:
    """
    Inserts processed DataFrames into the SQLite database.
    Uses INSERT OR REPLACE to ensure pipeline idempotency.
    """
    if df_alerts.empty:
        return

    conn = get_connection(db_path)
    cursor = conn.cursor()

    " Inserts or updates alert records "
    alerts_records = df_alerts.to_dict(orient="records")
    cursor.executemany("""
        INSERT OR REPLACE INTO alerts (
            alert_id, event, severity, urgency, certainty, 
            headline, effective, expires, duration_hours
        ) VALUES (
            :alert_id, :event, :severity, :urgency, :certainty, 
            :headline, :effective, :expires, :duration_hours
        );
    """, alerts_records)

    " Inserts area mappings to avoid duplicate area associations for an alert "
    if not df_areas.empty:
        areas_records = df_areas.to_dict(orient="records")
        cursor.executemany("""
            INSERT INTO alert_areas (alert_id, area_code)
            SELECT :alert_id, :area_code
            WHERE NOT EXISTS (
                SELECT 1 FROM alert_areas 
                WHERE alert_id = :alert_id AND area_code = :area_code
            );
        """, areas_records)

    conn.commit()
    conn.close()