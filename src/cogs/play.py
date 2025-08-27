"""
`   Author: Cameron Oakley (Camsterrr)
    Date: Aug 2025
    Description: This file is dedicated to logic for removing Groovester
        from the voice channel it's connected to.
"""

import logging as log

import discord
from discord.ext import commands

from src.helpers import download_youtube_audio, validate_url, validate_url_domain
from src.threads import get_thread_warden


log.getLogger(__name__)


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
        This command triggers the bot to download a song and place it in
            the queue.
        """
        # Input validation: The command should be in the format of:
        #   '!play https://youtube.com/arbitrary/url'
        play_command = ctx.message.content
        media_url = None

        if (
            len(play_command) > 5
            and play_command[:5] == "!play"
            and play_command[5] == " "
        ):
            media_url = play_command[6:]
            log.debug(f"Stripped message: {media_url}")

        else:
            await ctx.send("Incorrect !play usage...\n\t!play *URL to YouTube video*")

            return

        # * 1. Check domain is what is expected.
        if not validate_url_domain(media_url):
            await ctx.send("Incorrect !play usage...\n\tPlease enter a valid domain.")

            return

        # * 2. Test if the Domain is reachable and valid.
        # *  (Emphasis on Domain)
        if not validate_url(media_url):
            await ctx.send("Incorrect !play usage...\n\tEnter a valid domain.")

        #! TODO: Add logic to limit the number of downloaded videos to ten.
        #!  Download the YouTube video.
        #! TODO: Pass author name as requestor so that it's in the
        #!  DownloadedMedia object.
        downloaded_media = download_youtube_audio(media_url, ctx.message.author)
        if downloaded_media is None:
            await ctx.send("Groovester failed to download the requested video!")

            return

        #! TODO: Invoke add song to queue logic.
        get_thread_warden().add_media_to_queue(downloaded_media)

        # ! TODO: If Groovester is not already in the voice channel have
        # !  it connect to the voice channel.
        # if not is_connected(ctx):
        #     await join(ctx)

        return
