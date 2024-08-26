# tests/test_ui_manager.py

import unittest
from unittest.mock import Mock, patch
import tkinter as tk
from src.ui.ui_manager import UIManager
from src.config.settings import UI_TEXTS

class TestUIManager(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.controller = Mock()
        self.controller.recent_files = []
        self.ui_manager = UIManager(self.root, self.controller)

    def tearDown(self):
        self.root.destroy()

    def test_initialization(self):
        self.assertIsInstance(self.ui_manager.master, tk.Tk)
        self.assertEqual(self.ui_manager.master.title(), UI_TEXTS["app_title"])

    def test_validate_float_input(self):
        self.assertTrue(self.ui_manager.validate_float_input("1.5"))
        self.assertTrue(self.ui_manager.validate_float_input("2"))
        self.assertFalse(self.ui_manager.validate_float_input("abc"))

    def test_update_aspect_ratio_estimated(self):
        self.ui_manager.update_aspect_ratio("Estimated")
        self.assertEqual(self.ui_manager.custom_aspect_entry.cget('state'), 'disabled')
        self.controller.estimate_aspect_ratio.assert_called_once()

    def test_update_aspect_ratio_square(self):
        self.ui_manager.update_aspect_ratio("Square")
        self.assertEqual(self.ui_manager.custom_aspect_entry.cget('state'), 'disabled')
        self.assertEqual(self.controller.aspect_ratio, 1.0)
        self.controller.extract_texture.assert_called_once()

    def test_update_aspect_ratio_custom(self):
        self.ui_manager.update_aspect_ratio("Custom")
        self.assertEqual(self.ui_manager.custom_aspect_entry.cget('state'), 'normal')

    @patch('tkinter.messagebox.showerror')
    def test_commit_custom_aspect_ratio_invalid(self, mock_showerror):
        self.ui_manager.custom_aspect_entry.configure(state='normal')
        self.ui_manager.custom_aspect_entry.delete(0, tk.END)
        self.ui_manager.custom_aspect_entry.insert(0, "invalid")
        self.ui_manager.commit_custom_aspect_ratio()
        mock_showerror.assert_called_once_with("Invalid Input", UI_TEXTS["custom_aspect_error"])

    def test_commit_custom_aspect_ratio_valid(self):
        self.ui_manager.custom_aspect_entry.configure(state='normal')
        self.ui_manager.custom_aspect_entry.delete(0, tk.END)
        self.ui_manager.custom_aspect_entry.insert(0, "1.5")
        self.ui_manager.commit_custom_aspect_ratio()
        self.assertEqual(self.controller.aspect_ratio, 1.5)
        self.controller.extract_texture.assert_called_once()

    def test_auto_complete_decimal(self):
        self.ui_manager.custom_aspect_entry.configure(state='normal')
        self.ui_manager.custom_aspect_entry.delete(0, tk.END)
        self.ui_manager.custom_aspect_entry.insert(0, ".")
        self.ui_manager.auto_complete_decimal(None)  # Simulate event
        self.assertEqual(self.ui_manager.custom_aspect_entry.get(), "0.")

    def test_update_estimated_aspect_ratio(self):
        self.ui_manager.update_estimated_aspect_ratio(1.5)
        expected_text = UI_TEXTS["estimated_aspect_label"].format(1.5)
        self.assertEqual(self.ui_manager.estimated_aspect_label.cget('text'), expected_text)

    @patch('tkinter.filedialog.asksaveasfilename')
    def test_get_save_file_path(self, mock_asksaveasfilename):
        expected_path = "/path/to/save/file.png"
        mock_asksaveasfilename.return_value = expected_path
        result = self.ui_manager.get_save_file_path()
        self.assertEqual(result, expected_path)

    @patch('tkinter.filedialog.askopenfilename')
    def test_get_open_file_path(self, mock_askopenfilename):
        expected_path = "/path/to/open/file.png"
        mock_askopenfilename.return_value = expected_path
        result = self.ui_manager.get_open_file_path()
        self.assertEqual(result, expected_path)

    @patch('tkinter.messagebox.showerror')
    def test_show_error(self, mock_showerror):
        self.ui_manager.show_error("Error Title", "Error Message")
        mock_showerror.assert_called_once_with("Error Title", "Error Message")

    @patch('tkinter.messagebox.showinfo')
    def test_show_info(self, mock_showinfo):
        self.ui_manager.show_info("Info Title", "Info Message")
        mock_showinfo.assert_called_once_with("Info Title", "Info Message")

    @patch('tkinter.messagebox.askokcancel')
    def test_ask_quit(self, mock_askokcancel):
        mock_askokcancel.return_value = True
        result = self.ui_manager.ask_quit()
        self.assertTrue(result)
        mock_askokcancel.assert_called_once_with("Quit", "Do you want to quit?")

    def test_update_status(self):
        test_message = "Test status message"
        self.ui_manager.update_status(test_message)
        self.assertEqual(self.ui_manager.status_bar.cget('text'), test_message)

if __name__ == '__main__':
    unittest.main()