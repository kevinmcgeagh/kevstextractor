# tests/test_image_processor.py

import unittest
import numpy as np
from src.core.image_processor import ImageProcessor


class TestImageProcessor(unittest.TestCase):
    def setUp(self):
        self.image_processor = ImageProcessor()

    def test_scale_image(self):
        # Create a simple 100x100 image
        image = np.zeros((100, 100, 3), dtype=np.uint8)

        # Test scaling down
        scaled_image, scale_factor = self.image_processor.scale_image(image, 50, 50)
        self.assertEqual(scaled_image.shape, (50, 50, 3))
        self.assertAlmostEqual(scale_factor, 0.5)

        # Test scaling up
        scaled_image, scale_factor = self.image_processor.scale_image(image, 200, 200)
        self.assertEqual(scaled_image.shape, (200, 200, 3))
        self.assertAlmostEqual(scale_factor, 2.0)

    def test_extract_texture(self):
        # Create a simple 100x100 image
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        image[25:75, 25:75] = 255  # White square in the middle

        # Define points for a 50x50 square in the middle
        points = np.array([(25, 25), (75, 25), (75, 75), (25, 75)], dtype=np.float32)

        extracted = self.image_processor.extract_texture(image, points, 50, 50)

        self.assertEqual(extracted.shape, (50, 50, 3))

        # Print diagnostics
        print(f"Extracted shape: {extracted.shape}")
        print(f"Min value: {np.min(extracted)}")
        print(f"Max value: {np.max(extracted)}")
        print(f"Mean value: {np.mean(extracted)}")
        print(f"Unique values: {np.unique(extracted)}")
        print(f"Percentage of 255: {np.sum(extracted == 255) / extracted.size * 100:.2f}%")

        # Print a small sample of the extracted texture
        print("Sample of extracted texture (top-left 5x5 corner):")
        print(extracted[:5, :5, 0])  # Assuming all channels are the same, we'll just print one

        # Check if all pixels are close to white (255), allowing for small differences
        almost_white = np.sum(np.abs(extracted - 255) <= 2) / extracted.size
        self.assertGreaterEqual(almost_white, 0.95,
                                f"Only {almost_white:.2%} of pixels are close to white (within 2 units), expected at least 95%")

        # Check if at least 90% of the pixels are exactly white
        white_percentage = np.sum(extracted == 255) / extracted.size
        self.assertGreaterEqual(white_percentage, 0.90,
                                f"Only {white_percentage:.2%} of pixels are exactly white, expected at least 90%")


if __name__ == '__main__':
    unittest.main()