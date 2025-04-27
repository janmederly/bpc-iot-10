import random
import BME280
from machine import Pin, I2C

class SensorManager:
    def __init__(self, use_bme280=False):
        """Initialize sensor manager with real or simulated sensors
        
        Args:
            use_bme280: If True, use BME280 sensor; otherwise, use simulated values
        """
        self.use_bme280 = use_bme280
        
        # Initialize I2C for BME280
        if self.use_bme280:
            self.i2c = I2C(0, scl=Pin(1), sda=Pin(0))
            try:
                self.bme = BME280.BME280(i2c=self.i2c)
                print("BME280 sensor initialized")
            except Exception as e:
                print(f"Error initializing BME280: {e}")
                self.use_bme280 = False
                self._init_simulation()
        else:
            print("BME280 not connected, using simulated values")
            self._init_simulation()
    
    def _init_simulation(self):
        """Initialize simulation values"""
        self.sim_temp = 25.0      # Start at room temp
        self.sim_voltage = 230.0  # Start at nominal voltage
        self.sim_current = 1.0    # Start at 1A
        self.sim_humidity = 50.0  # Start at 50% humidity
    
    def read_temperature(self):
        """Read temperature from sensor or simulation"""
        if self.use_bme280:
            try:
                return float(self.bme.temperature[:-1])  # Remove 'C' and convert to float
            except Exception as e:
                print(f"Error reading temperature: {e}")
                # Fall back to simulation if reading fails
                self.use_bme280 = False
                self._init_simulation()
                return self.sim_temp
        else:
            # Simulate temperature with some inertia
            self.sim_temp += random.uniform(-0.3, 0.3)
            self.sim_temp = max(15, min(60, self.sim_temp))  # Keep within reasonable range
            return self.sim_temp
    
    def read_humidity(self):
        """Read humidity from sensor or simulation"""
        if self.use_bme280:
            try:
                return float(self.bme.humidity[:-1])  # Remove '%' and convert to float
            except Exception as e:
                print(f"Error reading humidity: {e}")
                # Fall back to simulation if reading fails
                self.use_bme280 = False
                self._init_simulation()
                return self.sim_humidity
        else:
            # Simulate humidity with some inertia
            self.sim_humidity += random.uniform(-1, 1)
            self.sim_humidity = max(30, min(80, self.sim_humidity))  # Keep within reasonable range
            return self.sim_humidity
    
    def read_electrical_values(self):
        """Read voltage and current from sensors or simulation"""
        if self.use_bme280:
            # In the original code, electrical values were always random
            voltage = 230 + random.uniform(-5, 5)
            current = 1 + random.uniform(-0.5, 5)
        else:
            # Simulate with some inertia
            self.sim_voltage += random.uniform(-0.2, 0.2)
            self.sim_voltage = max(220, min(240, self.sim_voltage))
            self.sim_current += random.uniform(-0.05, 0.05)
            self.sim_current = max(0.5, min(5, self.sim_current))
            voltage = self.sim_voltage
            current = self.sim_current
        
        power = voltage * current
        return voltage, current, power
