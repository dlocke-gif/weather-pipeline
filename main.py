from src.fetcher import fetch_active_alerts

def main():
    print("Connecting to the National Weather Service API...")
    data = fetch_active_alerts(area = "MS")
    # Leaving area empty fetches all active alerts across the US.
    features = data.get("features", [])

    print(f"Successfully retrieved {len(features)} active alerts for Mississippi.")

    if features:
        sample = features[0]["properties"]
        print("\n--- Alert ---")
        print(f"Event: {sample.get('event')}")
        print(f"Severity: {sample.get('severity')}")
        print(f"Headline: {sample.get('headline')}")
        print(f"Expires: {sample.get('expires')}")

if __name__ == "__main__":
    main()