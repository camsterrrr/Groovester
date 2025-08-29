import asyncio
import logging as log

from src.bot import main_bot
from src.util.helpers import setup_media_directory


if __name__ == "__main__":
    """
    This serves as the entry point to the Groovester application.
    """

    #! TODO: Allow user to specify log level. Add user-input parameters.
    log.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="Groovester.log",
        format="%(levelname)s,%(asctime)s,%(message)s",
        level=log.DEBUG,
    )

    # Try to start the Groovester's client thread.
    try:
        log.info(
            "\n==================================================="
            + "\n\t\t\tNew Groovester instance started!"
            + "\n==================================================="
        )
        log.debug("Attempting to start Groovester!")

        # Create Discord's client connection object.
        asyncio.run(main_bot())

        # Setup the directory where media will be sotred temporarily.
        setup_media_directory()

    except Exception as err:
        log.error(
            "A general error occurred while trying to start the Groovester client: %s",
            err,
        )
