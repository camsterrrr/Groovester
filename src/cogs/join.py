"""
`   Author: Cameron Oakley (Camsterrr)
    Date: Aug 2025
    Description: This file is dedicated to logic for joining Groovester to
        a voice channel.
"""

import logging as log

import discord
from discord import app_commands
from discord.ext import commands

from src.helpers import is_connected


log.getLogger(__name__)


class Join(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        """
        Join command constructor, links the bot object to the class instance.
        """
        self.bot = bot

        return

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        This event listener indicates when the cog has been loaded. Really
            just used for logging purposes and is optional.
        """
        log.debug("Successfully loaded the `Join` command cog!")

        return

    @commands.command()
    async def join(self, ctx: commands.Context) -> None:
        """
        This command triggers Groovester to join the voice channel the
            message author is connected to.
        """

        message_obj = ctx.message
        message_author = ctx.message.author

        # Validate message author is connected to a voice channel.
        if message_author.voice:

            # Connect Groovester to voice channel.
            #! TODO: Check if Groovester is already in a voice channel.
            try:
                voice_channel = message_author.voice.channel
                await voice_channel.connect()
                log.debug(
                    f"!join successfully connected to the voice channel: {voice_channel.name}"
                )

            except discord.ClientException as err:
                log.error(err)

            except Exception as err:
                log.error(err)

        # Message author is not connect to a voice channel.
        else:
            log.error("!join failed, message author is not in a voice channel.")
            await ctx.send(
                "Incorrect !join usage...\n"
                + "\tYou are not currently in a voice channel."
            )

            return

        #! TODO: Revisit multithreaded logic.
        # with self.readerCv:
        #     self.readerCv.notify()

        # Send some helpful commands to the user.
        await ctx.send(
            "Groovester successfully joined the voice channel!"
            + " Here are some useful commands to get you started:\n"
            + "!join usage:\t!join\n"
            + "\tGroovester will join the voice channel that the message author is connected to.\n"
            + "!leave usage:\t!leave\n"
            + "\tGroovester will leave the voice channel it is currently connected to.\n"
            + "!play usage:\t!play *URL to YouTube URL*\n"
            + "\tGroovester will download YouTube video and play it in a voice channel.\n"
        )

        return
    