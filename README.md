# Fingertip Paint App 🎨✋

A gesture-controlled paint application that lets you draw using your fingertips! Uses your webcam and hand tracking to create digital artwork with natural hand gestures.

## Features

- **Fingertip Drawing**: Point with your index finger to draw on a clean white canvas
- **Gesture Controls**: Use hand gestures to select colors and control the app
- **8 Color Palette**: Choose from Red, Green, Blue, Yellow, Magenta, Cyan, Black, and White
- **Eraser Tool**: Toggle eraser mode to remove parts of your drawing
- **Clear Canvas**: Clear all drawings with one gesture or keyboard shortcut
- **Adjustable Brush Size**: Fine-tune brush size (1-50px) for precise control
- **Smooth Drawing**: Advanced smoothing algorithm for better line quality
- **Save Functionality**: Save your artwork as PNG images
- **Real-time Hand Tracking**: Powered by MediaPipe for accurate hand detection
- **Modular Architecture**: Clean, maintainable code structure
- **Video Preview**: Small webcam overlay to see your hand movements

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

Or use the standalone version:
```bash
python fingertip_paint.py
```

## Project Structure

```
paint/
├── main.py                          # Entry point for modular version
├── fingertip_paint.py              # Standalone single-file version
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── src/                            # Modular source code
    ├── __init__.py                # Package initialization
    ├── paint_app.py               # Main application controller
    ├── gesture_recognizer.py      # Hand gesture recognition
    ├── canvas.py                  # Drawing canvas management
    └── ui.py                      # UI rendering components
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

- `+` or `=` - Increase brush size
- `-` or `_` - Decrease brush size
- `V` - Toggle webcam visibility (hide/show)
- `C` - Clear canvas (Clear All)
- `S` - Save current drawing
- `Q` - Quit application

## How to Use

1. **Launch the app** - Your webcam will activate
2. **Position yourself** - Make sure your hand is visible to the camera
3. **Draw**: 
   - Point with your index finger (like pointing at something)
   - Move your finger around to draw on the white canvas
   - The app uses smoothing to make your lines cleaner
4. **Toggle webcam**:
   - Press `V` to hide/show the webcam preview
   - The webcam is hidden by default for a cleaner canvas
   - You can still draw with it hidden!
5. **Adjust brush size**:
   - Press `+` to make the brush larger
   - Press `-` to make the brush smaller
   - Perfect for drawing fine details or bold strokes!
6. **Change colors**:
   - Open your palm (show all 5 fingers)
   - Move your hand over a color in the palette at the top
7. **Use eraser**:
   - Open your palm
   - Move over the "ERASE" button
8. **Clear everything**:
   - Open your palm and move over "CLEAR" button, OR
   - Press 'C' on your keyboard
9. **Save your art**:
   - Press 'S' on your keyboard

## Tips for Best Results

- 🔆 Ensure good lighting for better hand detection
- 🖐️ Keep your hand clearly visible in the camera view
- 📏 Maintain a moderate distance from the camera (arm's length works well)
- 🎨 Practice the gestures - it becomes natural quickly!
- 🔄 If tracking is lost, simply reposition your hand in view
- ✏️ Use smaller brush sizes (1-3px) for fine details like dots
- 🖌️ Use larger brush sizes (10-20px) for bold strokes
- 🤚 Hold your drawing gesture steady for smoother lines
- 📺 Press 'V' to hide the webcam for a cleaner, distraction-free canvas
- 🎯 The entire white area is your canvas - draw anywhere!

## Architecture

The application is built with a modular architecture:

### Components

1. **GestureRecognizer** (`gesture_recognizer.py`)
   - Hand detection using MediaPipe
   - Gesture recognition (drawing vs selection)
   - Finger position tracking

2. **Canvas** (`canvas.py`)
   - Drawing surface management
   - Line rendering
   - Save/clear operations

3. **UI** (`ui.py`)
   - Color palette rendering
   - Button controls
   - Status display
   - User interaction detection

4. **PaintApp** (`paint_app.py`)
   - Main application controller
   - Coordinates all components
   - Frame processing pipeline
   - Event handling

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
