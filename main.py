# main.py

# Import necessary modules
import logging  # For logging messages
import tkinter as tk  # For creating the GUI
from tkinter import messagebox  # For displaying message boxes in the GUI
from src.core.textractor import Textractor  # Import our main application class
from src.config.settings import LOG_FILE, WINDOW_WIDTH, WINDOW_HEIGHT  # Import settings


def setup_logging():
    """
    Set up logging configuration for the application.
    This function configures both file and console logging.
    """
    # Configure the root logger
    logging.basicConfig(
        filename=LOG_FILE,  # Log to a file specified in settings
        level=logging.INFO,  # Set the logging level to INFO (can be changed to DEBUG for more details)
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'  # Format for the timestamp
    )

    # Create a console handler to also log to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def run_application():
    """
    Initialize and run the main application.
    This function sets up logging, creates the main window, and starts the application.
    """
    # Set up logging
    setup_logging()

    # Create a logger object for this module
    logger = logging.getLogger(__name__)

    try:
        # Log the start of application initialization
        logger.info("Initializing the Textractor application.")

        # Create the main Tkinter window
        root = tk.Tk()
        root.title("Textractor")  # Set the window title

        # Set initial window size
        root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # Set minimum window size to ensure all elements are visible
        root.minsize(800, 600)

        # Hide the default Tkinter icon
        # This is done to allow for a custom icon to be set later if desired
        root.iconbitmap(default="")

        # Create an instance of our main application class
        app = Textractor(root)

        # Log successful initialization
        logger.info("Application initialized successfully. Starting main loop.")

        # Start the Tkinter event loop
        # This keeps the window open and responds to user interactions
        app.run()

    except Exception as e:
        # Catch and log any unexpected errors during initialization or runtime
        logger.exception(f"An error occurred while running the application: {str(e)}")

        # Display an error message to the user
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    finally:
        # Log application closure, whether it closed normally or due to an error
        logger.info("Application closed.")


if __name__ == "__main__":
    # This block is executed only if the script is run directly (not imported)
    print("This script should not be run directly. Please use run.py instead.")
    print("If you're a developer testing this module, you can comment out this check.")
    # Uncomment the following line for testing purposes:
    # run_application()