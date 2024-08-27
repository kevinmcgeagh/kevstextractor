# src/config/settings.py

import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# File paths
RECENT_FILES_PATH = BASE_DIR / "recent_files.json"
LOG_FILE = BASE_DIR / "kevstextractor.log"
BANNER_PATH = BASE_DIR / "resources" / "images" / "textractor_banner.png"

# Application settings
APP_NAME = "Kev's Textractor"
VERSION = "1.0"
COMPANY_NAME = "Kevin McGeagh"

# UI settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600

# Color scheme
BACKGROUND_COLOR = "#2E2E2E"
FOREGROUND_COLOR = "#FFFFFF"
ACCENT_COLOR = "#4A90E2"

# Texture extraction settings
MAX_TEXTURE_SIZE = 2048  # Maximum size of extracted texture

# Launch popup settings
SHOW_LAUNCH_POPUP = True
LICENSE_WARNING = "This software is licensed under the Apache License 2.0. See the LICENSE file for more information."

# About text
ABOUT_TEXT = f"""
{APP_NAME} v{VERSION}
© 2024 {COMPANY_NAME}

This software is licensed under the Apache License 2.0 License.
For more information, visit: https://www.apache.org/licenses/LICENSE-2.0
"""

# Recent files settings
MAX_RECENT_FILES = 5

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Default aspect ratio
DEFAULT_ASPECT_RATIO = 1.0

# Image processing settings
PREVIEW_MAX_SIZE = 500  # Maximum size of preview image (width or height)

# File type settings
SUPPORTED_IMAGE_TYPES = [
    ("PNG files", "*.png"),
    ("JPEG files", "*.jpg;*.jpeg"),
    ("TIFF files", "*.tif;*.tiff"),
    ("BMP files", "*.bmp"),
    ("All files", "*.*")
]

# Keyboard shortcuts
SHORTCUTS = {
    "open": "<Control-o>",
    "save": "<Control-s>",
    "undo": "<Control-z>",
    "redo": "<Control-y>",
    "quit": "<Control-q>"
}

# UI text strings
UI_TEXTS = {
    "app_title": APP_NAME,
    "load_button": "Load Image",
    "clear_button": "Clear Selection",
    "save_button": "Save Texture",
    "flip_checkbox": "Flip Vertically",
    "flop_checkbox": "Flop Horizontally",
    "rotate_checkbox": "Rotate 90° Clockwise",
    "aspect_ratio_label": "Aspect Ratio:",
    "estimated_aspect_label": "Estimated Aspect Ratio: {:.2f}",
    "custom_aspect_error": "Please enter a valid aspect ratio between 0.1 and 10.0."
}

# Status messages
STATUS_MESSAGES = {
    "ready": "Ready",
    "loading_image": "Loading image: {}",
    "image_loaded": "Image loaded successfully",
    "load_failed": "Failed to load image",
    "extracting_texture": "Extracting texture...",
    "extraction_success": "Texture extracted successfully",
    "extraction_failed": "Failed to extract texture",
    "saving_texture": "Saving texture: {}",
    "save_success": "Texture saved successfully",
    "save_failed": "Failed to save texture",
    "selection_cleared": "Selection cleared",
    "undo_performed": "Undo performed",
    "redo_performed": "Redo performed"
}