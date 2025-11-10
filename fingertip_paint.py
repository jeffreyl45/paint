import cv2
import numpy as np
import mediapipe as mp

class FingertipPaintApp:
    def __init__(self):
        # Initialize MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            max_num_hands=1
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Canvas setup
        self.canvas = np.ones((480, 640, 3), dtype=np.uint8) * 255
        self.current_color = (0, 0, 255)  # Red in BGR
        self.brush_size = 5
        self.prev_x, self.prev_y = None, None
        self.drawing_mode = True
        
        # Color palette
        self.colors = [
            ((0, 0, 255), "Red"),
            ((0, 255, 0), "Green"),
            ((255, 0, 0), "Blue"),
            ((0, 255, 255), "Yellow"),
            ((255, 0, 255), "Magenta"),
            ((255, 255, 0), "Cyan"),
            ((0, 0, 0), "Black"),
            ((255, 255, 255), "White"),
        ]
        
        # UI setup
        self.palette_height = 80
        self.eraser_mode = False
        
    def draw_ui(self, frame):
        """Draw UI elements on frame"""
        # Draw color palette
        color_box_width = frame.shape[1] // len(self.colors)
        for i, (color, name) in enumerate(self.colors):
            x1 = i * color_box_width
            x2 = (i + 1) * color_box_width
            cv2.rectangle(frame, (x1, 0), (x2, self.palette_height), color, -1)
            
            # Highlight selected color
            if color == self.current_color and not self.eraser_mode:
                cv2.rectangle(frame, (x1, 0), (x2, self.palette_height), (0, 255, 0), 5)
            
            # Add text
            cv2.putText(frame, name[:3], (x1 + 5, 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Draw clear button
        clear_x1 = frame.shape[1] - 100
        clear_y1 = 10
        clear_x2 = frame.shape[1] - 10
        clear_y2 = 70
        cv2.rectangle(frame, (clear_x1, clear_y1), (clear_x2, clear_y2), (200, 200, 200), -1)
        cv2.putText(frame, "CLEAR", (clear_x1 + 5, clear_y1 + 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        # Draw eraser button
        eraser_x1 = frame.shape[1] - 210
        eraser_y1 = 10
        eraser_x2 = frame.shape[1] - 110
        eraser_y2 = 70
        eraser_color = (100, 255, 100) if self.eraser_mode else (200, 200, 200)
        cv2.rectangle(frame, (eraser_x1, eraser_y1), (eraser_x2, eraser_y2), eraser_color, -1)
        cv2.putText(frame, "ERASE", (eraser_x1 + 5, eraser_y1 + 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        # Instructions
        instructions = [
            "Point index finger straight to draw",
            "Show palm (5 fingers) to select color/button",
            "Press 's' to save | 'q' to quit"
        ]
        y_offset = frame.shape[0] - 80
        for i, text in enumerate(instructions):
            cv2.putText(frame, text, (10, y_offset + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def is_index_finger_up(self, hand_landmarks):
        """Check if only index finger is up (drawing gesture)"""
        # Get landmarks
        landmarks = hand_landmarks.landmark
        
        # Index finger tip and pip
        index_tip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        index_pip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_PIP]
        
        # Thumb
        thumb_tip = landmarks[self.mp_hands.HandLandmark.THUMB_TIP]
        thumb_ip = landmarks[self.mp_hands.HandLandmark.THUMB_IP]
        
        # Middle finger
        middle_tip = landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        middle_pip = landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
        
        # Ring finger
        ring_tip = landmarks[self.mp_hands.HandLandmark.RING_FINGER_TIP]
        ring_pip = landmarks[self.mp_hands.HandLandmark.RING_FINGER_PIP]
        
        # Pinky
        pinky_tip = landmarks[self.mp_hands.HandLandmark.PINKY_TIP]
        pinky_pip = landmarks[self.mp_hands.HandLandmark.PINKY_PIP]
        
        # Check if index finger is up and others are down
        index_up = index_tip.y < index_pip.y
        middle_down = middle_tip.y > middle_pip.y
        ring_down = ring_tip.y > ring_pip.y
        pinky_down = pinky_tip.y > pinky_pip.y
        
        return index_up and middle_down and ring_down and pinky_down
    
    def is_all_fingers_up(self, hand_landmarks):
        """Check if all fingers are up (selection gesture)"""
        landmarks = hand_landmarks.landmark
        
        fingers_up = 0
        
        # Check each finger
        finger_tips = [
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mp_hands.HandLandmark.RING_FINGER_TIP,
            self.mp_hands.HandLandmark.PINKY_TIP
        ]
        
        finger_pips = [
            self.mp_hands.HandLandmark.INDEX_FINGER_PIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
            self.mp_hands.HandLandmark.RING_FINGER_PIP,
            self.mp_hands.HandLandmark.PINKY_PIP
        ]
        
        for tip, pip in zip(finger_tips, finger_pips):
            if landmarks[tip].y < landmarks[pip].y:
                fingers_up += 1
        
        return fingers_up >= 4
    
    def process_hand(self, hand_landmarks, frame_shape):
        """Process hand landmarks and perform actions"""
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        
        # Convert normalized coordinates to pixel coordinates
        h, w, _ = frame_shape
        x = int(index_tip.x * w)
        y = int(index_tip.y * h)
        
        # Drawing mode - index finger only
        if self.is_index_finger_up(hand_landmarks):
            if y > self.palette_height:  # Below UI area
                if self.prev_x is not None and self.prev_y is not None:
                    color = (255, 255, 255) if self.eraser_mode else self.current_color
                    thickness = self.brush_size * 3 if self.eraser_mode else self.brush_size
                    cv2.line(self.canvas, (self.prev_x, self.prev_y), (x, y), color, thickness)
                self.prev_x, self.prev_y = x, y
            return True
        
        # Selection mode - all fingers up
        elif self.is_all_fingers_up(hand_landmarks):
            self.prev_x, self.prev_y = None, None
            
            # Check if selecting color
            if y < self.palette_height:
                color_box_width = w // len(self.colors)
                color_index = x // color_box_width
                if 0 <= color_index < len(self.colors):
                    self.current_color = self.colors[color_index][0]
                    self.eraser_mode = False
            
            # Check if clicking eraser button
            elif w - 210 < x < w - 110 and 10 < y < 70:
                self.eraser_mode = not self.eraser_mode
            
            # Check if clicking clear button
            elif w - 100 < x < w - 10 and 10 < y < 70:
                self.canvas = np.ones((h, w, 3), dtype=np.uint8) * 255
            
            return False
        
        else:
            self.prev_x, self.prev_y = None, None
            return False
    
    def run(self):
        """Main loop"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("Fingertip Paint App Started!")
        print("Gestures:")
        print("  - Point with index finger to draw")
        print("  - Show all fingers (open palm) to select colors/buttons")
        print("  - Press 'S' to save your drawing")
        print("  - Press 'Q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            # Resize canvas to match frame if needed
            if self.canvas.shape[:2] != (h, w):
                self.canvas = cv2.resize(self.canvas, (w, h))
            
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            # Process hand landmarks
            drawing = False
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks on frame
                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Process hand gestures
                    drawing = self.process_hand(hand_landmarks, frame.shape)
            else:
                self.prev_x, self.prev_y = None, None
            
            # Combine frame and canvas
            # Make frame semi-transparent where there's drawing
            frame_with_ui = self.draw_ui(frame.copy())
            
            # Blend canvas with frame
            mask = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
            mask = cv2.threshold(mask, 250, 255, cv2.THRESH_BINARY_INV)[1]
            mask_3channel = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            
            # Apply canvas drawings on top of frame
            frame_with_canvas = frame_with_ui.copy()
            frame_with_canvas = np.where(mask_3channel > 0, self.canvas, frame_with_canvas)
            
            # Show status
            status = "DRAWING" if drawing else "SELECTION MODE" if results.multi_hand_landmarks else "NO HAND DETECTED"
            cv2.putText(frame_with_canvas, status, (10, h - 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('Fingertip Paint', frame_with_canvas)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f'fingertip_painting_{cv2.getTickCount()}.png'
                cv2.imwrite(filename, self.canvas)
                print(f'Drawing saved as {filename}')
        
        cap.release()
        cv2.destroyAllWindows()
        self.hands.close()


if __name__ == '__main__':
    app = FingertipPaintApp()
    app.run()