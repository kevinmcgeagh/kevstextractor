# dependency_checker.py

import importlib
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import logging

logger = logging.getLogger(__name__)

# List of required libraries
REQUIRED_LIBRARIES = [
    "opencv-python", "numpy", "Pillow", "tkinter", "tkhtmlview"
]

def install_libraries(libraries):
    """
    Install the selected libraries using pip.
    """
    for lib in libraries:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            logger.info(f"Successfully installed {lib}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {lib}: {str(e)}")
            messagebox.showerror("Error", f"Failed to install {lib}: {str(e)}")

def check_libraries():
    """
    Check if required libraries are installed.
    """
    missing_libraries = []
    for lib in REQUIRED_LIBRARIES:
        try:
            if lib == "opencv-python":
                importlib.import_module("cv2")
            elif lib == "Pillow":
                importlib.import_module("PIL")
            else:
                importlib.import_module(lib)
        except ImportError:
            missing_libraries.append(lib)
    return missing_libraries

def dependency_checker():
    """
    Check for missing libraries and provide a GUI for installation.
    """
    missing_libraries = check_libraries()
    if not missing_libraries:
        logger.info("All required libraries are installed")
        return True
    else:
        logger.warning(f"Missing libraries: {', '.join(missing_libraries)}")
        root = tk.Tk()
        root.title("Missing Dependencies")
        root.geometry("400x300")

        style = ttk.Style(root)
        style.theme_use('clam')

        frame = ttk.Frame(root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        label = ttk.Label(frame, text="The following libraries are missing:", font=('Arial', 12))
        label.pack(anchor=tk.W, pady=(0, 10))

        selected_libraries = {lib: tk.BooleanVar(value=True) for lib in missing_libraries}

        for lib, var in selected_libraries.items():
            checkbox = ttk.Checkbutton(frame, text=lib, variable=var, style='TCheckbutton')
            checkbox.pack(anchor=tk.W, pady=2)

        def install_selected_libraries():
            libraries_to_install = [lib for lib, var in selected_libraries.items() if var.get()]
            if libraries_to_install:
                install_button.config(state=tk.DISABLED)
                progress_bar.pack(pady=(10, 0), fill=tk.X)
                root.update()

                for i, lib in enumerate(libraries_to_install):
                    install_libraries([lib])
                    progress_bar['value'] = (i + 1) / len(libraries_to_install) * 100
                    root.update()

                root.destroy()
                missing_libraries_after_install = check_libraries()
                if missing_libraries_after_install:
                    logger.error(f"The following libraries are still missing: {', '.join(missing_libraries_after_install)}")
                    messagebox.showerror("Error", f"The following libraries are still missing: {', '.join(missing_libraries_after_install)}\nThe program will now close.")
                    return False
                else:
                    logger.info("All required libraries are now installed")
                    return True
            else:
                logger.warning("No libraries selected for installation")
                messagebox.showwarning("Warning", "No libraries selected. The program may not function correctly.")
                root.destroy()
                return False

        install_button = ttk.Button(frame, text="Install Selected", command=install_selected_libraries)
        install_button.pack(pady=(20, 0))

        progress_bar = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=300, mode='determinate')

        root.mainloop()

        # Check again after the window is closed
        missing_libraries = check_libraries()
        if missing_libraries:
            logger.error(f"The following libraries are still missing: {', '.join(missing_libraries)}")
            messagebox.showerror("Error", f"The following libraries are still missing: {', '.join(missing_libraries)}\nThe program will now close.")
            return False

    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    result = dependency_checker()
    print(f"Dependency check result: {'All dependencies satisfied' if result else 'Missing dependencies'}")