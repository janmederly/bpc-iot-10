import socket
import json
import config
from html_templates import dashboard_html, settings_html, wifi_setup_html

class WebServer:
    def __init__(self, port=80):
        """Initialize web server on the specified port"""
        self.port = port
        self.sock = socket.socket()
        self.sock.settimeout(0.01)
        self.sock.bind(('0.0.0.0', port))
        self.sock.listen(1)
        print(f"Web server started on port {port}")
    
    def send_response(self, client, content, content_type="text/html"):
        """Send HTTP response to client"""
        client.send(f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nConnection: close\r\n\r\n")
        if isinstance(content, str):
            for line in content.splitlines():
                client.send(line + "\n")
        else:
            client.send(content)
    
    def handle_request(self, request, client, wifi_manager, sensor_data, fan_controller=None):
        """Handle HTTP request and send appropriate response"""
        request_parts = request.split(' ')
        if len(request_parts) < 2:
            return
        
        path = request_parts[1]
        
        # If not connected to WiFi, show setup page
        if not wifi_manager.is_connected:
            if path.startswith("/wifi_save?"):
                try:
                    query = path.split('?')[1]
                    new_creds = {}
                    for arg in query.split('&'):
                        key, value = arg.split('=')
                        new_creds[key] = value
                    
                    wifi_manager.save_credentials(new_creds.get("ssid", ""), new_creds.get("pswd", ""))
                    self.send_response(client, "<html><body><h2>Credentials saved. Please restart the Pico manually.</h2></body></html>")
                except Exception as e:
                    print(f"Failed to save credentials: {e}")
                    self.send_response(client, "<html><body><h2>Error saving credentials.</h2></body></html>")
                return
            
            # Show WiFi setup page
            self.send_response(client, wifi_setup_html)
            return
        
        # Handle API endpoints
        if path.startswith("/data"):
            self.send_response(
                client, 
                json.dumps({
                    "temp": sensor_data["temperature"],
                    "volt": sensor_data["voltage"],
                    "curr": sensor_data["current"],
                    "power": sensor_data["power"],
                    "consumption": sensor_data["consumption"],
                    "curr_speed": sensor_data["curr_speed"]
                }),
                "application/json"
            )
            return
        
        if path.startswith("/set_curve"):
            try:
                query = path.split('?')[1]
                settings = config.load_settings()
                
                for arg in query.split('&'):
                    key, value = arg.split('=')
                    if key == 'low': settings["low_temp"] = int(value)
                    if key == 'medium': settings["medium_temp"] = int(value)
                    if key == 'high': settings["high_temp"] = int(value)
                
                config.save_settings(settings)
                self.send_response(client, "OK", "text/plain")
            except Exception as e:
                print(f"Error setting fan curve: {e}")
                self.send_response(client, "Error", "text/plain")
            return
        
        if path.startswith("/fan/"):
            action = path.split('/')[-1]
            settings = config.load_settings()
            
            if action == "on":
                settings["fan_enabled"] = True
                if fan_controller:
                    fan_controller.enable()
                self.send_response(client, "Fan enabled", "text/plain")
            elif action == "off":
                settings["fan_enabled"] = False
                if fan_controller:
                    fan_controller.disable()
                self.send_response(client, "Fan disabled", "text/plain")
            
            config.save_settings(settings)
            return
        
        # Handle page requests
        if path.startswith("/settings"):
            self.send_response(client, settings_html)
        else:
            self.send_response(client, dashboard_html)

    def accept_connection(self, wifi_manager, sensor_data, fan_controller=None):
        """Accept and process a single client connection
        
        Args:
            wifi_manager: WiFi manager instance
            sensor_data: Tuple of (temperature, voltage, current, power, consumption)
            fan_controller: Fan controller instance (optional)
        """
        try:
            client, addr = self.sock.accept()
            client.settimeout(0.5)
            request = client.recv(1024).decode('utf-8')
            
            if request:
                print(f"Request from {addr}:", request.splitlines()[0] if request else "Empty request")
                self.handle_request(request, client, wifi_manager, sensor_data, fan_controller)
            
            client.close()
            return True
        except OSError as e:
            # Socket timeout (no connection available) - this is normal
            if e.args[0] == 110:  # ETIMEDOUT
                return False
            print(f"Socket error: {e}")
            return False
        except Exception as e:
            print(f"Error handling connection: {e}")
            return False
