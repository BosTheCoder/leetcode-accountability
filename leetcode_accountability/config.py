import logging

def setup_logging():
    """Set up logging to console and file with line numbers."""
    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("cli.log")

    # Set levels (INFO for both, adjust if needed)
    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)

    # Define formatter with line numbers
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Apply formatter
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Get root logger and attach handlers
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Reduce verbosity from gql library
    logging.getLogger("gql.transport.requests").setLevel(logging.WARNING)
