"""
UI components for the paint application.
"""
import cv2


class ColorPalette:
    """Color palette configuration."""
    
    COLORS = [
        ((0, 0, 255), "Red"),
        ((0, 255, 0), "Green"),
        ((255, 0, 0), "Blue"),
        ((0, 255, 255), "Yellow"),
        ((255, 0, 255), "Magenta"),
        ((255, 255, 0), "Cyan"),
        ((0, 0, 0), "Black"),
        ((255, 255, 255), "White"),
    ]


class UI:
    """Handles UI rendering."""
    
    def __init__(self, palette_height=80):
        """
        Initialize UI.
        
        Args:
            palette_height: Height of the color palette area
        """
        self.palette_height = palette_height
        self.colors = ColorPalette.COLORS
    
    def draw_color_palette(self, frame, current_color, eraser_mode):
        """
        Draw color palette on the frame.
        
        Args:
            frame: Frame to draw on
            current_color: Currently selected color
            eraser_mode: Whether eraser mode is active
        """
        color_box_width = frame.shape[1] // len(self.colors)
        
        for i, (color, name) in enumerate(self.colors):
            x1 = i * color_box_width
            x2 = (i + 1) * color_box_width
            
            # Draw color box
            cv2.rectangle(frame, (x1, 0), (x2, self.palette_height), color, -1)
            
            # Highlight selected color
            if color == current_color and not eraser_mode:
                cv2.rectangle(frame, (x1, 0), (x2, self.palette_height), (0, 255, 0), 5)
            
            # Add text label
            cv2.putText(frame, name[:3], (x1 + 5, 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    def draw_button(self, frame, x1, y1, x2, y2, label, is_active=False):
        """
        Draw a button on the frame.
        
        Args:
            frame: Frame to draw on
            x1, y1: Top-left corner
            x2, y2: Bottom-right corner
            label: Button text
            is_active: Whether button is in active state
        """
        color = (100, 255, 100) if is_active else (200, 200, 200)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)
        
        # Center text
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        text_x = x1 + (x2 - x1 - text_size[0]) // 2
        text_y = y1 + (y2 - y1 + text_size[1]) // 2
        
        cv2.putText(frame, label, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    
    def draw_buttons(self, frame, eraser_mode):
        """
        Draw all control buttons.
        
        Args:
            frame: Frame to draw on
            eraser_mode: Whether eraser mode is active
        """
        width = frame.shape[1]
        
        # Eraser button
        self.draw_button(frame, width - 210, 10, width - 110, 70, "ERASE", eraser_mode)
        
        # Clear button
        self.draw_button(frame, width - 100, 10, width - 10, 70, "CLEAR")
    
    def draw_instructions(self, frame):
        """
        Draw instruction text on the frame.
        
        Args:
            frame: Frame to draw on
        """
        instructions = [
            "Point index finger straight to draw",
            "Show palm (5 fingers) to select color/button",
            "Press 's' to save | 'q' to quit"
        ]
        
        y_offset = frame.shape[0] - 80
        for i, text in enumerate(instructions):
            cv2.putText(frame, text, (10, y_offset + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def draw_status(self, frame, status):
        """
        Draw status text on the frame.
        
        Args:
            frame: Frame to draw on
            status: Status message to display
        """
        h = frame.shape[0]
        cv2.putText(frame, status, (10, h - 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    def draw(self, frame, current_color, eraser_mode, status):
        """
        Draw all UI elements on the frame.
        
        Args:
            frame: Frame to draw on
            current_color: Currently selected color
            eraser_mode: Whether eraser mode is active
            status: Status message to display
        """
        self.draw_color_palette(frame, current_color, eraser_mode)
        self.draw_buttons(frame, eraser_mode)
        self.draw_instructions(frame)
        self.draw_status(frame, status)
    
    def get_color_from_position(self, x, y, frame_width):
        """
        Get color index from click position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            frame_width: Width of the frame
            
        Returns:
            tuple or None: (color, name) if valid position, None otherwise
        """
        if y < self.palette_height:
            color_box_width = frame_width // len(self.colors)
            color_index = x // color_box_width
            if 0 <= color_index < len(self.colors):
                return self.colors[color_index]
        return None
    
    def is_eraser_button_clicked(self, x, y, frame_width):
        """
        Check if eraser button was clicked.
        
        Args:
            x: X coordinate
            y: Y coordinate
            frame_width: Width of the frame
            
        Returns:
            bool: True if eraser button was clicked
        """
        return frame_width - 210 < x < frame_width - 110 and 10 < y < 70
    
    def is_clear_button_clicked(self, x, y, frame_width):
        """
        Check if clear button was clicked.
        
        Args:
            x: X coordinate
            y: Y coordinate
            frame_width: Width of the frame
            
        Returns:
            bool: True if clear button was clicked
        """
        return frame_width - 100 < x < frame_width - 10 and 10 < y < 70
