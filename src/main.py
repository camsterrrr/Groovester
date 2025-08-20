import logging as log

from src.client import create_discord_client_instance
from src.helpers import setup_media_directory


if __name__ == "__main__":
    """
        This serves as the entry point to the Groovester application.
    """
    
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
        client = create_discord_client_instance()
        
        # Setup the directory where media will be sotred temporarily.
        setup_media_directory()
        

    except Exception as err:
        log.error(
            "A general error occurred while trying to start the Groovester client: %s",
            err,
        )
