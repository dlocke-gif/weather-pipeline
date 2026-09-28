import pandas as pd
from typing import Dict, Any, Tuple

def process_alerts_data(raw_data: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Parses raw NWS GeoJSON into two DataFrames:
    1. df_alerts: Alert attributes (id, event, severity, timing, duration)
    2. df_areas: 1-to-many relationship mapping alert_id to UGC area codes
    """
    features = raw_data.get("features", [])
    if not features:
        return pd.DataFrame(), pd.DataFrame()

    alerts_list = []
    areas_list = []

    for item in features:
        props = item.get("properties", {})
        alert_id = props.get("id")

        if not alert_id:
            continue

        " Extracts alert attributes "
        alerts_list.append({
            "alert_id": alert_id,
            "event": props.get("event"),
            "severity": props.get("severity"),
            "urgency": props.get("urgency"),
            "certainty": props.get("certainty"),
            "headline": props.get("headline"),
            "effective": props.get("effective"),
            "expires": props.get("expires")
        })

        " Extracts affected UGC area codes "
        geocode = props.get("geocode", {})
        ugc_codes = geocode.get("UGC", [])
        for code in ugc_codes:
            areas_list.append({
                "alert_id": alert_id,
                "area_code": code
            })

    " Builds Panda DataFrames "
    df_alerts = pd.DataFrame(alerts_list)
    df_areas = pd.DataFrame(areas_list)

    " Cleans and parses timestamps with Pandas "
    df_alerts["effective"] = pd.to_datetime(df_alerts["effective"], errors = "coerce", utc = True)
    df_alerts["expires"] = pd.to_datetime(df_alerts["expires"], errors = "coerce", utc = True)

    " Calculates duration in hours "
    duration = (df_alerts["expires"] - df_alerts["effective"]).dt.total_seconds() / 3600.0
    df_alerts["duration_hours"] = duration.round(2)

    " Converts timestamps to ISO strings to store in SQLite "
    df_alerts["effective"] = df_alerts["effective"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df_alerts["expires"] = df_alerts["expires"].dt.strftime("%Y-%m-%d %H:%M:%S")

    " Drops duplicate alerts if any exist "
    df_alerts = df_alerts.drop_duplicates(subset = ["alert_id"])
    df_areas = df_areas.drop_duplicates()

    return df_alerts, df_areas