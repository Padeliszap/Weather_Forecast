import mysql.connector
import requests
from datetime import datetime, timedelta

# Connect to the database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="My$QL_S3rv3r_2025!", 
    database="weather",  
    port=3306  
)
cursor = conn.cursor()
print("Connection successful!")

#  Function to fetch data from the API
def get_weather_data(lat, lon, start_date, end_date):
    url = f"https://api.meteomatics.com/{start_date}T00:00:00Z--{end_date}T23:59:59Z:PT1H/t_2m:C/{lat},{lon}/json"
    auth = ('ded_zapadiotis_padelis', '91IzRgU5qR')
    response = requests.get(url, auth=auth)
    
    if response.status_code == 200:
        print(f" Data retrieved successfully for lat:{lat}, lon:{lon}")
        return response.json()
    else:
        print("Failed to retrieve data from API!")
        return None

#  Insert data into the database
def insert_weather_data(location_id, data):
    if not data or 'data' not in data or not data['data']:
        print(f" No weather data for location_id: {location_id}")
        return
    
    for entry in data['data'][0]['coordinates'][0]['dates']:
        forecast_date = entry['date']
        forecast_date = datetime.strptime(forecast_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
        the_temp = entry['value']
        
        cursor.execute("""
            INSERT INTO forecasts (location_id, forecast_date, temperature)
            VALUES (%s, %s, %s)
        """, (location_id, forecast_date, the_temp))
    
    conn.commit()
    print(f" Weather data inserted for location_id: {location_id}")

#  Cities for weather forecasting
locations = [
    {"name": "Athens", "lat": 37.9838, "lon": 23.7275},
    {"name": "Thessaloniki", "lat": 40.6401, "lon": 22.9444},
    {"name": "Patras", "lat": 38.2466, "lon": 21.7346}
]

#  Set forecast date range
start_date = datetime.now().strftime('%Y-%m-%d')
end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

#  Insert locations and fetch weather data
for loc in locations:
    cursor.execute("""
        INSERT INTO locations (name, latitude, longitude)
        VALUES (%s, %s, %s)
    """, (loc["name"], loc["lat"], loc["lon"]))
    conn.commit()  # Ensure the insert is completed
    location_id = cursor.lastrowid
    print(f"📍 Location inserted: {loc['name']} (ID: {location_id})")
    
    data = get_weather_data(loc["lat"], loc["lon"], start_date, end_date)
    if data:
        insert_weather_data(location_id, data)

# Close connection
conn.close()
print(" Data successfully inserted into the database!")

