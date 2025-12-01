import sys
import logging


# ANSI Escape codes for coloring console output
class LogColors:
    GREY = "\x1b[38;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"


class CustomFormatter(logging.Formatter):
    """
    Custom formatter to add specific colors based on the log level.
    Only applied to Console output.
    """
    
    # Format: [Time] [Level] - Message
    FORMAT = "[%(asctime)s] [%(levelname)s] - %(message)s"

    FORMATS = {
        logging.DEBUG: LogColors.GREY + FORMAT + LogColors.RESET,
        logging.INFO: LogColors.GREEN + FORMAT + LogColors.RESET,
        logging.WARNING: LogColors.YELLOW + FORMAT + LogColors.RESET,
        logging.ERROR: LogColors.RED + FORMAT + LogColors.RESET,
        logging.CRITICAL: LogColors.BOLD_RED + FORMAT + LogColors.RESET
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)
    

class Logger:
    """
    Static wrapper around the Python logging module.
    Initializes both File and Console handlers.
    """
    _logger = None

    @staticmethod
    def init(name: str = "PyEngine", log_file: str = "logs/engine.log", debug_mode: bool = True):
        """
        Sets up the logger instance.
        """
        Logger._logger = logging.getLogger(name)
        
        # Set default level
        level = logging.DEBUG if debug_mode else logging.INFO
        Logger._logger.setLevel(level)

        # 1. Console Handler (with Colors)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(CustomFormatter())
        
        # 2. File Handler (Clean text, no colors)
        file_handler = logging.FileHandler(log_file, mode='w') # 'w' overwrites log each run
        file_handler.setLevel(level)
        file_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
        file_handler.setFormatter(file_formatter)

        # Add handlers to the logger
        if not Logger._logger.hasHandlers():
            Logger._logger.addHandler(console_handler)
            Logger._logger.addHandler(file_handler)
        
        Logger.info("Logger initialized successfully.")

    @staticmethod
    def debug(msg: str):
        if Logger._logger: Logger._logger.debug(msg)

    @staticmethod
    def info(msg: str):
        if Logger._logger: Logger._logger.info(msg)

    @staticmethod
    def warning(msg: str):
        if Logger._logger: Logger._logger.warning(msg)

    @staticmethod
    def error(msg: str):
        if Logger._logger: Logger._logger.error(msg)
    
    @staticmethod
    def critical(msg: str):
        if Logger._logger: Logger._logger.critical(msg)
