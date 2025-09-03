from argparse import ArgumentParser, Namespace
from asyncio import run
import logging as log
from os.path import exists
from pathlib import Path
from sys import exit

from src.bot import main_bot
from src.util.file_system import setup_media_directory


LOG_LEVELS = {
    "none": log.NOTSET,
    "debug": log.DEBUG,
    "info": log.INFO,
    "warning": log.WARNING,
    "error": log.ERROR,
}


def check_ffmpeg_path(ffmpeg_path: Path) -> bool:
    """
    Function that checks if the user-specified FFMPEG binary path actually
        exists on the file system.

    Args:
        ffmpeg_path (Path): Path object to the FFMPEG binary.

    Returns:
        bool: Whether or not the path exists.
    """
    if not exists(ffmpeg_path):
        log.error(
            "FFMMPEG binary doesn't exist on the file system. Please check the path parameter you specified."
        )
        print(
            "FFMMPEG binary doesn't exist on the file system. Please check the path parameter you specified."
        )

        return False

    return True


def configure_argparse() -> Namespace:
    """
    Function that instantiates the ArgumentParser object that interprets
        user-specified parameters.

    Returns:
        Namespace: The parameters the user specified.
    """
    parser = ArgumentParser()

    parser.add_argument(
        "-co",
        "--command_output",
        choices=[True, False],
        default=False,
        help="Whether or not you want the bot to send messages in response to regular commands (not slash commands - these respond ephemerally). Enabling this means the bot would send messages that notify everyone in the server.",
        type=bool,
    )
    parser.add_argument(
        "-f", "--ffmpeg", help="The path to your FFMPEG executable.", type=Path
    )
    parser.add_argument(
        "-l",
        "--log",
        choices=list(LOG_LEVELS.keys()),
        default="info",
        help='Set the logging level of the application. Default is "INFO" level logging.',
        type=str,
    )
    parser.add_argument(
        "-m",
        "--media",
        help="The path to the media directory where temporary files are stored.",
        default=Path("./media/"),
        type=Path,
    )

    return parser.parse_args()


def configure_logging(user_specified_level: str = "info"):
    """
    Function that configures logging for the entire project.

    Args:
        log_level (int, optional): User-specified log level. Defaults to
            2, which represents INFO mode.
    """
    log_level = LOG_LEVELS.get(user_specified_level.lower(), log.INFO)

    log.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="Groovester.log",
        format="%(levelname)s,%(asctime)s,%(message)s",
        level=log_level,
    )

    return


##########################################################################
############################   ENTRY POINT   #############################
##########################################################################


if __name__ == "__main__":
    """
    This serves as the entry point to the Groovester application.
    """
    # Try to start the Groovester's client thread.
    try:
        # Parse user specified parameters
        user_args = configure_argparse()

        # Configure project logging.
        configure_logging(user_args.log)

        log.info(
            "\n==================================================="
            + "\n\t\t\tNew Groovester instance started!"
            + "\n==================================================="
        )
        log.debug("Attempting to start Groovester!")
        print("Attempting to start Groovester!")

        # End the program if the FFMPEG path doesn't exist.
        if not check_ffmpeg_path:
            exit()

        # Setup the directory where media will be stored temporarily.
        setup_media_directory(user_args.media)
        import os

        print(os.getcwd())

        # Create Discord's client connection object.
        run(main_bot())

    except Exception as err:
        log.error(
            "A general error occurred while trying to start the Groovester client: %s",
            err,
        )
