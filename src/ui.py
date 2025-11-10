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
        
        # Minimum dimensions for proper display
        self.min_button_width = 60
        self.min_button_spacing = 5
    
    def get_scale_factor(self, frame_width):
        """
        Calculate scale factor based on frame width.
        
        Args:
            frame_width: Width of the frame
            
        Returns:
            float: Scale factor (0.5 to 1.0)
        """
        # Scale down UI elements for smaller screens
        if frame_width < 600:
            return 0.5
        elif frame_width < 800:
            return 0.7
        elif frame_width < 1000:
            return 0.85
        else:
            return 1.0
    
    def draw_color_palette(self, frame, current_color, eraser_mode):
        """
        Draw color palette on the frame.
        
        Args:
            frame: Frame to draw on
            current_color: Currently selected color
            eraser_mode: Whether eraser mode is active
        """
        frame_width = frame.shape[1]
        scale = self.get_scale_factor(frame_width)
        
        # Calculate dynamic palette height
        dynamic_palette_height = int(self.palette_height * scale)
        
        # Calculate how much space we need for buttons on the right
        # Reserve space for brush indicator, eraser, and clear buttons
        reserved_width = int(350 * scale)
        available_width = max(frame_width - reserved_width, frame_width // 2)
        
        color_box_width = available_width // len(self.colors)
        
        # Calculate text size based on scale
        text_scale = 0.3 + (0.3 * scale)  # Range from 0.3 to 0.6
        text_thickness = max(1, int(2 * scale))
        
        for i, (color, name) in enumerate(self.colors):
            x1 = i * color_box_width
            x2 = (i + 1) * color_box_width
            
            # Draw color box
            cv2.rectangle(frame, (x1, 0), (x2, dynamic_palette_height), color, -1)
            
            # Highlight selected color
            if color == current_color and not eraser_mode:
                highlight_thickness = max(2, int(5 * scale))
                cv2.rectangle(frame, (x1, 0), (x2, dynamic_palette_height), 
                            (0, 255, 0), highlight_thickness)
            
            # Add text label if there's enough space
            if color_box_width > 30:
                label = name if color_box_width > 50 else name[:3]
                text_y = max(15, int(20 * scale))
                cv2.putText(frame, label, (x1 + 5, text_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, text_scale, (255, 255, 255), text_thickness)
    
    def draw_button(self, frame, x1, y1, x2, y2, label, is_active=False, scale=1.0):
        """
        Draw a button on the frame.
        
        Args:
            frame: Frame to draw on
            x1, y1: Top-left corner
            x2, y2: Bottom-right corner
            label: Button text
            is_active: Whether button is in active state
            scale: Scale factor for text
        """
        color = (100, 255, 100) if is_active else (200, 200, 200)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)
        
        # Calculate text size based on scale and button size
        button_width = x2 - x1
        text_scale = min(0.5 * scale, button_width / 100)  # Adapt to button width
        text_thickness = max(1, int(2 * scale))
        
        # Center text
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, text_scale, text_thickness)[0]
        text_x = x1 + (x2 - x1 - text_size[0]) // 2
        text_y = y1 + (y2 - y1 + text_size[1]) // 2
        
        cv2.putText(frame, label, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, text_scale, (0, 0, 0), text_thickness)
    
    def draw_buttons(self, frame, eraser_mode, brush_size, show_webcam=False):
        """
        Draw all control buttons and brush size indicator.
        
        Args:
            frame: Frame to draw on
            eraser_mode: Whether eraser mode is active
            brush_size: Current brush size
            show_webcam: Whether webcam is visible
        """
        width = frame.shape[1]
        scale = self.get_scale_factor(width)
        
        # Calculate dynamic button dimensions
        button_height = int(60 * scale)
        button_width = int(90 * scale)
        spacing = int(10 * scale)
        margin = int(10 * scale)
        
        # Calculate positions from right to left
        # Clear button (rightmost)
        clear_x2 = width - margin
        clear_x1 = clear_x2 - button_width
        
        # Eraser button
        eraser_x2 = clear_x1 - spacing
        eraser_x1 = eraser_x2 - button_width
        
        # Brush indicator position
        brush_x = eraser_x1 - spacing - int(120 * scale)
        
        # All buttons at the same y position
        button_y1 = margin
        button_y2 = button_y1 + button_height
        
        # Draw buttons
        self.draw_button(frame, eraser_x1, button_y1, eraser_x2, button_y2, 
                        "ERASE", eraser_mode, scale)
        self.draw_button(frame, clear_x1, button_y1, clear_x2, button_y2, 
                        "CLEAR", False, scale)
        
        # Brush size indicator
        brush_text_scale = 0.3 + (0.2 * scale)
        brush_text_thickness = max(1, int(2 * scale))
        brush_y = button_y1 + int(25 * scale)
        
        cv2.putText(frame, f"Brush: {brush_size}px", (brush_x, brush_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, brush_text_scale, (0, 0, 0), brush_text_thickness)
        cv2.putText(frame, "[+/-]", (brush_x, brush_y + int(25 * scale)), 
                   cv2.FONT_HERSHEY_SIMPLEX, brush_text_scale * 0.8, (100, 100, 100), 
                   max(1, brush_text_thickness - 1))
        
        # Webcam indicator (small icon/text)
        webcam_x = brush_x - int(100 * scale)
        webcam_status = "Cam:ON" if show_webcam else "Cam:OFF"
        webcam_color = (0, 200, 0) if show_webcam else (150, 150, 150)
        cv2.putText(frame, webcam_status, (webcam_x, brush_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, brush_text_scale * 0.9, webcam_color, 
                   brush_text_thickness)
        cv2.putText(frame, "[v]", (webcam_x, brush_y + int(25 * scale)), 
                   cv2.FONT_HERSHEY_SIMPLEX, brush_text_scale * 0.8, (100, 100, 100), 
                   max(1, brush_text_thickness - 1))
        
        # Store button positions for click detection
        self.eraser_button_bounds = (eraser_x1, button_y1, eraser_x2, button_y2)
        self.clear_button_bounds = (clear_x1, button_y1, clear_x2, button_y2)
    
    def draw_instructions(self, frame):
        """
        Draw instruction text on the frame.
        
        Args:
            frame: Frame to draw on
        """
        width = frame.shape[1]
        scale = self.get_scale_factor(width)
        
        # Dynamic text based on screen size
        if width < 600:
            instructions = [
                "Point to draw | Palm to select",
                "+/- brush | v:cam | s:save | c:clear | q:quit"
            ]
        elif width < 800:
            instructions = [
                "Point finger to draw",
                "Palm (5 fingers) to select",
                "+/- brush | v:cam | s:save | c:clear | q:quit"
            ]
        else:
            instructions = [
                "Point index finger to draw",
                "Show palm (5 fingers) to select color/button",
                "Press '+'/'-' brush | 'v' webcam | 's' save | 'c' clear | 'q' quit" 
            ]
        
        text_scale = 0.3 + (0.2 * scale)
        text_thickness = max(1, int(1 * scale))
        line_spacing = int(25 * scale)
        
        y_offset = frame.shape[0] - int(80 * scale)
        for i, text in enumerate(instructions):
            cv2.putText(frame, text, (10, y_offset + i * line_spacing), 
                       cv2.FONT_HERSHEY_SIMPLEX, text_scale, (50, 50, 50), text_thickness)
    
    def draw_status(self, frame, status):
        """
        Draw status text on the frame.
        
        Args:
            frame: Frame to draw on
            status: Status message to display
        """
        h = frame.shape[0]
        width = frame.shape[1]
        scale = self.get_scale_factor(width)
        
        text_scale = 0.4 + (0.3 * scale)
        text_thickness = max(1, int(2 * scale))
        
        cv2.putText(frame, status, (10, h - int(100 * scale)), 
                   cv2.FONT_HERSHEY_SIMPLEX, text_scale, (0, 255, 0), text_thickness)
    
    def draw(self, frame, current_color, eraser_mode, status, brush_size, show_webcam=False):
        """
        Draw all UI elements on the frame.
        
        Args:
            frame: Frame to draw on
            current_color: Currently selected color
            eraser_mode: Whether eraser mode is active
            status: Status message to display
            brush_size: Current brush size
            show_webcam: Whether webcam is visible
        """
        self.draw_color_palette(frame, current_color, eraser_mode)
        self.draw_buttons(frame, eraser_mode, brush_size, show_webcam)
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
        if hasattr(self, 'eraser_button_bounds'):
            x1, y1, x2, y2 = self.eraser_button_bounds
            return x1 < x < x2 and y1 < y < y2
        # Fallback to old calculation
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
        if hasattr(self, 'clear_button_bounds'):
            x1, y1, x2, y2 = self.clear_button_bounds
            return x1 < x < x2 and y1 < y < y2
        # Fallback to old calculation
        return frame_width - 100 < x < frame_width - 10 and 10 < y < 70
