import time

class ConsumptionManager:

    def __init__(self):
        """Initialize consumption manager"""
        self.consumption = 0.0
        self.last_time = time.time_ns()

    def update_consumption(self, current, voltage):
        """Update consumption calculation based on current and voltage"""
        curr_time = time.time_ns()
        elapsed_time = float((curr_time - self.last_time)) / 1000000000
        self.last_time = curr_time
        if elapsed_time > 1.8:
            return 0
        self.consumption += (current * voltage * elapsed_time) / 1000 / 3600
        return self.consumption
    
    def get_consumption(self):
        """Get the current consumption value"""
        return self.consumption
    
    def reset_consumption(self):
        """Reset the consumption value"""
        self.consumption = 0.0
        self.curr_time = time.time()
        self.last_time = self.curr_time