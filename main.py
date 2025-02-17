import schedule
import time
from pylogix import PLC
from weather_fetcher import fetch_weather_data
from precip_fetcher import fetch_precip_data, check_weather_condition, check_precipitation_condition
from alert_processor import get_alerts, determine_alert_value, counties

plc_ip = '10.120.76.100'
plc_tag = 'Storm_Code'

def process_weather_and_alerts():
    print()
    print("Starting weather and alert processing")
    while True:
        try:
            # Fetch weather data once
            weather_data = fetch_weather_data("Gibson County")
            
            for i, data in enumerate(weather_data):
                location = data["location"]
                temp_f = data["temp_f"]
                wind = data["wind"]
                humidity = data["humidity"]
                pressure_inhg = data["pressure_inhg"]
                dew_point_f = data["dew_point_f"]
                visibility_miles = data["visibility_miles"]
                
                print(f"Weather Data for {location}: Temp={temp_f}, WindSpeed={wind}, Humidity={humidity}, Pressure={pressure_inhg}, DewPoint={dew_point_f}, Visibility={visibility_miles}")
                #print(f"Index type: {type(i)}")  # Debug print to check index type
                
                with PLC(plc_ip) as comm:
                    # Write weather data to PLC arrays
                    weather_temp = comm.Write(f"W_Temp[{i}]", temp_f if isinstance(temp_f, float) else 0.0)
                    weather_windspeed = comm.Write(f"W_WindSpeed[{i}]", wind if isinstance(wind, float) else 0.0)
                    weather_humidity = comm.Write(f"W_Humidity[{i}]", humidity if isinstance(humidity, float) else 0.0)
                    weather_pressure = comm.Write(f"W_Pressure[{i}]", pressure_inhg if isinstance(pressure_inhg, float) else 0.0)
                    weather_dewpoint = comm.Write(f"W_DewPoint[{i}]", dew_point_f if isinstance(dew_point_f, float) else 0.0)
                    weather_visibility = comm.Write(f"W_Visibility[{i}]", visibility_miles if isinstance(visibility_miles, float) else 0.0)
            print()
            
            for i, (county, state) in enumerate(counties.items()):
                #print(f"Processing county: {county}, state: {state}, index: {i}")  # Debug print
                alerts = get_alerts(state)
                #print(f"Alerts for {county}: {alerts}")  # Debug print
    
                highest_alert_value = 0
                for alert in alerts:
                    if county in alert['properties']['areaDesc']:
                        alert_value = determine_alert_value(alert)
                        #print(f"Alert: {alert}, Alert Value: {alert_value}")  # Debug print
                        if alert_value > highest_alert_value:
                            highest_alert_value = alert_value
                #print(f"Determined highest alert value: {highest_alert_value}")  # Debug print
    
                with PLC(plc_ip) as comm:
                    comm.Write(f'Storm_Code[{i}]', highest_alert_value)
                    print(f'Alert value for {county} County: {highest_alert_value}')
                    
            print("Completed weather and alert processing")
            print()
            break  # Exit the loop if successful
        except Exception as e:
            print(f" Fetch_Weather Error occurred: {e}. Retrying in 1 minute...")
            time.sleep(60)  # Wait for 1 minute before retrying

def process_precipitation():
    print("Starting precipitation processing")
    while True:
        try:
            precip_data = fetch_precip_data()
            
            with PLC(plc_ip) as comm:
                for i, precip in enumerate(precip_data):
                    location = precip['location']
                    weather_condition_value = check_weather_condition(precip['weather'])
                    precipitation_condition_value = check_precipitation_condition(precip['precip_1hr'])
                    
                    print(f"Index type: {type(i)}")  # Debug print to check index type
                    print(f"Location: {location}, Weather Condition Value: {weather_condition_value}, Precipitation Condition Value: {precipitation_condition_value}")
                    
                    comm.Write(f"W_WeatherCondition[{i}]", weather_condition_value)
                    comm.Write(f"W_PrecipCondition[{i}]", precipitation_condition_value)
                    print(f"Weather condition value for {location}: {weather_condition_value}")
                    print(f"Precipitation condition value for {location}: {precipitation_condition_value}")
                    
            print("Completed precipitation processing")
            break  # Exit the loop if successful
        except Exception as e:
            print(f"Error occurred: {e}. Retrying in 1 minute...")
            time.sleep(60)  # Wait for 1 minute before retrying

# Schedule the jobs
def job_scheduler():
    print("Scheduling jobs")
    schedule.every(1).minutes.do(process_weather_and_alerts)
    schedule.every().hour.at(":00").do(process_precipitation)
    print("Jobs scheduled")

print("Starting script")

# Add back the job scheduler
job_scheduler()

# Add a small delay before starting the main loop
time.sleep(5)

# Main loop to run scheduled jobs
while True:
    schedule.run_pending()
    time.sleep(1)

print("Script ended")
