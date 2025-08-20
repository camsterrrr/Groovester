from enum import Enum
import logging as log


#! Todo: Add more log levels.
class LogLevel(Enum):
    """
    Enum class used to define the log level for the application.
    """

    INFO = log.INFO
    DEBUG = log.DEBUG


def configure_project_logging(logging_level=log.INFO) -> None:
    """
    Function to configure logging for the Groovester application. It
    ensures that all parts of the application have the same
    logging configuration.

    Args:
        logging_level (LogLevel): Represents what class of logging to
            configure for the application.
    """
    
    
    print(logging_level)

    log.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="Groovester.log",
        format="%(levelname)s,%(asctime)s,%(message)s",
        level=logging_level,
    )

    return
