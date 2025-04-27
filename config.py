import json

def load_settings():
    """Load settings from settings.json file"""
    try:
        with open("settings.json") as fd:
            return json.load(fd)
    except OSError:
        # Create default settings if file doesn't exist
        default_settings = {
            "low_temp": 20, 
            "medium_temp": 50, 
            "high_temp": 100,
            "fan_enabled": False,
        }
        save_settings(default_settings)
        return default_settings

def save_settings(settings):
    """Save settings to settings.json file"""
    with open("settings.json", "w") as fd:
        json.dump(settings, fd)

def load_wifi_credentials():
    """Load WiFi credentials from creds.json file"""
    try:
        with open("creds.json") as fd:
            creds = json.load(fd)
            return creds.get("SSID", ""), creds.get("PSWD", "")
    except OSError:
        # Create default credentials file if it doesn't exist
        with open("creds.json", "w") as fd:
            creds = {"SSID": "", "PSWD": ""}
            json.dump(creds, fd)
            return "", ""

def save_wifi_credentials(ssid, password):
    """Save WiFi credentials to creds.json file"""
    try:
        with open("creds.json") as fd:
            creds = json.load(fd)
    except OSError:
        creds = {}
    
    creds["SSID"] = ssid
    creds["PSWD"] = password
    
    with open("creds.json", "w") as fd:
        json.dump(creds, fd)

def load_mqtt_credentials():
    """Load MQTT credentials from creds.json file"""
    try:
        with open("creds.json") as fd:
            creds = json.load(fd)
            
            mqtt_fields = {
                "_MQTT_CLIENT_ID_": "ID",
                "_MQTT_REMOTE_SERVER_IP_": "your.mqtt.server.ip",
                "_MQTT_ACCESS_TOKEN_": "your_access_token",
                "_MQTT_PASSWORD_": "your_mqtt_password",
                "_MQTT_REMOTE_SERVER_PORT_": "1883"
            }
            
            modified = False
            for field, default_value in mqtt_fields.items():
                if field not in creds:
                    creds[field] = default_value
                    modified = True
                    
            if modified:
                with open("creds.json", "w") as fdw:
                    json.dump(creds, fdw)
                    
            return creds
    except OSError:
        # Create default credentials file if it doesn't exist
        default_creds = {
            "SSID": "SSID", 
            "PSWD": "PASS",
            "_MQTT_CLIENT_ID_": "ID",
            "_MQTT_REMOTE_SERVER_IP_": "your.mqtt.server.ip",
            "_MQTT_ACCESS_TOKEN_": "your_access_token",
            "_MQTT_PASSWORD_": "your_mqtt_password",
            "_MQTT_REMOTE_SERVER_PORT_": "1883"
        }
        with open("creds.json", "w") as fd:
            json.dump(default_creds, fd)
        return default_creds
