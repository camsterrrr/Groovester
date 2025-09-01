import datetime
import logging as log
import os
from pathlib import Path

import discord
from discord.ext import commands
from pytubefix import YouTube
from validators import ValidationError, url


log.getLogger(__name__)  # Set same logging parameters as main.py.


##########################################################################
######################   CORE APPLICATION LOGIC   ########################
##########################################################################


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
        self.path_to_file: Path = path_to_file
        self.requestor: discord.member.Member = requestor
        self.timestamp: datetime = datetime.datetime.now()
        self.media_url: str = media_url
        self.pytube: YouTube = pytube


def download_youtube_audio(
    media_url: str, requestor: discord.member.Member
) -> DownloadedMedia:
    """
    Helper function used to download a YouTube video given a valid YouTube
        URL. Future work will allow for other types of streamed media, like
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
    # Download video via `pytubefix` API.
    try:
        #! TODO: Ensure that the local file system has enough space for
        #!  the video.
        youtube_obj = YouTube(media_url)
        audio_stream = youtube_obj.streams.get_audio_only(
            subtype="mp4"
        )  # Only download audio and save it as .mp4.
        path_to_file = Path(
            audio_stream.download(filename=f"{youtube_obj.video_id}.mp4")
        )
        log.debug(f"Downloaded the following song: {media_url}")

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


def is_connected(ctx: commands.Context) -> bool:
    """
    Function to check if the Discord bot is actively connected to a voice
        channel.
    """
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

    return voice_client and voice_client.is_connected()


def validate_url(media_url: str) -> bool:
    """
    Function that validates a given URL is valid.

    Args:
        media_url (str): URL of media that needs to be validated.

    Returns:
        Bool: Indicates whether the URL is valid or not.
    """
    try:
        flag = url(media_url)

    except ValidationError as v_err:
        log.error(f"Validation error, unable to validate {media_url}: {v_err}")
        flag = False

    except Exception as err:
        log.error(
            f"General exception, unexpected error occurred when trying to test the media URL: {err}"
        )
        flag = False

    return flag


def validate_url_domain(media_url: str) -> bool:
    """
    Function that validates if a URL has an allowed domain.

    Args:
        media_url (str): URL of media that needs to be validated.

    Returns:
        Bool: Indicates whether the URL is valid or not.
    """
    #! TODO: There are several YouTube domains to check for.
    valid_domains: list = [
        "www.youtube.com",
        "www.youtu.be",
        "https://www.youtube.com",
        "https://www.youtu.be",
    ]

    if any(media_url.startswith(i) for i in valid_domains):
        flag = True

    else:
        flag = False

    return flag
