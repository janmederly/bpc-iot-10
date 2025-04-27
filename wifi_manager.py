import network
import time
from machine import Pin
import config

class WiFiManager:
    def __init__(self):
        """Initialize WiFi manager"""
        self.led = Pin("LED", Pin.OUT)
        self.is_connected = False
    
    def start_ap_mode(self):
        """Start access point mode for WiFi configuration"""
        ap = network.WLAN(network.AP_IF)
        ap.config(essid="Projekt10_Setup", password="123456789")
        ap.active(True)
        print('AP Mode started: Projekt10_Setup , PSWD = 123456789')
        return True
    
    def connect_to_wifi(self):
        """Connect to WiFi using stored credentials
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        ssid, pswd = config.load_wifi_credentials()
        if not ssid:
            print("No SSID configured, starting AP mode")
            return self.start_ap_mode()
        
        wlan = network.WLAN(network.STA_IF)
        
        for i in range(3):  # 3 attempts
            print(f"WiFi connect attempt {i+1}/3")
            wlan.active(False)   # Reset WiFi module
            time.sleep(1)
            wlan.active(True)
            
            wlan.connect(ssid, pswd)
            
            timeout = 10
            while timeout > 0:
                if wlan.isconnected():
                    print('WiFi connected:', wlan.ifconfig())
                    self.led.on()
                    self.is_connected = True
                    return True
                self.led.toggle()
                time.sleep(1)
                timeout -= 1
            
            print(f"Attempt {i+1} failed, retrying...")
        
        print('Failed to connect after 3 attempts, switching to AP mode')
        self.led.off()
        self.is_connected = False
        return self.start_ap_mode()
    
    def save_credentials(self, ssid, password):
        """Save new WiFi credentials"""
        config.save_wifi_credentials(ssid, password)
        print(f"Saved new credentials for SSID: {ssid}")
