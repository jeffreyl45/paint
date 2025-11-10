"""
Canvas module for drawing operations.
"""
import cv2
import numpy as np


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
    
    def draw_line(self, x, y, color, thickness):
        """
        Draw a line from previous position to current position.
        
        Args:
            x: Current x coordinate
            y: Current y coordinate
            color: Line color in BGR format
            thickness: Line thickness
        """
        if self.prev_x is not None and self.prev_y is not None:
            cv2.line(self.canvas, (self.prev_x, self.prev_y), (x, y), color, thickness)
        self.prev_x, self.prev_y = x, y
    
    def reset_position(self):
        """Reset the previous drawing position."""
        self.prev_x, self.prev_y = None, None
    
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
