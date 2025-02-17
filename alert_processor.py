import requests
import json
import re

counties = {
    'Gibson': 'IN',
    'Knox': 'IN',
    'Vanderburgh': 'IN',
    'Posey': 'IN',
    'Pike': 'IN',
    'Warrick': 'IN',
    'Wabash': 'IL',
    'Lawrence': 'IL',
    'Edwards': 'IL',
    'White': 'IL',
    'Henderson': 'KY',
    'Union': 'KY',
    'Daviess': 'KY'
}

alert_levels = {
    'Advisory': 1000,
    'Watch': 2000,
    'Warning': 3000,
    'Emergency': 4000,
    'Unknown': 0  # Default value for undefined severity
}

weather_alert_types = {
    'Blizzard': 10,
    'Dense Fog': 20,
    'Excessive Heat': 30,
    'Extreme Cold': 40,
    'Flash Flood': 50,
    'Flood': 60,
    'Freeze': 70,
    'Freezing Fog': 80,
    'Freezing Rain': 90,
    'Frost': 100,
    'Hard Freeze': 110,
    'Heat': 120,
    'Ice Storm': 130,
    'Severe Thunderstorm': 140,
    'Storm': 150,
    'Tornado': 160,
    'Wind': 170,
    'Wind Chill': 180,
    'Winter Storm': 190,
    'Hydrologic Outlook': 0
}

def get_alerts(state):
    url = f"https://api.weather.gov/alerts/active?area={state}"
    response = requests.get(url)
    #print(f"Fetching alerts for state: {state}, URL: {url}")  # Debug print
    if response.status_code == 200:
        alerts = response.json().get('features', [])
        #print(f"Received {len(alerts)} alerts for state: {state}")  # Debug print
        return alerts
    print(f"Failed to fetch alerts for state: {state}, status code: {response.status_code}")  # Debug print
    return []

def determine_alert_value(alert):
    alert_type = alert['properties']['event']
    alert_parts = alert_type.split()
    if len(alert_parts) < 2:
        return 0
    weather_type = ' '.join(alert_parts[:-1])
    severity = alert_parts[-1]
    #print(f"Weather Type: {weather_type}, Severity: {severity}")  # Debug print
    type_value = weather_alert_types.get(weather_type, 0)
    level_value = alert_levels.get(severity, 0)
    #print(f"Alert Type: {alert_type}, Type Value: {type_value}, Severity: {severity}, Level Value: {level_value}")
    return type_value + level_value

def get_highest_alert(county, state):
    alerts = get_alerts(state)
    highest_value = 0
    for alert in alerts:
        if county in alert['properties']['areaDesc']:
            value = determine_alert_value(alert)
            if value > highest_value:
                highest_value = value
    return highest_value

if __name__ == "__main__":
    for county, state in counties.items():
        highest_alert_value = get_highest_alert(county, state)
        print(f"Highest alert value for {county}, {state}: {highest_alert_value}")
