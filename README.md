# Textractor

Kev's Textractor is a powerful and user-friendly application designed to extract textures from images. Whether you're a game developer, graphic designer, or digital artist, Textractor provides an intuitive interface for selecting, adjusting, and extracting textures from any image.

![Textractor Screenshot](path/to/screenshot.png)

## Features

- Intuitive point-and-click interface for selecting texture areas
- Real-time preview of extracted textures
- Multiple aspect ratio modes: Estimated, Square, and Custom
- Image transformation options: Flip, Flop, and Rotate
- Undo/Redo support
- Recent files tracking
- Cross-platform compatibility (Windows, macOS, Linux)

## Installation

1. Ensure you have Python 3.7 or later installed on your system.
2. Clone this repository:
   ```
   git clone https://github.com/kevinmcgeagh/kevstextractor.git
   ```
3. Navigate to the Textractor directory:
   ```
   cd textractor
   ```
4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python run.py
   ```
2. Click "Load Image" or use Ctrl+O to open an image.
3. Click on four points in the image to select your texture area.
4. Adjust aspect ratio and apply transformations as needed.
5. Click "Save Texture" or use Ctrl+S to save the extracted texture.

For more detailed instructions, please refer to the [User Guide](docs/user_guide.md).

## Dependencies

- OpenCV
- NumPy
- Pillow
- tkinter (usually comes with Python)

For a complete list of dependencies, see `requirements.txt`.

## License

Distributed under the Apache License 2.0. See `LICENSE` file for more information.

Project Link: [https://github.com/yourusername/textractor](https://github.com/yourusername/textractor)

## Acknowledgments

- [OpenCV](https://opencv.org/)
- [NumPy](https://numpy.org/)
- [Pillow](https://python-pillow.org/)
- [All other acknowledgments]