# NWS Severe Weather Ingestion Pipeline

An automated ETL (Extract, Transform, Load) data pipeline written in Python that ingests, cleans, and stores real-time severe weather alerts from the National Weather Service (NWS / NOAA) API into a relational SQLite database.

# Architecture & System Design

```text
[ NWS REST API ]
         │ (GeoJSON)
         ▼
[ Ingestion Layer: fetcher.py ]  --> Handles HTTP sessions, headers & status codes
         │ (Raw JSON Dict)
         ▼
[ Processing Layer: processor.py ] --> Pandas data cleaning, timestamp normalization & duration metrics
         │ (Normalized DataFrames)
         ▼
[ Database Layer: database.py ]  --> SQLite schema with 1-to-many foreign keys & idempotent upserts
         │
         ▼
[ CLI Analytics: main.py ]       --> SQL reporting & terminal dashboard
