# src/utils/exceptions.py

class TextractorError(Exception):
    """Base exception for Textractor"""

class ImageLoadError(TextractorError):
    """Raised when an image fails to load"""

class TextureExtractionError(TextractorError):
    """Raised when texture extraction fails"""