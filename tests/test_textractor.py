# tests/test_textractor.py

import unittest
from unittest.mock import Mock, patch
import tkinter as tk
import numpy as np
from src.core.textractor import Textractor


class TestTextractor(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        with patch('src.core.textractor.UIManager'), \
                patch('src.core.textractor.ImageProcessor'), \
                patch('src.core.textractor.load_recent_files'):
            self.textractor = Textractor(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_initialization(self):
        self.assertIsInstance(self.textractor.ui, Mock)
        self.assertIsInstance(self.textractor.image_processor, Mock)
        self.assertEqual(self.textractor.zoom_factor, 1.0)

    @patch('tkinter.filedialog.askopenfilename')
    @patch('cv2.imread')
    def test_load_image(self, mock_imread, mock_askopenfilename):
        mock_askopenfilename.return_value = "test_image.jpg"
        mock_imread.return_value = np.zeros((100, 100, 3), dtype=np.uint8)

        self.textractor.load_image()

        mock_askopenfilename.assert_called_once()
        mock_imread.assert_called_once_with("test_image.jpg", -1)
        self.assertIsNotNone(self.textractor.image)

    def test_clear_selection(self):
        self.textractor.points = [(0, 0), (1, 1)]
        self.textractor.original_points = [(0, 0), (1, 1)]

        self.textractor.clear_selection()

        self.assertEqual(self.textractor.points, [])
        self.assertEqual(self.textractor.original_points, [])

    def test_estimate_aspect_ratio(self):
        self.textractor.points = [(0, 0), (1, 0), (1, 1), (0, 1)]
        self.textractor.estimate_aspect_ratio()
        self.assertEqual(self.textractor.aspect_ratio, 1.0)


if __name__ == '__main__':
    unittest.main()