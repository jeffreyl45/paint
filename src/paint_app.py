"""
Main paint application logic.
"""
import cv2
import numpy as np
from src.gesture_recognizer import GestureRecognizer
from src.canvas import Canvas
from src.ui import UI


class PaintApp:
    """Main paint application controller."""
    
    def __init__(self):
        """Initialize the paint application."""
        # Initialize components
        self.gesture_recognizer = GestureRecognizer()
        self.canvas = Canvas()
        self.ui = UI()
        
        # Drawing state
        self.current_color = (0, 0, 255)  # Red in BGR
        self.brush_size = 5
        self.eraser_mode = False
        
        # Camera
        self.cap = None
    
    def process_drawing_gesture(self, x, y, frame_height, frame_width):
        """
        Process drawing gesture.
        
        Args:
            x: X coordinate
            y: Y coordinate
            frame_height: Frame height
            frame_width: Frame width
        """
        if y > self.ui.palette_height:  # Below UI area
            color = (255, 255, 255) if self.eraser_mode else self.current_color
            thickness = self.brush_size * 3 if self.eraser_mode else self.brush_size
            self.canvas.draw_line(x, y, color, thickness)
    
    def process_selection_gesture(self, x, y, frame_height, frame_width):
        """
        Process selection gesture.
        
        Args:
            x: X coordinate
            y: Y coordinate
            frame_height: Frame height
            frame_width: Frame width
        """
        # Check if selecting color
        color_selection = self.ui.get_color_from_position(x, y, frame_width)
        if color_selection:
            self.current_color = color_selection[0]
            self.eraser_mode = False
            return
        
        # Check if clicking eraser button
        if self.ui.is_eraser_button_clicked(x, y, frame_width):
            self.eraser_mode = not self.eraser_mode
            return
        
        # Check if clicking clear button
        if self.ui.is_clear_button_clicked(x, y, frame_width):
            self.canvas.clear()
    
    def process_hand(self, hand_landmarks, frame_shape):
        """
        Process hand landmarks and perform actions.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            frame_shape: Shape of the frame (h, w, c)
            
        Returns:
            bool: True if currently drawing
        """
        h, w, _ = frame_shape
        x, y = self.gesture_recognizer.get_index_finger_position(hand_landmarks, frame_shape)
        
        # Drawing mode - index finger only
        if self.gesture_recognizer.is_index_finger_up(hand_landmarks):
            self.process_drawing_gesture(x, y, h, w)
            return True
        
        # Selection mode - all fingers up
        elif self.gesture_recognizer.is_all_fingers_up(hand_landmarks):
            self.canvas.reset_position()
            self.process_selection_gesture(x, y, h, w)
            return False
        
        else:
            self.canvas.reset_position()
            return False
    
    def blend_canvas_with_frame(self, frame):
        """
        Blend the canvas drawings with the camera frame.
        
        Args:
            frame: Camera frame
            
        Returns:
            numpy.ndarray: Blended frame
        """
        canvas_img = self.canvas.get_canvas()
        
        # Create mask from canvas
        mask = cv2.cvtColor(canvas_img, cv2.COLOR_BGR2GRAY)
        mask = cv2.threshold(mask, 250, 255, cv2.THRESH_BINARY_INV)[1]
        mask_3channel = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        
        # Apply canvas drawings on top of frame
        return np.where(mask_3channel > 0, canvas_img, frame)
    
    def process_frame(self, frame):
        """
        Process a single frame.
        
        Args:
            frame: Camera frame
            
        Returns:
            tuple: (processed_frame, is_drawing)
        """
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        # Resize canvas to match frame if needed
        self.canvas.resize(w, h)
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.gesture_recognizer.process_frame(rgb_frame)
        
        # Process hand landmarks
        drawing = False
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks on frame
                self.gesture_recognizer.draw_landmarks(frame, hand_landmarks)
                
                # Process hand gestures
                drawing = self.process_hand(hand_landmarks, frame.shape)
        else:
            self.canvas.reset_position()
        
        # Blend canvas with frame
        frame_with_canvas = self.blend_canvas_with_frame(frame)
        
        # Determine status
        if drawing:
            status = "DRAWING"
        elif results.multi_hand_landmarks:
            status = "SELECTION MODE"
        else:
            status = "NO HAND DETECTED"
        
        # Draw UI
        self.ui.draw(frame_with_canvas, self.current_color, self.eraser_mode, status)
        
        return frame_with_canvas, drawing
    
    def save_canvas(self):
        """Save the current canvas to a file."""
        filename = f'fingertip_painting_{cv2.getTickCount()}.png'
        if self.canvas.save(filename):
            print(f'Drawing saved as {filename}')
            return True
        return False
    
    def run(self):
        """Run the main application loop."""
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("Fingertip Paint App Started!")
        print("Gestures:")
        print("  - Point with index finger to draw")
        print("  - Show all fingers (open palm) to select colors/buttons")
        print("  - Press 's' to save your drawing")
        print("  - Press 'q' to quit")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Failed to capture frame")
                    break
                
                # Process frame
                processed_frame, _ = self.process_frame(frame)
                
                # Display
                cv2.imshow('Fingertip Paint', processed_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self.save_canvas()
        
        finally:
            # Cleanup
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            self.gesture_recognizer.close()
