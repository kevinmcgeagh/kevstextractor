# src/core/textractor.py

import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import threading
import queue
import logging
import os
from typing import List, Tuple, Optional

from src.ui.ui_manager import UIManager
from src.core.image_processor import ImageProcessor
from src.utils.file_utils import load_recent_files, save_recent_files
from src.utils.exceptions import ImageLoadError, TextureExtractionError
from src.config.settings import LICENSE_WARNING, BANNER_PATH

logger = logging.getLogger(__name__)


class Textractor:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.recent_files: List[str] = load_recent_files()

        self.image_processor = ImageProcessor()
        self.ui = UIManager(master, self)

        self.points: List[Tuple[float, float]] = []
        self.original_points: List[Tuple[float, float]] = []
        self.image: Optional[np.ndarray] = None
        self.original_image_size: Optional[Tuple[int, int]] = None
        self.image_scale_factor: float = 1.0
        self.dragging_index: Optional[int] = None
        self.aspect_ratio: float = 1.0

        self.undo_stack: List[dict] = []
        self.redo_stack: List[dict] = []

        self.queue: queue.Queue = queue.Queue()
        self.thread: Optional[threading.Thread] = None

        # Zoom and pan variables
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.zoom_factor = 1.0

        self.setup_ui_commands()
        self.setup_keyboard_shortcuts()
        self.ui.setup_bindings(
            self.on_press,
            self.on_release,
            self.on_drag,
            self.on_move,
            self.on_resize,
            self.on_closing
        )

        # Show the launch pop-up
        self.show_launch_popup()

    def show_launch_popup(self):
        popup = tk.Toplevel(self.master)
        popup.title("Welcome to Textractor")
        popup.geometry("400x300")
        popup.resizable(False, False)

        # Try to load the banner image
        try:
            banner_image = Image.open(BANNER_PATH)
            banner_photo = ImageTk.PhotoImage(banner_image)
            banner_label = tk.Label(popup, image=banner_photo)
            banner_label.image = banner_photo  # Keep a reference
            banner_label.pack(pady=10)
        except FileNotFoundError:
            # Fallback to text if image is not found
            banner_text = tk.Label(popup, text="Welcome to Textractor", font=("Helvetica", 16, "bold"))
            banner_text.pack(pady=20)

        # License warning
        warning_label = tk.Label(popup, text=LICENSE_WARNING, wraplength=380, justify="center")
        warning_label.pack(pady=10)

        # OK button to close the popup
        ok_button = tk.Button(popup, text="OK", command=popup.destroy)
        ok_button.pack(pady=10)

        # Center the popup on the screen
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        # Make the popup modal
        popup.transient(self.master)
        popup.grab_set()
        self.master.wait_window(popup)

    def setup_ui_commands(self) -> None:
        self.ui.load_button.config(command=self.load_image)
        self.ui.clear_button.config(command=self.clear_selection)
        self.ui.save_button.config(command=self.save_texture)
        self.ui.flip_check.config(command=self.update_preview)
        self.ui.flop_check.config(command=self.update_preview)
        self.ui.rotate_check.config(command=self.update_preview)

    def setup_keyboard_shortcuts(self) -> None:
        self.ui.master.bind("<Control-z>", self.undo)
        self.ui.master.bind("<Control-y>", self.redo)
        self.ui.master.bind("<Control-o>", lambda e: self.load_image())
        self.ui.master.bind("<Control-s>", lambda e: self.save_texture())

    def load_image(self, file_path: Optional[str] = None) -> None:
        if file_path is None:
            file_path = filedialog.askopenfilename(filetypes=[
                ("Image files", "*.png;*.jpg;*.jpeg;*.tif;*.tiff;*.bmp"),
                ("All files", "*.*")
            ])
        if file_path:
            try:
                self.ui.update_status(f"Loading image: {file_path}")
                self.image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
                if self.image is None:
                    raise ImageLoadError("Failed to load image")
                self.display_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                self.original_image_size = self.display_image.shape[:2][::-1]  # (width, height)
                self.scale_image()
                self.draw_image()
                self.clear_selection()
                self.add_to_undo_stack()
                self.add_recent_file(file_path)
                logger.info(f"Loaded image: {file_path}")
                self.ui.update_status("Image loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load image: {str(e)}")
                self.ui.show_error("Error", f"Failed to load image: {str(e)}")
                self.ui.update_status("Failed to load image")

    def scale_image(self) -> None:
        if self.image is None:
            return
        canvas_width = self.ui.canvas.winfo_width()
        canvas_height = self.ui.canvas.winfo_height()
        self.scaled_display_image, self.image_scale_factor = self.image_processor.scale_image(
            self.display_image, canvas_width, canvas_height)
        self.scale_points()

    def scale_points(self) -> None:
        if self.original_image_size and self.original_points:
            orig_width, orig_height = self.original_image_size
            new_width, new_height = self.scaled_display_image.shape[1], self.scaled_display_image.shape[0]
            scale_x = new_width / orig_width
            scale_y = new_height / orig_height
            self.points = [(x * scale_x, y * scale_y) for x, y in self.original_points]

    def draw_image(self) -> None:
        if self.scaled_display_image is None:
            return
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.scaled_display_image))
        self.ui.canvas.delete("image")
        self.ui.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo, tags="image")
        self.ui.update_status(f"Zoom: {self.zoom_factor:.2f}x")

    def on_press(self, event) -> None:
        if self.image is None:
            return

        # Convert event coordinates to canvas coordinates
        x = self.ui.canvas.canvasx(event.x)
        y = self.ui.canvas.canvasy(event.y)

        if len(self.points) < 4:
            if not self.is_point_too_close(x, y):
                canvas_x = x / (self.image_scale_factor * self.zoom_factor)
                canvas_y = y / (self.image_scale_factor * self.zoom_factor)
                self.original_points.append((canvas_x, canvas_y))
                self.points.append((x, y))
                self.draw_polygon()
                if len(self.points) == 4:
                    self.apply_aspect_ratio_mode()
                    self.extract_texture()
                self.add_to_undo_stack()
        else:
            self.dragging_index = self.get_closest_point_index(x, y)

    def on_release(self, event) -> None:
        if self.dragging_index is not None:
            self.dragging_index = None
            self.apply_aspect_ratio_mode()
            self.extract_texture()
            self.add_to_undo_stack()

    def on_drag(self, event) -> None:
        if self.dragging_index is not None:
            # Convert event coordinates to canvas coordinates
            x = self.ui.canvas.canvasx(event.x)
            y = self.ui.canvas.canvasy(event.y)

            if not self.is_point_too_close(x, y, exclude=self.dragging_index):
                canvas_x = x / (self.image_scale_factor * self.zoom_factor)
                canvas_y = y / (self.image_scale_factor * self.zoom_factor)
                self.original_points[self.dragging_index] = (canvas_x, canvas_y)
                self.points[self.dragging_index] = (x, y)
                self.draw_polygon()
                self.apply_aspect_ratio_mode()
                self.extract_texture()

    def on_move(self, event) -> None:
        self.ui.canvas.delete("temp_line")
        if len(self.points) > 0 and len(self.points) < 4:
            # Convert event coordinates to canvas coordinates
            x = self.ui.canvas.canvasx(event.x)
            y = self.ui.canvas.canvasy(event.y)
            self.ui.canvas.create_line(self.points[-1], (x, y), fill="yellow", width=2, tags="temp_line")

    def on_resize(self, event) -> None:
        if self.image is not None:
            self.scale_image()
            self.draw_image()
            self.draw_polygon()
        self.update_preview()

    def on_closing(self) -> None:
        if self.ui.ask_quit():
            self.ui.master.quit()

    def start_pan(self, event):
        self.ui.canvas.config(cursor="fleur")
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def pan(self, event):
        if self.image is None:
            return
        self.ui.canvas.config(cursor="fleur")
        dx = event.x - self.pan_start_x
        dy = event.y - self.pan_start_y
        self.ui.canvas.move("all", dx, dy)
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def zoom(self, event):
        if self.image is None:
            return
        x = self.ui.canvas.canvasx(event.x)
        y = self.ui.canvas.canvasy(event.y)
        factor = 1.1 if event.delta > 0 else 0.9
        self.zoom_factor *= factor
        self.ui.canvas.scale("all", x, y, factor, factor)
        self.draw_image()
        self.draw_polygon()

    def is_point_too_close(self, x: float, y: float, exclude: Optional[int] = None) -> bool:
        min_distance = 20 / self.zoom_factor
        for i, point in enumerate(self.points):
            if i != exclude and ((point[0] - x) ** 2 + (point[1] - y) ** 2) < min_distance ** 2:
                return True
        return False

    def get_closest_point_index(self, x: float, y: float) -> Optional[int]:
        if not self.points:
            return None
        distances = [(i, (p[0] - x) ** 2 + (p[1] - y) ** 2) for i, p in enumerate(self.points)]
        closest_index, distance = min(distances, key=lambda x: x[1])
        return closest_index if distance < (100 / self.zoom_factor ** 2) else None

    def draw_polygon(self) -> None:
        self.ui.canvas.delete("polygon", "points")
        if len(self.points) > 1:
            self.ui.canvas.create_polygon(self.points, outline="cyan", fill="", width=2, tags="polygon")
        for i, point in enumerate(self.points):
            self.ui.canvas.create_oval(point[0] - 3, point[1] - 3, point[0] + 3, point[1] + 3, fill="red",
                                       outline="white", tags="points")
            self.ui.canvas.create_text(point[0] + 10, point[1] + 10, text=str(i + 1), fill="white", tags="points")

    def clear_selection(self) -> None:
        self.points = []
        self.original_points = []
        self.ui.canvas.delete("polygon", "points", "temp_line")
        self.ui.preview_canvas.delete("all")
        self.aspect_ratio = 1.0
        self.ui.custom_aspect_entry.delete(0, tk.END)
        self.ui.custom_aspect_entry.insert(0, "1.0")
        self.ui.custom_aspect_entry.configure(state='disabled')
        self.ui.aspect_ratio_var.set("Estimated")
        self.ui.flip_var.set(False)
        self.ui.flop_var.set(False)
        self.ui.rotate_var.set(False)
        self.ui.update_estimated_aspect_ratio(1.0)
        self.add_to_undo_stack()
        self.ui.update_status("Selection cleared")

    def estimate_aspect_ratio(self) -> None:
        if len(self.points) == 4:
            side_lengths = [
                ((self.points[i][0] - self.points[(i + 1) % 4][0]) ** 2 +
                 (self.points[i][1] - self.points[(i + 1) % 4][1]) ** 2) ** 0.5
                for i in range(4)
            ]
            width = (side_lengths[0] + side_lengths[2]) / 2
            height = (side_lengths[1] + side_lengths[3]) / 2
            self.aspect_ratio = width / height
            self.ui.update_estimated_aspect_ratio(self.aspect_ratio)
            logger.info(f"Estimated aspect ratio: {self.aspect_ratio:.2f}")
            self.extract_texture()
        else:
            self.ui.update_estimated_aspect_ratio(1.0)

    def apply_aspect_ratio_mode(self) -> None:
        selected_mode = self.ui.aspect_ratio_var.get()
        if selected_mode == "Estimated":
            self.estimate_aspect_ratio()
        elif selected_mode == "Square":
            self.aspect_ratio = 1.0
            self.extract_texture()
        elif selected_mode == "Custom":
            self.ui.update_custom_aspect_ratio()

    def extract_texture(self) -> None:
        if self.image is not None and len(self.points) == 4:
            self.ui.update_status("Extracting texture...")
            self.thread = threading.Thread(target=self._extract_texture_thread)
            self.thread.start()
            self.ui.master.after(100, self.check_thread)

    def _extract_texture_thread(self) -> None:
        try:
            src_pts = np.array(self.original_points, dtype=np.float32)
            preview_width = self.ui.preview_canvas.winfo_width()
            preview_height = self.ui.preview_canvas.winfo_height()

            # Adjust dimensions based on aspect ratio
            if self.aspect_ratio > 1:
                w = preview_width
                h = int(w / self.aspect_ratio)
            else:
                h = preview_height
                w = int(h * self.aspect_ratio)

            warped = self.image_processor.extract_texture(self.image, src_pts, w, h)
            display_warped = cv2.cvtColor(warped, cv2.COLOR_BGR2RGB)
            self.queue.put((warped, display_warped))
        except Exception as e:
            logger.error(f"Error in texture extraction: {str(e)}")
            self.queue.put(None)

    def check_thread(self) -> None:
        if self.thread.is_alive():
            self.ui.master.after(100, self.check_thread)
        else:
            try:
                result = self.queue.get_nowait()
                if result is not None:
                    self.warped, self.display_warped = result
                    self.update_preview()
                    self.ui.update_status("Texture extracted successfully")
                else:
                    raise TextureExtractionError("Failed to extract texture")
            except queue.Empty:
                pass
            except TextureExtractionError as e:
                logger.error(str(e))
                self.ui.show_error("Error", str(e))
                self.ui.update_status("Failed to extract texture")

    def update_preview(self) -> None:
        if hasattr(self, 'display_warped'):
            preview = Image.fromarray(self.display_warped)
            if self.ui.flip_var.get():
                preview = ImageOps.flip(preview)
            if self.ui.flop_var.get():
                preview = ImageOps.mirror(preview)
            if self.ui.rotate_var.get():
                preview = preview.rotate(-90, expand=True)

            preview_width = self.ui.preview_canvas.winfo_width()
            preview_height = self.ui.preview_canvas.winfo_height()

            preview_aspect = preview.width / preview.height
            if preview_aspect > preview_width / preview_height:
                new_width = preview_width
                new_height = int(preview_width / preview_aspect)
            else:
                new_height = preview_height
                new_width = int(preview_height * preview_aspect)

            preview = preview.resize((new_width, new_height), Image.LANCZOS)

            self.preview_photo = ImageTk.PhotoImage(image=preview)
            self.ui.preview_canvas.delete("all")
            self.ui.preview_canvas.create_image(preview_width // 2, preview_height // 2, anchor=tk.CENTER,
                                                image=self.preview_photo)
            self.ui.update_status("Preview updated")

    def save_texture(self) -> None:
        if hasattr(self, 'warped'):
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("TIFF files", "*.tif"),
                    ("BMP files", "*.bmp"),
                    ("All files", "*.*")
                ]
            )
            if file_path:
                try:
                    save_image = Image.fromarray(cv2.cvtColor(self.warped, cv2.COLOR_BGR2RGB))
                    if self.ui.flip_var.get():
                        save_image = ImageOps.flip(save_image)
                    if self.ui.flop_var.get():
                        save_image = ImageOps.mirror(save_image)
                    if self.ui.rotate_var.get():
                        save_image = save_image.rotate(-90, expand=True)

                    save_image.save(file_path)
                    logger.info(f"Texture saved: {file_path}")
                    self.ui.show_info("Success", "Texture saved successfully.")
                    self.ui.update_status(f"Texture saved: {file_path}")
                except Exception as e:
                    logger.error(f"Error saving texture: {str(e)}")
                    self.ui.show_error("Error", f"Failed to save texture: {str(e)}")
                    self.ui.update_status("Failed to save texture")

    def add_to_undo_stack(self) -> None:
        state = {
            'original_points': self.original_points.copy(),
            'points': self.points.copy(),
            'flip': self.ui.flip_var.get(),
            'flop': self.ui.flop_var.get(),
            'rotate': self.ui.rotate_var.get(),
            'aspect_ratio': self.aspect_ratio,
            'aspect_ratio_mode': self.ui.aspect_ratio_var.get()
        }
        self.undo_stack.append(state)
        self.redo_stack.clear()

    def undo(self, event=None) -> None:
        if len(self.undo_stack) > 1:
            current_state = self.undo_stack.pop()
            self.redo_stack.append(current_state)
            previous_state = self.undo_stack[-1]
            self.apply_state(previous_state)
            self.ui.update_status("Undo performed")

    def redo(self, event=None) -> None:
        if self.redo_stack:
            next_state = self.redo_stack.pop()
            self.undo_stack.append(next_state)
            self.apply_state(next_state)
            self.ui.update_status("Redo performed")

    def apply_state(self, state: dict) -> None:
        self.original_points = state['original_points'].copy()
        self.points = state['points'].copy()
        self.ui.flip_var.set(state['flip'])
        self.ui.flop_var.set(state['flop'])
        self.ui.rotate_var.set(state['rotate'])
        self.aspect_ratio = state['aspect_ratio']
        self.ui.aspect_ratio_var.set(state['aspect_ratio_mode'])

        self.draw_polygon()
        if len(self.points) == 4:
            self.apply_aspect_ratio_mode()
        else:
            self.ui.preview_canvas.delete("all")
            self.ui.update_estimated_aspect_ratio(1.0)

    def add_recent_file(self, file_path: str) -> None:
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:5]  # Keep only the 5 most recent files
        save_recent_files(self.recent_files)
        self.ui.update_recent_files_menu()

    def run(self) -> None:
        self.ui.master.mainloop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    root = tk.Tk()
    app = Textractor(root)
    app.run()