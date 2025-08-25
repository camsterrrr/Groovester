import datetime
import logging as log
import os
from pathlib import Path

import discord
from discord.ext import commands
from pytube import YouTube


log.getLogger(__name__)  # Set same logging parameters as client.py.

VOICE_CLIENT: discord.VoiceClient = None


class DownloadedMedia:
    """
    Object that maintains reference to relevant information for song
        requests.
    """

    def __init__(
        self,
        path_to_file: Path,
        requestor: discord.member.Member,  # The message author.
        media_url: str,
        pytube: YouTube,
    ):
        self.path_to_file = path_to_file
        self.requestor = requestor
        self.timestamp = datetime.datetime.now()
        self.media_url = media_url
        self.pytube = pytube


def download_youtube_audio(
    media_url: str, requestor: discord.member.Member
) -> DownloadedMedia:
    """
    Helper function used to download a YouTube video given a valid YouTube
        URL.
    Future work will allow for other types of streamed media, like
        Spotify.

    Args:
        media_path (str): Represents a URL of the YouTube video that the
            user wants to download.
        requestor (discord.member.Member): Represents the Member object
            of the !play command's message author.

    Returns:
        DownloadedMedia: An object that stores relevant information for
            the request.
    """

    #!  Todo: Ensure that the local file system has enough space for the video.
    youtube_obj = YouTube(media_url)
    audio_stream = (
        youtube_obj.streams.get_audio_only()  # ? ASCII characters issue?
    )  # Only download audio and save it as .mp4.

    # Download video via pytube API.
    try:
        log.debug(f"Attempting to download the following song: {media_url}")
        path_to_file = Path(audio_stream.download())

    except OSError as os_err:
        log.error(f"OS exception, unexpected error occurred: {os_err}")

        return

    except Exception as err:
        log.error(f"General exception, unexpected error occurred: {err}")

        return

    # Sanity check.
    if not os.path.exists(path_to_file):
        log.debug(
            f"Failed to download the following video, no file exists on the local file system: {media_url}"
        )
        return

    log.info(f"Successfully downloaded the following video: {media_url}")

    # Store key information relating to the video in a PyTube object.
    downloaded_media = DownloadedMedia(path_to_file, requestor, media_url, youtube_obj)

    return downloaded_media


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
        log.debug(f"Can't delete {path_to_file} becuase it's in use: {err}")

        return True

    return False


def is_connected(ctx: commands.Context) -> bool:
    """
    Function to check if Groovester is actively connected to a voice
        channel.
    """
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

    return voice_client and voice_client.is_connected()


def set_voice_client(voice_client_operation):
    global VOICE_CLIENT
    VOICE_CLIENT = voice_client_operation


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
