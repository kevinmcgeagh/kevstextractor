# src/ui/ui_manager.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkhtmlview import HTMLLabel
from src.config.settings import ABOUT_TEXT, UI_TEXTS, SUPPORTED_IMAGE_TYPES, WINDOW_WIDTH, WINDOW_HEIGHT, \
    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT


class UIManager:
    def __init__(self, master: tk.Tk, controller):
        self.master = master
        self.controller = controller
        self.last_valid_aspect_ratio = "1.0"
        self.setup_ui()
        self.create_menu()
        self.create_status_bar()

    def setup_ui(self):
        self.master.title(UI_TEXTS["app_title"])
        self.master.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.master.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', padding=5)
        style.configure('TLabel', padding=2)

        # Create main frames
        self.paned_window = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.paned_window)
        self.right_frame = ttk.Frame(self.paned_window)

        self.paned_window.add(self.left_frame, weight=3)
        self.paned_window.add(self.right_frame, weight=1)

        # Setup left frame (main image canvas)
        self.canvas = tk.Canvas(self.left_frame, bg='#1E1E1E', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Setup right frame (preview and controls)
        self.preview_canvas = tk.Canvas(self.right_frame, bg='#1E1E1E', highlightthickness=0)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)

        self.control_frame = ttk.Frame(self.right_frame)
        self.control_frame.pack(fill=tk.X, pady=(10, 0))

        # Control buttons
        self.load_button = ttk.Button(self.control_frame, text=UI_TEXTS["load_button"])
        self.load_button.pack(fill=tk.X, pady=2)

        self.clear_button = ttk.Button(self.control_frame, text=UI_TEXTS["clear_button"])
        self.clear_button.pack(fill=tk.X, pady=2)

        self.save_button = ttk.Button(self.control_frame, text=UI_TEXTS["save_button"])
        self.save_button.pack(fill=tk.X, pady=2)

        # Aspect ratio options
        aspect_ratio_frame = ttk.Frame(self.control_frame)
        aspect_ratio_frame.pack(fill=tk.X, pady=(5, 0))

        self.aspect_ratio_label = ttk.Label(aspect_ratio_frame, text=UI_TEXTS["aspect_ratio_label"])
        self.aspect_ratio_label.pack(side=tk.LEFT)

        self.aspect_ratio_var = tk.StringVar(value="Estimated")
        self.aspect_ratio_menu = ttk.OptionMenu(
            aspect_ratio_frame,
            self.aspect_ratio_var,
            "Estimated",
            "Estimated", "Square", "Custom",
            command=self.update_aspect_ratio
        )
        self.aspect_ratio_menu.pack(side=tk.LEFT, padx=(5, 10))

        # Custom aspect ratio entry with validation
        vcmd = (self.master.register(self.validate_float_input), '%P')
        self.custom_aspect_entry = ttk.Entry(aspect_ratio_frame, width=10, validate='key', validatecommand=vcmd)
        self.custom_aspect_entry.pack(side=tk.LEFT)
        self.custom_aspect_entry.insert(0, "1.0")
        self.custom_aspect_entry.configure(state='disabled')
        self.custom_aspect_entry.bind('<KeyRelease>', self.auto_complete_decimal)
        self.custom_aspect_entry.bind('<FocusOut>', self.commit_custom_aspect_ratio)
        self.custom_aspect_entry.bind('<Return>', self.commit_custom_aspect_ratio)

        # Add estimated aspect ratio display label
        self.estimated_aspect_label = ttk.Label(self.control_frame, text=UI_TEXTS["estimated_aspect_label"].format(1.0))
        self.estimated_aspect_label.pack(fill=tk.X, pady=(5, 0))

        # Image transformation options
        self.flip_var = tk.BooleanVar()
        self.flip_check = ttk.Checkbutton(self.control_frame, text=UI_TEXTS["flip_checkbox"], variable=self.flip_var)
        self.flip_check.pack(fill=tk.X, pady=2)

        self.flop_var = tk.BooleanVar()
        self.flop_check = ttk.Checkbutton(self.control_frame, text=UI_TEXTS["flop_checkbox"], variable=self.flop_var)
        self.flop_check.pack(fill=tk.X, pady=2)

        self.rotate_var = tk.BooleanVar()
        self.rotate_check = ttk.Checkbutton(self.control_frame, text=UI_TEXTS["rotate_checkbox"],
                                            variable=self.rotate_var)
        self.rotate_check.pack(fill=tk.X, pady=2)

    def create_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.controller.load_image)

        # Recent files submenu
        self.recent_files_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Open Recent", menu=self.recent_files_menu)
        self.update_recent_files_menu()

        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="About", command=self.show_about)

    def create_status_bar(self):
        self.status_bar = ttk.Label(self.master, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_aspect_ratio(self, value):
        if value == "Estimated":
            self.custom_aspect_entry.configure(state='disabled')
            self.controller.estimate_aspect_ratio()
        elif value == "Square":
            self.custom_aspect_entry.configure(state='disabled')
            self.controller.aspect_ratio = 1.0
            self.controller.extract_texture()
        elif value == "Custom":
            self.custom_aspect_entry.configure(state='normal')
            self.custom_aspect_entry.focus_set()

    def validate_float_input(self, value):
        if value == "":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False

    def commit_custom_aspect_ratio(self, event=None):
        if self.custom_aspect_entry.cget('state') == 'disabled':
            return
        value = self.custom_aspect_entry.get()
        if value == "":
            self.custom_aspect_entry.delete(0, tk.END)
            self.custom_aspect_entry.insert(0, self.last_valid_aspect_ratio)
            return
        try:
            custom_ratio = float(value)
            if 0.1 <= custom_ratio <= 10.0:
                self.last_valid_aspect_ratio = value
                self.controller.aspect_ratio = custom_ratio
                self.controller.extract_texture()
            else:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", UI_TEXTS["custom_aspect_error"])
            self.custom_aspect_entry.delete(0, tk.END)
            self.custom_aspect_entry.insert(0, self.last_valid_aspect_ratio)
        finally:
            if event and event.type == '10':  # FocusOut event
                self.master.focus_set()  # Remove focus from the entry

    def auto_complete_decimal(self, event):
        value = self.custom_aspect_entry.get()
        if value == ".":
            self.custom_aspect_entry.delete(0, tk.END)
            self.custom_aspect_entry.insert(0, "0.")
            self.custom_aspect_entry.icursor(tk.END)

    def update_estimated_aspect_ratio(self, value):
        self.estimated_aspect_label.config(text=UI_TEXTS["estimated_aspect_label"].format(value))

    def update_recent_files_menu(self):
        self.recent_files_menu.delete(0, tk.END)
        if hasattr(self.controller, 'recent_files'):
            for file in self.controller.recent_files:
                self.recent_files_menu.add_command(label=file, command=lambda f=file: self.controller.load_image(f))
        else:
            self.recent_files_menu.add_command(label="No recent files", state=tk.DISABLED)

    def show_user_guide(self):
        guide_window = tk.Toplevel(self.master)
        guide_window.title("Kev's Textractor User Guide")
        guide_window.geometry("800x600")

        # Create a frame with scrollbar
        frame = ttk.Frame(guide_window)
        frame.pack(fill=tk.BOTH, expand=True)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create an HTMLLabel widget
        with open('resources/user_guide.html', 'r') as file:
            html_content = file.read()

        # Remove any DOCTYPE, html, head, and body tags
        html_content = html_content.replace('<!DOCTYPE html>', '').replace('<html>', '').replace('</html>', '')
        html_content = html_content.replace('<head>', '').replace('</head>', '')
        html_content = html_content.replace('<body>', '').replace('</body>', '')

        html_label = HTMLLabel(frame, html=html_content, yscrollcommand=scrollbar.set)
        html_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=html_label.yview)

        # Make the window modal
        guide_window.transient(self.master)
        guide_window.grab_set()
        self.master.wait_window(guide_window)

    def show_about(self):
        messagebox.showinfo("About Kev's Textractor", ABOUT_TEXT)

    def update_status(self, message):
        self.status_bar.config(text=message)
        self.master.update_idletasks()

    def setup_bindings(self, on_press, on_release, on_drag, on_move, on_resize, on_closing):
        self.canvas.bind("<ButtonPress-1>", on_press)
        self.canvas.bind("<ButtonRelease-1>", on_release)
        self.canvas.bind("<B1-Motion>", on_drag)
        self.canvas.bind("<Motion>", on_move)
        self.master.bind("<Configure>", on_resize)
        self.master.protocol("WM_DELETE_WINDOW", on_closing)

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def show_info(self, title, message):
        messagebox.showinfo(title, message)

    def ask_quit(self):
        return messagebox.askokcancel("Quit", "Do you want to quit?")

    def get_save_file_path(self):
        return filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=SUPPORTED_IMAGE_TYPES
        )

    def get_open_file_path(self):
        return filedialog.askopenfilename(filetypes=SUPPORTED_IMAGE_TYPES)