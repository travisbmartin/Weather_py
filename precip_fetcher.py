import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

precip_urls = {
    'Evansville': 'https://forecast.weather.gov/data/obhistory/KEVV.html',
    'Vincennes': 'https://forecast.weather.gov/data/obhistory/KLWV.html',
    'Mt. Carmel': 'https://forecast.weather.gov/data/obhistory/KAJG.html'
}

def fetch_precip_data():
    precip_data = []
    print(f'Fetching precipitation data from {precip_urls}')

    for location, url in precip_urls.items():
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f'Failed to fetch data for {location}: {e}')
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table')
        print(f'Found {len(tables)} tables for {location}')

        for table in tables:
            headers = [header.text.strip() for header in table.find_all('th')]
            print(f'Table headers for {location}: {headers}')
            required_headers = ['Date', 'Time (cst)', 'Weather', 'Precipitation (in)', '1 hr', '3 hr', '6 hr']
            if all(header in headers for header in required_headers):
                rows = table.find_all('tr')[1:]  # Skip the header row

                current_time = datetime.now()
                six_hours_ago = current_time - timedelta(hours=6)
                print(f'Current time: {current_time}')
                print(f'Six hours ago: {six_hours_ago}')

                for row in rows:
                    cols = row.find_all('td')
                    print(f"Row columns: {[col.text.strip() for col in cols]}")
                    if len(cols) > 0:
                        date_str = cols[0].text.strip()
                        time_str = cols[1].text.strip()
                        datetime_str = f"{date_str} {time_str}"
                        print(f"Processing datetime: {datetime_str}")
                        try:
                            time_obj = datetime.strptime(datetime_str, '%d %H:%M')
                            time_obj = time_obj.replace(year=current_time.year, month=current_time.month)
                            print(f"Parsed datetime: {time_obj}")
                        except ValueError as e:
                            print(f"Error parsing datetime: {e}")
                            continue

                        if time_obj >= six_hours_ago:
                            weather = cols[4].text.strip() if len(cols) > 4 else ''
                            precip_1hr = float(cols[-3].text.strip()) if len(cols) > 3 and cols[-3].text.strip() else 0
                            precip_3hr = float(cols[-2].text.strip()) if len(cols) > 2 and cols[-2].text.strip() else 0
                            precip_6hr = float(cols[-1].text.strip()) if len(cols) > 1 and cols[-1].text.strip() else 0

                            if precip_1hr > 0.05 or precip_3hr > 0.05 or precip_6hr > 0.05:
                                precip_data.append({
                                    'location': location,
                                    'time': time_obj.strftime('%Y-%m-%d %H:%M'),
                                    'weather': weather,
                                    'precip_1hr': precip_1hr,
                                    'precip_3hr': precip_3hr,
                                    'precip_6hr': precip_6hr
                                })

                print(f'Fetched data for {location}: {precip_data}')
                break
        else:
            print(f'Could not find the correct table for {location}')

    return precip_data

def check_weather_condition(weather):
    if weather == "Light Rain":
        return 1
    elif weather == "Rain":
        return 2
    elif weather == "Heavy Rain":
        return 3
    elif weather == "Thunderstorm":
        return 3
    else:
        return 0

def check_precipitation_condition(precip_1hr):
    if precip_1hr >= 0.5:
        return 3
    elif precip_1hr >= 0.1 and precip_1hr < 0.5:
        return 2
    elif precip_1hr > 0 and precip_1hr < 0.1:
        return 1
    else:
        return 0
