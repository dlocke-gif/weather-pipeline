import argparse
from src.fetcher import fetch_active_alerts
from src.processor import process_alerts_data
from src.database import init_db, save_alerts_to_db, get_connection

def parse_args():
    parser = argparse.ArgumentParser(description = "NWS Severe Weather Ingestion Pipeline")
    parser.add_argument(
        "--area",
        type = str,
        default = None,
        help = "Two-letter state code to filter alerts (e.g., MS, TX). Defaults to nationwide."
    )
    return parser.parse_args()

def generate_terminal_report():
    " Queries SQLite and outputs a summary table. "
    conn = get_connection()
    cursor = conn.cursor()

    " First query outputs the total alerts stored. "
    cursor.execute("SELECT COUNT(*) FROM alerts;")
    total_alerts = cursor.fetchone()[0]

    " Second query breaks down events by severity. "
    cursor.execute("""
        SELECT severity, COUNT(*) 
        FROM alerts 
        GROUP BY severity 
        ORDER BY COUNT(*) DESC;
    """)
    severity_breakdown = cursor.fetchall()

    " Third query outputs the top warning events "
    cursor.execute("""
        SELECT event, COUNT(*) 
        FROM alerts 
        GROUP BY event 
        ORDER BY COUNT(*) DESC 
        LIMIT 5;
    """)
    top_events = cursor.fetchall()

    conn.close()

    print("\n" + "=" * 50)
    print("        NWS WEATHER ALERT INGESTION REPORT       ")
    print("=" * 50)
    print(f"Total Unique Alerts in DB: {total_alerts}")
    
    print("\n--- Active Severity Levels ---")
    for sev, count in severity_breakdown:
        print(f"  {sev:<12}: {count}")

    print("\n--- Top 5 Weather Events ---")
    for event, count in top_events:
        print(f"  {event:<30}: {count}")
    print("=" * 50 + "\n")

def main():
    args = parse_args()
    target_area = args.area.upper() if args.area else None

    print("1. Initializing SQLite Database schema...")
    init_db()

    print(f"2. Ingesting active alerts from NWS API (Target: {target_area or 'Nationwide'})...")
    raw_data = fetch_active_alerts(area=target_area)
    features = raw_data.get("features", [])
    print(f"   Retrieved {len(features)} active alert records.")

    if not features:
        print("No active alerts found for this query. Database remains unchanged.")
        return

    print("3. Transforming & cleaning data via Pandas...")
    df_alerts, df_areas = process_alerts_data(raw_data)
    print(f"   Sanitized {len(df_alerts)} alerts and mapped {len(df_areas)} areas.")

    print("4. Persisting records to SQLite database...")
    save_alerts_to_db(df_alerts, df_areas)
    print("5. Database write complete.")

    generate_terminal_report()

if __name__ == "__main__":
    main()