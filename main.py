from flask import Flask, jsonify, request
import mysql.connector
import os

# Initialize Flask app
app = Flask(__name__)

# Function to connect to the database
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="My$QL_S3rv3r_2025!",
        database="weather",
        port=3306  
    )
    return conn

# Root endpoint (home)
@app.route('/', methods=['GET'])
def home():
    return '''Welcome to the Weather API!<br>
              <a href="/locations" target="_blank">List Locations</a><br>
              <a href="/latest_forecast" target="_blank">Latest Forecasts</a><br>
              <a href="/average_temp_last_3" target="_blank">Average Temperature (Last 3 Forecasts)</a><br>
              <a href="/top_locations?n=5&metric=temperature" target="_blank">Top Locations by Temperature</a>
           '''

# List all locations
@app.route('/locations', methods=['GET'])
def list_locations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM locations")
    locations = cursor.fetchall()
    conn.close()
    return jsonify(locations)

# Latest forecast for each location for each day
@app.route('/latest_forecast', methods=['GET'])
def latest_forecast():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT l.name AS location_name, 
               f.forecast_date, 
               f.temperature
        FROM forecasts f
        JOIN locations l ON f.location_id = l.id
        WHERE (f.location_id, f.forecast_date, f.id) IN (
            SELECT location_id, forecast_date, MAX(id)
            FROM forecasts
            GROUP BY location_id, forecast_date
        )
        ORDER BY l.name, f.forecast_date DESC;
    """)

    forecasts = cursor.fetchall()
    conn.close()
    return jsonify(forecasts)


# Average temperature of the last 3 forecasts for each location per day
@app.route('/average_temp_last_3', methods=['GET'])
def average_temp_last_3():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        WITH latest_forecasts AS (
            SELECT location_id, forecast_date, temperature,
                   ROW_NUMBER() OVER (PARTITION BY location_id, DATE(forecast_date) ORDER BY forecast_date DESC) AS row_num
            FROM forecasts
        )
        SELECT l.name AS location_name, 
               DATE(f.forecast_date) AS forecast_day,
               ROUND(AVG(f.temperature), 2) AS avg_temp
        FROM latest_forecasts f
        JOIN locations l ON f.location_id = l.id
        WHERE f.row_num <= 3
        GROUP BY l.name, DATE(f.forecast_date)
        ORDER BY forecast_day DESC
    """)
    
    averages = cursor.fetchall()
    conn.close()
    return jsonify(averages)

# Get the top n locations based on a given metric
@app.route('/top_locations', methods=['GET'])
def top_locations():
    n = request.args.get('n', default=5, type=int)
    metric = request.args.get('metric', default='temperature')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = f"""
        SELECT l.name AS location_name, AVG(f.{metric}) AS avg_{metric}
        FROM forecasts f
        JOIN locations l ON f.location_id = l.id
        GROUP BY l.name
        ORDER BY avg_{metric} DESC
        LIMIT %s
    """
    
    try:
        cursor.execute(query, (n,))
        top_locations = cursor.fetchall()
    except mysql.connector.Error as e:
        return jsonify({"error": f"MySQL Error: {e}"}), 500
    finally:
        conn.close()

    return jsonify(top_locations)

# Run the Flask app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
