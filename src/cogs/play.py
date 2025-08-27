"""
`   Author: Cameron Oakley (Camsterrr)
    Date: Aug 2025
    Description: This file is dedicated to logic for removing Groovester
        from the voice channel it's connected to.
"""

import logging as log

import discord
from discord import app_commands
from discord.ext import commands
from validators import url

from src.helpers import DownloadedMedia, download_youtube_audio
from src.threads import ThreadWarden, THREAD_WARDEN


log.getLogger(__name__)


#! TODO: There are several YouTube domnains to check for.
YOUTUBE_DOMAINS: list = ["www.youtube.com", "www.youtu.be"]


class Play(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        """
        Play command constructor, links the bot object to the class instance.
        """
        self.bot = bot

        return

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        This event listener indicates when the cog has been loaded. Really
            just used for logging purposes and is optional.
        """
        log.debug("Successfully loaded the `Play` command cog!")

        return

    @commands.command()
    async def play(self, ctx: commands.Context) -> None:
        """
        This command triggers Groovester to leave the voice channel that
            it's connected to.
        """

        """Client event to download a song and place it in the queue."""

        # Input validation: The command should be in the format of:
        #   !play https://youtube.com/arbitrary/url
        play_command = ctx.message.content
        media_url = None

        if (
            len(play_command) > 5
            and play_command[:5] == "!play"
            and play_command[5] == " "
        ):
            media_url = play_command[6:]

        else:
            await ctx.send(
                "Incorrect !play usage...\n" + "\t!play *URL to YouTube video*"
            )

            return

        # Check domain is what is expected.
        #! TODO: There are several YouTube domnains to check for.
        if not media_url.startswith("https://www.youtube.com/"):
            await ctx.send(
                "Incorrect !play usage...\n" + "\tPlease enter a valid domain."
            )

            return

        # Test if the Domain is reachable and valid.
        # *  (Emphasis on Domain)
        if not url(media_url):
            await ctx.send("Incorrect !play usage...\n\tEnter a valid domain.")

            return

        #! TODO: Add logic to limit the number of downloaded videos to ten.
        # Download the YouTube video.
        #! TODO: Pass author name as requestor so that it's in the
        #   DownloadedMedia object.
        downloaded_media = download_youtube_audio(media_url, ctx.message.author)
        if downloaded_media is None:
            await ctx.send("Groovester failed to download the requested video!")

            return

        # Acquire lock and await signal.
        with THREAD_WARDEN.writer_cv:

            # Fall through, only if there are no active readers or writers.
            while THREAD_WARDEN.num_readers or THREAD_WARDEN.num_writers:
                THREAD_WARDEN.writer_cv.wait()

            # * Enter mutual exclusion zone.
            THREAD_WARDEN.num_writers = THREAD_WARDEN.num_writers + 1  # Lock

            log.info(
                f"Adding the following media to the song queue: {downloaded_media.path_to_file}",
            )
            THREAD_WARDEN.song_queue.append(downloaded_media)

            THREAD_WARDEN.num_writers = THREAD_WARDEN.num_writers - 1  # Unlock
            # * Exit mutual exclusion zone.

            # Signal any threads waiting to run.
            with THREAD_WARDEN.reader_cv:
                THREAD_WARDEN.reader_cv.notify()
            THREAD_WARDEN.writer_cv.notify()

        # #! TODO: If Groovester is not already in the voice channel have it connect to the voice channel.
        # if not is_connected(ctx):
        #     await join(ctx)

        return
