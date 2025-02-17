import requests
from bs4 import BeautifulSoup

# URL for NWS page
locations_urls = {
    'Mt. Carmel': 'https://forecast.weather.gov/MapClick.php?lat=38.3552&lon=-87.5676',
    'Evansville': 'https://forecast.weather.gov/MapClick.php?lat=37.9716&lon=-87.5711',
    'Vincennes': 'https://forecast.weather.gov/MapClick.php?lat=38.682025&lon=-87.5125'
}

def get_weather_urls(county):
    paducah_counties = [
        'Gibson County', 'Knox County', 'Vanderburgh County',
        'Posey County', 'Pike County', 'Warrick County',
        'Wabash County', 'Lawrence County', 'Edwards County', 
        'White County', 'Henderson County', 'Union County', 'Daviess County'
    ]

    if county in paducah_counties:
        return locations_urls
    else:
        return locations_urls  # Same URL used for simplicity

def fetch_weather_data(county):
    urls = get_weather_urls(county)
    weather_data = []

    for location, url in urls.items():
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            try:
                conditions = soup.find('p', class_='myforecast-current').text.strip()
            except AttributeError:
                conditions = 'N/A'
            try:
                temp_f = soup.find('p', class_='myforecast-current-lrg').text.strip()
                temp_f = float(temp_f.replace('°F', '').strip())
            except (AttributeError, ValueError):
                temp_f = 'N/A'
            details = soup.find('div', id='current_conditions_detail')
            rows = details.find_all('tr')
            try:
                humidity = [row.find_all('td')[1].text.strip() for row in rows if 'Humidity' in row.find('td').text][0]
                humidity = float(humidity.replace('%', '').strip())
            except (AttributeError, ValueError, IndexError):
                humidity = 'N/A'
            try:
                wind = [row.find_all('td')[1].text.strip() for row in rows if 'Wind Speed' in row.find('td').text][0]
                wind_value = wind.split()[1]
                wind = float(wind_value)
            except (AttributeError, ValueError, IndexError):
                wind = 'N/A'
            try:
                pressure_inhg = [row.find_all('td')[1].text.strip() for row in rows if 'Barometer' in row.find('td').text][0]
                pressure_inhg = float(pressure_inhg.split()[0].replace('in', '').strip())
            except (AttributeError, ValueError, IndexError):
                pressure_inhg = 'N/A'
            try:
                dew_point_f = [row.find_all('td')[1].text.strip() for row in rows if 'Dewpoint' in row.find('td').text][0]
                dew_point_value = dew_point_f.split(' ')[0]
                dew_point_f = float(dew_point_value.replace('°F', '').strip())
            except (AttributeError, ValueError, IndexError):
                dew_point_f = 'N/A'
            try:
                visibility_miles = [row.find_all('td')[1].text.strip() for row in rows if 'Visibility' in row.find('td').text][0]
                visibility_miles = float(visibility_miles.replace('mi', '').strip())
            except (AttributeError, ValueError, IndexError):
                visibility_miles = 'N/A'
                
            weather_data.append({
                "location": location,
                "conditions": conditions,
                "temp_f": temp_f,
                "humidity": humidity,
                "wind": wind,
                "pressure_inhg": pressure_inhg,
                "dew_point_f": dew_point_f,
                "visibility_miles": visibility_miles
            })

    for data in weather_data:
        print(f"Location: {data['location']}")
        print(f"Conditions: {data['conditions']}")
        print(f"Temperature (F): {data['temp_f']}")
        print(f"Humidity (%): {data['humidity']}")
        print(f"Wind Speed (mph): {data['wind']}")
        print(f"Pressure (inHg): {data['pressure_inhg']}")
        print(f"Dew Point (F): {data['dew_point_f']}")
        print(f"Visibility (miles): {data['visibility_miles']}")
        print("\n")
    
    return weather_data
