# Fingertip Paint App 🎨✋

A gesture-controlled paint application that lets you draw using your fingertips! Uses your webcam and hand tracking to create digital artwork with natural hand gestures.

## Features

- **Fingertip Drawing**: Point with your index finger to draw
- **Gesture Controls**: Use hand gestures to select colors and control the app
- **8 Color Palette**: Choose from Red, Green, Blue, Yellow, Magenta, Cyan, Black, and White
- **Eraser Tool**: Toggle eraser mode to remove parts of your drawing
- **Clear Canvas**: Start fresh with one gesture
- **Save Functionality**: Save your artwork as PNG images
- **Real-time Hand Tracking**: Powered by MediaPipe for accurate hand detection

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python fingertip_paint.py
```

## Hand Gestures

### Drawing Gesture 🖊️
- **Point with your index finger** (only index finger up, other fingers down)
- Move your finger to draw on the canvas
- The app will draw lines following your fingertip movement

### Selection Gesture 🖐️
- **Show all fingers** (open palm with all 5 fingers extended)
- Use this gesture to:
  - Select colors from the palette at the top
  - Toggle the eraser button
  - Click the clear button to reset the canvas

## Keyboard Shortcuts

- `S` - Save current drawing
- `Q` - Quit application

## How to Use

1. **Launch the app** - Your webcam will activate
2. **Position yourself** - Make sure your hand is visible in the frame
3. **Draw**: 
   - Point with your index finger (like pointing at something)
   - Move your finger around to draw
4. **Change colors**:
   - Open your palm (show all 5 fingers)
   - Move your hand over a color in the palette at the top
5. **Use eraser**:
   - Open your palm
   - Move over the "ERASE" button
6. **Clear canvas**:
   - Open your palm
   - Move over the "CLEAR" button
7. **Save your art**:
   - Press 'S' on your keyboard

## Tips for Best Results

- 🔆 Ensure good lighting for better hand detection
- 🖐️ Keep your hand clearly visible in the camera frame
- 📏 Maintain a moderate distance from the camera (arm's length works well)
- 🎨 Practice the gestures - it becomes natural quickly!
- 🔄 If tracking is lost, simply reposition your hand in view

## Requirements

- Python 3.7+
- OpenCV
- NumPy
- MediaPipe
- Webcam

## Troubleshooting

**Hand not detected?**
- Check lighting conditions
- Ensure your hand is fully visible in the frame
- Try adjusting your distance from the camera

**Drawing not smooth?**
- Ensure stable hand movements
- Check that only your index finger is up when drawing
- Improve lighting conditions

Have fun creating digital art with your hands! 🎨✨
