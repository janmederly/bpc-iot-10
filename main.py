"""
Projekt10 IoT Main Application

This application monitors temperature, voltage, and current,
and controls a fan based on temperature thresholds.
It provides a web interface for monitoring and configuration.
"""
import time
from sensors import SensorManager
from wifi_manager import WiFiManager
from webserver import WebServer
from fan_control import FanController
from mqtt_manager import MQTTManager
from consumption_calc import ConsumptionManager
import config

# Configuration
USE_BME280 = False  # Set to True if BME280 sensor is connected
ENABLE_MQTT = True  # Enable MQTT functionality

# Initialize components
sensor_manager = SensorManager(use_bme280=USE_BME280)
wifi_manager = WiFiManager()
fan_controller = FanController()
web_server = WebServer(port=80)
consumptionManager = ConsumptionManager()
mqtt_manager = MQTTManager(fan_controller, consumptionManager) if ENABLE_MQTT else None

# Connect to WiFi
wifi_connected = wifi_manager.connect_to_wifi()

# Connect to MQTT broker if WiFi is connected and MQTT is enabled
mqtt_connected = False
if wifi_connected and ENABLE_MQTT:
    print("Connecting to MQTT broker...")
    mqtt_connected = mqtt_manager.connect()
    
# Initialize counters for periodic MQTT updates
mqtt_update_counter = 0
mqtt_update_interval = 5  # Send MQTT updates every 5 seconds

time.sleep(2)  # Allow time for consumption manager to initialize

print("Starting main loop...")

# Main loop
try:
    while True:
        # Read sensor data
        temp = sensor_manager.read_temperature()
        voltage, current, power = sensor_manager.read_electrical_values()
        humidity = sensor_manager.read_humidity() if hasattr(sensor_manager, 'read_humidity') else 50  # Default if not available
        
        # Update consumption calculation
        consumption = consumptionManager.update_consumption(current, voltage)
        
        # Adjust fan speed based on temperature
        curr_speed = fan_controller.set_speed_by_temperature(temp)
        
        # Handle web server requests
        sensor_data = {
            "temperature": temp if temp is not None else 0,
            "voltage": voltage if voltage is not None else 0,
            "current": current if current is not None else 0,
            "power": power if power is not None else 0,
            "consumption": consumption if consumption is not None else 0,
            "curr_speed": curr_speed if curr_speed is not None else 0,
        }
        web_server.accept_connection(wifi_manager, sensor_data, fan_controller)
        
        # Verbose MQTT debugging
        if ENABLE_MQTT:
            if not mqtt_connected:
                print("MQTT not connected, trying to reconnect...")
                mqtt_connected = mqtt_manager.connect()
            else:
                # Check for incoming MQTT messages
                mqtt_manager.check_msgs()
                
                # Publish sensor data periodically
                mqtt_update_counter += 1
                if mqtt_update_counter >= mqtt_update_interval * 10:
                    mqtt_update_counter = 0
                    print(f"Publishing MQTT data: temp={temp}, consumption={consumption}")
                    success = mqtt_manager.publish_sensor_data(
                        temperature=temp,
                        consumption=consumption,
                        voltage=voltage,
                        current=current,
                        power=power,
                        curr_speed=curr_speed,
                    )
                    if success:
                        print("MQTT data published successfully")
                    else:
                        print("Failed to publish MQTT data")
        
        # Short delay to prevent CPU overload and accept all requests
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Program stopped by user")
    if ENABLE_MQTT and mqtt_connected:
        mqtt_manager.disconnect()
except Exception as e:
    print(f"Error in main loop: {e}")
    # In case of error, try to restart
    import machine
    machine.reset()
