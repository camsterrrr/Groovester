import logging as log
import os
from pathlib import Path

import discord
from pytube import YouTube

from src.constants import ClientHelpMessages, DebugMessages, ErrorMessages, InfoMessages

log.getLogger(__name__)  # Set same logging parameters as client.py.


def checkIfFileIsInUse(absPathToFile: str) -> bool:

    try:
        fd = os.open(
            absPathToFile, os.O_RDWR | os.O_EXCL
        )  # os.O_EXCL ensures the operation fails if in use.
        os.close(fd)
    except OSError as err:
        log.debug("Can't delete " + absPathToFile + " becuase it's in use: " + err)

        return True

    return False


#! Todo: Make class that can store URL and absolute file path on local file system.
def downloadYouTubeAudio(linkToYouTubeVideo: str):
    """Helper function used to download a YouTube video given a valid URL."""

    #!  Todo: Ensure that the local file system has enough space for the video.
    ytObj = YouTube(linkToYouTubeVideo)
    audioStream = (
        ytObj.streams.get_audio_only()
    )  # Only download audio and save it as .mp4.

    # Download video via pytube API.
    try:
        absPathToDownloadedVideo = audioStream.download()
    except OSError as err:
        log.error("%s %s", ErrorMessages._exceptionPlayFailedToDownloadVideo, err)
        return None
    except Exception as err:
        log.error(err)
        return None

    if not os.path.exists(absPathToDownloadedVideo):
        return None
    log.debug(
        "%s %s", InfoMessages._logPlaySuccessfulyDownloadedVideo, linkToYouTubeVideo
    )

    # Store key information relating to the video in a PyTube object.
    pytubeObj = PyTube(absPathToDownloadedVideo, linkToYouTubeVideo, ytObj)

    return pytubeObj


#!  Todo: Create a thread that goes through and verifies the videos stored in /tmp are still there.
#!       Compare against list.
def setup_media_directory(media_path=Path("./media/")) -> bool:
    """
    This function is invoked when the Groovester application starts. It
        creates a directory where media can be stored.

    Args:
        media_path (Path): Represents file system path where the media
            directory should be created.

    Returns:
        bool: A flag indicating whether or not action was successful.
            - True: Media directoy was created or already exists.
            - False: Exception thrown or bad file system path provided.
    """

    if not os.path.exists(media_path):
        try:
            os.mkdir(media_path)

        except OSError as os_err:
            log.error(os_err)
            return False

        except Exception as err:
            log.error(err)
            return False

    os.chdir(media_path)

    return True


class PyTube:

    def __init__(self, absPathToFile: str, url: str, pytube: YouTube):
        self.absPathToFile = absPathToFile
        self.url = url
        self.pytube = pytube
