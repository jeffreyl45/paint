"""
Main paint application logic.
"""
import cv2
from src.gesture_recognizer import GestureRecognizer
from src.canvas import Canvas
from src.ui import UI


class PaintApp:
    """Main paint application controller."""
    
    def __init__(self):
        """Initialize the paint application."""
        # Initialize components
        self.gesture_recognizer = GestureRecognizer()
        self.canvas = Canvas(width=1000, height=700)
        self.ui = UI()
        
        # Drawing state
        self.current_color = (0, 0, 255)  # Red in BGR
        self.brush_size = 3  # Smaller default size for better control
        self.eraser_mode = False
        
        # Camera
        self.cap = None
        
        # Video feed window size (smaller, just for hand tracking)
        self.video_width = 320
        self.video_height = 240
        
        # Toggle for showing/hiding webcam
        self.show_webcam = False
        
        # Depth-based drawing control
        self.depth_threshold = -0.05  # Adjust this for sensitivity
        self.cursor_x = None
        self.cursor_y = None
        self.is_close_enough = False
    
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
    
    def draw_cursor(self, display, x, y):
        """
        Draw a cursor at the finger position to show where drawing will occur.
        
        Args:
            display: Display image
            x: X coordinate
            y: Y coordinate
        """
        if self.is_close_enough:
            # Drawing active - show filled circle with current color
            cv2.circle(display, (x, y), self.brush_size, self.current_color, -1, cv2.LINE_AA)
            # Add white outline for visibility
            cv2.circle(display, (x, y), self.brush_size + 2, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.circle(display, (x, y), self.brush_size + 3, (0, 0, 0), 1, cv2.LINE_AA)
        else:
            # Not close enough - show hollow circle
            cv2.circle(display, (x, y), self.brush_size, (150, 150, 150), 1, cv2.LINE_AA)
            # Small crosshair
            cross_size = 5
            cv2.line(display, (x - cross_size, y), (x + cross_size, y), 
                    (150, 150, 150), 1, cv2.LINE_AA)
            cv2.line(display, (x, y - cross_size), (x, y + cross_size), 
                    (150, 150, 150), 1, cv2.LINE_AA)
    
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
    
    def create_display_with_video_overlay(self, canvas_img, video_frame):
        """
        Create display with canvas and optional small video overlay.
        
        Args:
            canvas_img: Canvas image
            video_frame: Video frame
            
        Returns:
            numpy.ndarray: Combined display
        """
        # Start with canvas
        display = canvas_img.copy()
        
        # Only show webcam if enabled
        if self.show_webcam:
            # Resize video frame to small size
            small_video = cv2.resize(video_frame, (self.video_width, self.video_height))
            
            # Position for video overlay (bottom right corner)
            y_offset = display.shape[0] - self.video_height - 10
            x_offset = display.shape[1] - self.video_width - 10
            
            # Add border to video
            cv2.rectangle(display, 
                         (x_offset - 2, y_offset - 2), 
                         (x_offset + self.video_width + 2, y_offset + self.video_height + 2),
                         (0, 0, 0), 2)
            
            # Overlay video on canvas
            display[y_offset:y_offset + self.video_height, 
                    x_offset:x_offset + self.video_width] = small_video
        
        return display
    
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
        
        # Keep canvas at a fixed size (800x600)
        canvas_width = 1000
        canvas_height = 700
        if self.canvas.width != canvas_width or self.canvas.height != canvas_height:
            self.canvas.resize(canvas_width, canvas_height)
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.gesture_recognizer.process_frame(rgb_frame)
        
        # Create video preview frame with hand landmarks
        video_preview = frame.copy()
        
        # Process hand landmarks
        drawing = False
        self.is_close_enough = False
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks on video preview
                self.gesture_recognizer.draw_landmarks(video_preview, hand_landmarks)
                
                # Map coordinates from video to canvas
                x, y = self.gesture_recognizer.get_index_finger_position(hand_landmarks, frame.shape)
                # Scale coordinates to canvas size
                canvas_x = int(x * canvas_width / w)
                canvas_y = int(y * canvas_height / h)
                
                # Always update cursor position
                self.cursor_x = canvas_x
                self.cursor_y = canvas_y
                
                # Check if finger is close enough to camera (depth check)
                self.is_close_enough = self.gesture_recognizer.is_finger_close_enough(
                    hand_landmarks, self.depth_threshold)
                
                # Drawing mode - index finger only AND close enough
                if self.gesture_recognizer.is_index_finger_up(hand_landmarks):
                    if self.is_close_enough:
                        self.process_drawing_gesture(canvas_x, canvas_y, canvas_height, canvas_width)
                        drawing = True
                    # If not close enough, just show cursor but don't draw
                elif self.gesture_recognizer.is_all_fingers_up(hand_landmarks):
                    self.canvas.reset_position()
                    self.process_selection_gesture(canvas_x, canvas_y, canvas_height, canvas_width)
                    self.cursor_x = None
                    self.cursor_y = None
                else:
                    self.canvas.reset_position()
        else:
            self.canvas.reset_position()
            self.cursor_x = None
            self.cursor_y = None
        
        # Get canvas
        canvas_display = self.canvas.get_canvas()
        
        # Create display with video overlay
        display = self.create_display_with_video_overlay(canvas_display, video_preview)
        
        # Draw cursor if finger is pointing
        if self.cursor_x is not None and self.cursor_y is not None:
            self.draw_cursor(display, self.cursor_x, self.cursor_y)
        
        # Determine status
        if drawing:
            status = "DRAWING"
        elif self.is_close_enough and results.multi_hand_landmarks:
            status = "READY TO DRAW"
        elif results.multi_hand_landmarks:
            status = "MOVE CLOSER TO DRAW"
        else:
            status = "NO HAND DETECTED"
        
        # Draw UI
        self.ui.draw(display, self.current_color, self.eraser_mode, status, 
                    self.brush_size, self.show_webcam)
        
        return display, drawing
    
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
        
        # Create window and set it to the exact canvas size
        cv2.namedWindow('Fingertip Paint', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Fingertip Paint', self.canvas.width, self.canvas.height)
        
        print("Fingertip Paint App Started!")
        print("Gestures:")
        print("  - Point with index finger CLOSE to camera to draw")
        print("  - Show all fingers (open palm) to select colors/buttons")
        print("\nKeyboard Controls:")
        print("  - '+' or '=' : Increase brush size")
        print("  - '-' or '_' : Decrease brush size")
        print("  - 'v' : Toggle webcam visibility")
        print("  - 's' : Save your drawing")
        print("  - 'c' : Clear canvas")
        print("  - 'q' : Quit")
        
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
                elif key == ord('c'):
                    self.canvas.clear()
                    print("Canvas cleared")
                elif key == ord('v'):
                    self.show_webcam = not self.show_webcam
                    status_msg = "visible" if self.show_webcam else "hidden"
                    print(f"Webcam {status_msg}")
                elif key in [ord('+'), ord('=')]:
                    self.brush_size = min(50, self.brush_size + 1)
                    print(f"Brush size: {self.brush_size}")
                elif key in [ord('-'), ord('_')]:
                    self.brush_size = max(1, self.brush_size - 1)
                    print(f"Brush size: {self.brush_size}")
        
        finally:
            # Cleanup
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            self.gesture_recognizer.close()
