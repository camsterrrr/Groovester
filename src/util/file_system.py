import logging as log
import os
from pathlib import Path
from shutil import rmtree


log.getLogger(__name__)  # Set same logging parameters as main.py.


##########################################################################
######################   CORE FILE SYSTEM LOGIC   ########################
##########################################################################


def file_in_use(path_to_file: Path) -> bool:
    """
    Function that checks if a file has an active process reading or
        writing to it.

    Args:
        path_to_file (Path): Path to the object to check. Can be an
            absolute or relative path.

    Returns:
        bool: Result of the check.
            - True: If the resource is being used by another process
            - False: If the resource is not being used.
    """

    try:
        fd = os.open(
            path_to_file, os.O_RDWR | os.O_EXCL
        )  # os.O_EXCL ensures the operation fails if in use.
        os.close(fd)

    except OSError as err:
        log.debug(f"Can't delete {path_to_file} because it's in use: {err}")

        return True

    return False


def remove_media_directory(media_path=Path("./media/")) -> bool:
    """
    This function is invoked during unit testing to remove any media files
        from the file system.

    Args:
        media_path (Path): Represents file system path to the media
            directory that should be deleted.

    Returns:
        bool: A flag indicating whether or not action was successful.
            - True: Media directory was deleted.
            - False: Exception thrown or bad file system path provided.
    """
    flag: bool = False

    if os.path.exists(media_path):
        try:
            rmtree(media_path)
            flag = True

        except OSError as os_err:
            log.error(os_err)
            flag = False

        except Exception as err:
            log.error(err)
            flag = False

    return flag


def remove_media_file(media_path: Path) -> bool:
    """
    This function removes a specified file from the file system.

    Args:
        media_path (Path): Represents file system path to the file that
            will be deleted.

    Returns:
        bool: A flag indicating whether or not action was successful.
            - True: Media file was deleted.
            - False: Exception thrown or bad file system path provided.
    """
    flag: bool = False

    if os.path.exists(media_path):
        try:
            os.remove(media_path)
            flag = True

        except OSError as os_err:
            log.error(os_err)
            flag = False

        except Exception as err:
            log.error(err)
            flag = False

    return flag


#! TODO: Create a thread that goes through and verifies the videos stored
#!  in /tmp are still there. Compare against list.
def setup_media_directory(media_path=Path("./media/")) -> bool:
    """
    This function is invoked when the Discord bot application starts. It
        creates a directory where media can be stored.

    Args:
        media_path (Path): Represents file system path where the media
            directory should be created.

    Returns:
        bool: A flag indicating whether or not action was successful.
            - True: Media directory was created or already exists.
            - False: Exception thrown or bad file system path provided.
    """
    flag: bool = True

    if not os.path.exists(media_path):
        try:
            os.mkdir(media_path)
            flag = True

        except OSError as os_err:
            log.error(os_err)
            flag = False

        except Exception as err:
            log.error(err)
            flag = False

    os.chdir(media_path)

    return flag
