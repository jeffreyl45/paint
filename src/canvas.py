"""
Canvas module for drawing operations.
"""
import cv2
import numpy as np
from collections import deque


class Canvas:
    """Manages the drawing canvas."""
    
    def __init__(self, width=640, height=480, bg_color=(255, 255, 255)):
        """
        Initialize the canvas.
        
        Args:
            width: Canvas width
            height: Canvas height
            bg_color: Background color in BGR format
        """
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.canvas = np.ones((height, width, 3), dtype=np.uint8) * np.array(bg_color, dtype=np.uint8)
        self.prev_x = None
        self.prev_y = None
        
        # Smoothing parameters
        self.position_buffer = deque(maxlen=5)  # Store last 5 positions for smoothing
    
    def draw_line(self, x, y, color, thickness):
        """
        Draw a line from previous position to current position with smoothing.
        
        Args:
            x: Current x coordinate
            y: Current y coordinate
            color: Line color in BGR format
            thickness: Line thickness
        """
        # Add position to buffer
        self.position_buffer.append((x, y))
        
        # Calculate smoothed position
        if len(self.position_buffer) > 0:
            avg_x = int(sum(pos[0] for pos in self.position_buffer) / len(self.position_buffer))
            avg_y = int(sum(pos[1] for pos in self.position_buffer) / len(self.position_buffer))
            smoothed_x, smoothed_y = avg_x, avg_y
        else:
            smoothed_x, smoothed_y = x, y
        
        if self.prev_x is not None and self.prev_y is not None:
            # Draw smooth line
            cv2.line(self.canvas, (self.prev_x, self.prev_y), (smoothed_x, smoothed_y), 
                    color, thickness, cv2.LINE_AA)
        else:
            # Draw a dot for the starting point
            cv2.circle(self.canvas, (smoothed_x, smoothed_y), thickness // 2, color, -1)
            
        self.prev_x, self.prev_y = smoothed_x, smoothed_y
    
    def reset_position(self):
        """Reset the previous drawing position."""
        self.prev_x, self.prev_y = None, None
        self.position_buffer.clear()
    
    def clear(self):
        """Clear the canvas to background color."""
        self.canvas = np.ones((self.height, self.width, 3), dtype=np.uint8) * np.array(self.bg_color, dtype=np.uint8)
        self.reset_position()
    
    def resize(self, width, height):
        """
        Resize the canvas.
        
        Args:
            width: New width
            height: New height
        """
        if (self.height, self.width) != (height, width):
            self.canvas = cv2.resize(self.canvas, (width, height))
            self.width = width
            self.height = height
    
    def get_canvas(self):
        """
        Get the current canvas.
        
        Returns:
            numpy.ndarray: Canvas image
        """
        return self.canvas
    
    def save(self, filename):
        """
        Save the canvas to a file.
        
        Args:
            filename: Path to save the image
            
        Returns:
            bool: True if save was successful
        """
        return cv2.imwrite(filename, self.canvas)
