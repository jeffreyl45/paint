"""
Hand gesture recognition module for fingertip paint application.
"""
import mediapipe as mp


class GestureRecognizer:
    """Recognizes hand gestures using MediaPipe."""
    
    def __init__(self, min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=1):
        """
        Initialize the gesture recognizer.
        
        Args:
            min_detection_confidence: Minimum confidence for hand detection
            min_tracking_confidence: Minimum confidence for hand tracking
            max_num_hands: Maximum number of hands to detect
        """
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            max_num_hands=max_num_hands
        )
        self.mp_draw = mp.solutions.drawing_utils
    
    def process_frame(self, rgb_frame):
        """
        Process a frame to detect hands.
        
        Args:
            rgb_frame: Frame in RGB format
            
        Returns:
            MediaPipe results object
        """
        return self.hands.process(rgb_frame)
    
    def is_index_finger_up(self, hand_landmarks):
        """
        Check if only index finger is up (drawing gesture).
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            bool: True if only index finger is up
        """
        landmarks = hand_landmarks.landmark
        
        # Index finger tip and pip
        index_tip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        index_pip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_PIP]
        
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
        """
        Check if all fingers are up (selection gesture).
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            bool: True if at least 4 fingers are up
        """
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
    
    def get_index_finger_position(self, hand_landmarks, frame_shape):
        """
        Get the pixel coordinates of the index finger tip.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            frame_shape: Shape of the frame (h, w, c)
            
        Returns:
            tuple: (x, y) coordinates
        """
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        h, w, _ = frame_shape
        x = int(index_tip.x * w)
        y = int(index_tip.y * h)
        return x, y
    
    def draw_landmarks(self, frame, hand_landmarks):
        """
        Draw hand landmarks on the frame.
        
        Args:
            frame: Frame to draw on
            hand_landmarks: MediaPipe hand landmarks
        """
        self.mp_draw.draw_landmarks(
            frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
    
    def close(self):
        """Release resources."""
        self.hands.close()
