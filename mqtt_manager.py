"""
MQTT Manager for IoT Project

Handles connection to MQTT broker and publishing/subscribing to topics
"""
from machine import Pin
import time
import ujson
from umqtt.simple import MQTTClient
from umqtt.simple import MQTTException
from fan_control import FanController
from consumption_calc import ConsumptionManager
import config

class MQTTManager:
    # MQTT Topics
    MQTT_PUB_TOPIC = b"v1/devices/me/telemetry"
    MQTT_SUB_TOPIC = b"v1/devices/me/attributes"
    
    # QoS level
    QOS = 0
    
    # Error messages
    mqtt_error_table = [
        "Connection Accepted", 
        "Connection Refused, Unacceptable Protocol Version",
        "Connection Refused, Identifier Rejected",
        "Connection Refused, Server Unavailable", 
        "Connection Refused, Bad Username or Password", 
        "Connection Refused, Not Authorized"
    ]
    
    def __init__(self, fan_controller: FanController | None = None, consumption_manager: ConsumptionManager | None = None):
        """Initialize MQTT Manager"""
        self.client = None
        self.keepalive_seconds = 60
        self.mqtt_ctr = 0
        self.connected = False
        self.fan_controller = fan_controller
        self.consumption_manager = consumption_manager
        
    def connect(self) -> bool:
        """Connect to MQTT broker using credentials from config"""
        creds = config.load_mqtt_credentials()
        
        if not creds.get("_MQTT_CLIENT_ID_") or not creds.get("_MQTT_REMOTE_SERVER_IP_"):
            print("MQTT credentials not configured")
            return False
            
        try:
            self.client = MQTTClient(
                client_id=creds["_MQTT_CLIENT_ID_"], 
                server=creds["_MQTT_REMOTE_SERVER_IP_"], 
                user=creds["_MQTT_ACCESS_TOKEN_"], 
                keepalive=self.keepalive_seconds, 
                port=int(creds["_MQTT_REMOTE_SERVER_PORT_"]), 
                password=creds.get("_MQTT_PASSWORD_", "test")
            )
            
            # Set callback for received messages
            self.client.set_callback(self.on_message_callback)
            
            # Connect to broker
            self.client.connect()
            
            # Subscribe to topic
            self.client.subscribe(self.MQTT_SUB_TOPIC)
            
            self.connected = True
            print("Connected to MQTT broker")
            return True
            
        except MQTTException as mqtte:
            error_code = int(str(mqtte))
            error_msg = self.mqtt_error_table[error_code] if error_code < len(self.mqtt_error_table) else str(mqtte)
            print(f"MQTT Connection Error: {error_msg}")
            return False
        except Exception as e:
            print(f"MQTT Error: {repr(e)}")
            return False
    
    def on_message_callback(self, topic, msg):
        """Handle incoming MQTT messages"""
        print("\n===== MQTT MESSAGE RECEIVED =====")
        print(f"Topic: {topic.decode('utf-8') if isinstance(topic, bytes) else topic}")
        print(f"Raw message: {msg.decode('utf-8') if isinstance(msg, bytes) else msg}")
        print("--------------------------------")
        
        try:
            data = ujson.loads(msg)
            print("Parsed JSON data:")
            for key, value in data.items():
                print(f"  {key}: {value}")
                if key == "fan" and self.fan_controller:
                    if value == "on":
                        self.fan_controller.enable()
                    elif value == "off":
                        self.fan_controller.disable()
                    print(f"Fan status: {value}")
                elif key == "consumption" and value == "reset" and self.consumption_manager:
                    self.consumption_manager.reset_consumption()
                    print("Consumption reset")
        except Exception as e:
            print(f"Failed to parse MQTT message as JSON: {e}")
        
        print("=================================\n")
    
    def publish_sensor_data(self, temperature, consumption=None, voltage=None, current=None, power=None, curr_speed=None) -> bool:
        """Publish sensor data to MQTT broker"""
        print("Checking connection")
        if not self.connected or not self.client:
            return False
            
        print("Publishing sensor data to Thingsboard")

        try:
            # Create data payload
            data = {"temperature": temperature}
            
            # Add optional electrical data if available
            if voltage is not None:
                data["voltage"] = voltage
            if current is not None:
                data["current"] = current
            if power is not None:
                data["power"] = power
            if consumption is not None:
                data["consumption"] = consumption
            if curr_speed is not None:
                data["curr_speed"] = curr_speed
                
            # Convert to JSON and publish
            json_data = ujson.dumps(data)
            self.client.publish(self.MQTT_PUB_TOPIC, json_data, qos=self.QOS)
            return True
        except Exception as e:
            print(f"Error publishing to MQTT: {e}")
            return False
    
    def check_msgs(self):
        """Check for incoming MQTT messages and handle keepalive"""
        if not self.connected or not self.client:
            return
            
        try:
            self.client.check_msg()
            self.mqtt_ctr += 1
            
            # Send ping for keepalive
            if self.mqtt_ctr >= (self.keepalive_seconds - 2) / 0.1:
                self.mqtt_ctr = 0
                self.client.ping()
        except Exception as e:
            print(f"MQTT error: {e}")
            self.connected = False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client and self.connected:
            try:
                self.client.disconnect()
                self.connected = False
                print("Disconnected from MQTT broker")
            except:
                pass