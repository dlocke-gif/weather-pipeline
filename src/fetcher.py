import requests
from typing import Dict, Any, Optional

NWS_Active_Alerts_URL = "https://api.weather.gov/alerts/active"

Headers = {
    "User-Agent": "(msstate-weather-pipeline, darenlocke20@gmail.com)",
    "Accept": "application/geo+json"
}

def fetch_active_alerts(area: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetches active weather alerts from the NWS API.
    Optionally filter by state code (e.g., area = "MS").
    """
    params = {}
    if area:
        params["area"] = area

    try:
        response = requests.get(
            NWS_Active_Alerts_URL,
            headers = Headers,
            params = params,
            timeout = 10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching NWS alert data: {e}")
        raise