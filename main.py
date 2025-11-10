"""
Fingertip Paint Application
A gesture-controlled paint app using webcam and hand tracking.
"""
from src.paint_app import PaintApp


def main():
    """Main entry point for the application."""
    app = PaintApp()
    app.run()


if __name__ == '__main__':
    main()
