# run.py

# Import necessary modules
import sys  # For system-specific parameters and functions
import logging  # For logging messages
from dependency_checker import dependency_checker  # Custom module to check for required dependencies


def main():
    """
    Main function to run the Kev's Textractor application.
    This function sets up logging, checks dependencies, and launches the application.
    """

    # Set up logging configuration
    # This will log messages with timestamps, logger name, log level, and the actual message
    logging.basicConfig(
        level=logging.INFO,  # Set the logging level to INFO (you can change this to DEBUG for more detailed logs)
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'  # Format for the timestamp
    )

    # Create a logger object for this module
    logger = logging.getLogger(__name__)

    # Log the start of the application
    logger.info("Starting the application")

    # Check if all required dependencies are installed
    if dependency_checker():
        # If all dependencies are satisfied, proceed with launching the application
        logger.info("All dependencies are satisfied. Launching the application.")

        try:
            # Import the run_application function from the main module
            # We import here rather than at the top of the file to ensure all dependencies are met before importing
            from main import run_application

            # Run the main application
            run_application()

        except ImportError as e:
            # If there's an error importing the main module, log the error and exit
            logger.error(f"Failed to import the main module: {str(e)}")
            logger.error("The application will now exit.")
            sys.exit(1)  # Exit with an error code

        except Exception as e:
            # Catch any other exceptions that might occur during runtime
            logger.exception(f"An unexpected error occurred while running the application: {str(e)}")
            logger.error("The application will now exit.")
            sys.exit(1)  # Exit with an error code

    else:
        # If dependencies are missing, log an error and exit
        logger.error("Missing dependencies. Unable to start the application.")
        logger.error("Please install the required dependencies and try again.")
        sys.exit(1)  # Exit with an error code


# This block ensures that the main() function is only called if this script is run directly
# (not imported as a module)
if __name__ == "__main__":
    main()
