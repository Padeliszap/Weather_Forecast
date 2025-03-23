-- Δημιουργία βάσης δεδομένων
CREATE DATABASE weather;
USE weather;

-- Δημιουργία πίνακα locations
CREATE TABLE locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Δημιουργία πίνακα forecasts
CREATE TABLE forecasts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    forecast_date DATE NOT NULL,
    temperature DECIMAL(5,2),
    precipitation DECIMAL(6,2),
    wind_speed DECIMAL(5,2),
    FOREIGN KEY (location_id) REFERENCES locations(id),
    INDEX idx_location_date (location_id, forecast_date)
);


SELECT * FROM locations;
SELECT * FROM forecasts;

DESCRIBE locations;
DESCRIBE forecasts;