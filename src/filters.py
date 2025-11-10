"""
Smoothing filters for reducing jitter and noise in hand tracking.
"""
import math


class OneEuroFilter:
    """
    One Euro Filter for smoothing noisy signals.
    
    Provides low noise at low speeds and responsiveness at high speeds.
    Based on: http://cristal.univ-lille.fr/~casiez/1euro/
    """
    
    def __init__(self, freq=30.0, min_cutoff=1.0, beta=0.007, dcutoff=1.0):
        """
        Initialize the One Euro Filter.
        
        Args:
            freq: Estimated signal frequency (Hz), typically camera FPS
            min_cutoff: Minimum cutoff frequency (lower = more smoothing)
            beta: Speed coefficient (higher = more responsive to fast movements)
            dcutoff: Cutoff frequency for derivative
        """
        self.freq = freq
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.dcutoff = dcutoff
        self.x_prev = None
        self.dx_prev = 0.0
    
    def _smoothing_factor(self, cutoff):
        """Calculate smoothing factor (alpha) from cutoff frequency."""
        tau = 1.0 / (2 * math.pi * cutoff)
        te = 1.0 / self.freq
        return 1.0 / (1.0 + tau / te)
    
    def filter(self, x, timestamp=None):
        """
        Apply the filter to a new value.
        
        Args:
            x: New raw value
            timestamp: Optional timestamp (for variable frame rates)
            
        Returns:
            float: Filtered value
        """
        # Initialize on first call
        if self.x_prev is None:
            self.x_prev = x
            self.dx_prev = 0.0
            return x
        
        # Calculate derivative
        dx = x - self.x_prev
        
        # Smooth the derivative
        alpha_d = self._smoothing_factor(self.dcutoff)
        dx_smooth = alpha_d * dx + (1.0 - alpha_d) * self.dx_prev
        
        # Calculate adaptive cutoff frequency
        cutoff = self.min_cutoff + self.beta * abs(dx_smooth)
        
        # Smooth the signal
        alpha = self._smoothing_factor(cutoff)
        x_filtered = alpha * x + (1.0 - alpha) * self.x_prev
        
        # Update state
        self.x_prev = x_filtered
        self.dx_prev = dx_smooth
        
        return x_filtered
    
    def reset(self):
        """Reset the filter state."""
        self.x_prev = None
        self.dx_prev = 0.0


class ExponentialSmoothing:
    """
    Simple exponential smoothing filter.
    
    Fast and lightweight alternative to One Euro filter.
    """
    
    def __init__(self, alpha=0.45):
        """
        Initialize exponential smoothing.
        
        Args:
            alpha: Smoothing factor (0 = max smoothing, 1 = no smoothing)
        """
        self.alpha = alpha
        self.value = None
    
    def filter(self, x):
        """
        Apply exponential smoothing.
        
        Args:
            x: New raw value
            
        Returns:
            float: Filtered value
        """
        if self.value is None:
            self.value = x
            return x
        
        self.value = self.alpha * x + (1.0 - self.alpha) * self.value
        return self.value
    
    def reset(self):
        """Reset the filter state."""
        self.value = None


class OutlierGuard:
    """
    Guards against outlier jumps in position data.
    """
    
    def __init__(self, max_jump=80.0, dead_zone=2.0):
        """
        Initialize outlier guard.
        
        Args:
            max_jump: Maximum allowed position jump (pixels)
            dead_zone: Minimum movement to register (pixels)
        """
        self.max_jump = max_jump
        self.dead_zone = dead_zone
        self.prev_pos = None
        self.prev_velocity = 0.0
    
    def filter(self, x, y):
        """
        Check if position is valid and apply dead-zone.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            tuple: (filtered_x, filtered_y, is_valid)
        """
        if self.prev_pos is None:
            self.prev_pos = (x, y)
            return x, y, True
        
        # Calculate distance from previous position
        dx = x - self.prev_pos[0]
        dy = y - self.prev_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check for outliers (unrealistic velocity)
        # If jump is too large and we weren't moving fast, it's likely noise
        if distance > self.max_jump and self.prev_velocity < self.max_jump * 0.5:
            # Reject outlier, return previous position
            return self.prev_pos[0], self.prev_pos[1], False
        
        # Apply dead-zone to reduce micro-tremor
        if distance < self.dead_zone:
            # No meaningful movement
            return self.prev_pos[0], self.prev_pos[1], True
        
        # Valid movement
        self.prev_velocity = distance
        self.prev_pos = (x, y)
        return x, y, True
    
    def reset(self):
        """Reset the guard state."""
        self.prev_pos = None
        self.prev_velocity = 0.0
