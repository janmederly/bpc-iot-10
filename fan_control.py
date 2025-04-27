from machine import Pin
import config

class FanController:
    def __init__(self, pin_num=None):
        """Initialize fan controller
        
        Args:
            pin_num: GPIO pin number for fan control (PWM will be implemented later)
        """
        self.led = Pin("LED", Pin.OUT)  # Onboard LED as visual indicator
        
        # For future PWM implementation
        self.pin_num = pin_num
        self.fan_pin = None
        if pin_num is not None:
            self.fan_pin = Pin(pin_num, Pin.OUT)
        
        # Load settings
        settings = config.load_settings()
        self.enabled = settings.get("fan_enabled", False)
        self.update_state()
    
    def enable(self):
        """Enable fan"""
        self.enabled = True
        self.update_state()
    
    def disable(self):
        """Disable fan"""
        self.enabled = False
        self.update_state()
    
    def update_state(self):
        """Update fan state based on settings"""
        if self.enabled:
            self.led.on()
            if self.fan_pin:
                self.fan_pin.on()
        else:
            self.led.off()
            if self.fan_pin:
                self.fan_pin.off()
    
    def calc_parabola_vertex(self, x1, y1, x2, y2, x3, y3) -> tuple[float, float, float]:
        """Calculate a parabola given three points
        
        Returns:
            tuple: Coefficients (a, b, c) for the parabola y = ax^2 + bx + c
        """
        denom = (x1-x2) * (x1-x3) * (x2-x3)
        a = (x3 * (y2-y1) + x2 * (y1-y3) + x1 * (y3-y2)) / denom
        b = (x3*x3 * (y1-y2) + x2*x2 * (y3-y1) + x1*x1 * (y2-y3)) / denom
        c = (x2 * x3 * (x2-x3) * y1+x3 * x1 * (x3-x1) * y2+x1 * x2 * (x1-x2) * y3) / denom
        return a, b, c
    
    def count_pwm(self, temp, a, b, c) -> float:  
        """Calculate PWM value based on temperature and curve coefficients
        
        Args:
            temp: Current temperature
            a, b, c: Coefficients for the parabola y = ax^2 + bx + c
            
        Returns:
            float: PWM value (0-100%)
        """
        pwm = a*temp*temp + b*temp + c
        return max(0, min(100, pwm))  # Clamp between 0-100%
    
    def set_speed_by_temperature(self, temp) -> float | None:
        """Adjust fan speed based on temperature
        
        Args:
            temp: Current temperature in Celsius
        """
        if not self.enabled:
            return None
        
        # Get temperature thresholds from config
        settings = config.load_settings()
        low = settings.get("low_temp", 20)
        medium = settings.get("medium_temp", 50)
        high = settings.get("high_temp", 100)
        
        # Define fan curve points (temp, pwm%)
        x1, y1 = low, 0      # Low temp -> 0% speed
        x2, y2 = medium, 50  # Medium temp -> 50% speed
        x3, y3 = high, 100   # High temp -> 100% speed
        
        # Calculate curve coefficients
        a, b, c = self.calc_parabola_vertex(x1, y1, x2, y2, x3, y3)
        
        # Calculate PWM based on current temperature
        pwm_percent = self.count_pwm(temp, a, b, c)
        
        # TODO: Implement PWM control when hardware is connected
        print(f"Fan speed set to {pwm_percent:.1f}% at temperature {temp:.1f}°C")
        
        # For now, just use on/off control
        if pwm_percent > 0:
            self.led.on()
            if self.fan_pin:
                self.fan_pin.on()
        else:
            self.led.off()
            if self.fan_pin:
                self.fan_pin.off()

        return pwm_percent
