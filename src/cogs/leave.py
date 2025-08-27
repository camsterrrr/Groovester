"""
`   Author: Cameron Oakley (Camsterrr)
    Date: Aug 2025
    Description: This file is dedicated to logic for removing Groovester
        from the voice channel it's connected to.
"""

import logging as log
import random

import discord
from discord import app_commands
from discord.ext import commands

from src.helpers import is_connected, set_voice_client


log.getLogger(__name__)


#! TODO: Add more messages.
LIST_OF_LEAVE_MESSAGES: list = ["Bye, bye! 😔", "Damn son, I'll leave 😖"]


class Leave(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        """
        Leave command constructor, links the bot object to the class instance.
        """
        self.bot = bot

        return

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        This event listener indicates when the cog has been loaded. Really
            just used for logging purposes and is optional.
        """
        log.debug("Successfully loaded the `Leave` command cog!")

        return

    @commands.command()
    async def leave(self, ctx: commands.Context) -> None:
        """
        This command triggers Groovester to leave the voice channel that
            it's connected to.
        """

        message_obj = ctx.message
        message_author = ctx.message.author
        voice_client = ctx.voice_client

        #! TODO: Verify if user is in the same voice channel as Groovester.
        # Validate Groovester is in a voice channel.
        voice_channel = message_author.voice.channel

        if (
            voice_channel == None
        ):  # ? Is this variable None if Groovester is not in a voice channel?

            log.error("!leave failed, Groovester is not in a voice channel.")
            await ctx.send(
                "Incorrect !leave usage...\n"
                + "\tGroovester is not actively connected to a voice channel."
            )

            return

        # If connected to a voice channel, disconnect Groovester.
        if is_connected(ctx):
            try:
                set_voice_client(await voice_client.disconnect())
                log.debug(
                    f"!leave successfully disconnected from the voice channel: {voice_channel.name}",
                )

            except discord.ClientException as err:
                log.error(err)

                return

            except Exception as err:
                log.error(err)

                return

        else:
            pass  #! TODO: Send message about needing to be in same VC.

        #! TODO: Send random message
        await ctx.send(LIST_OF_LEAVE_MESSAGES[1])

        #! TODO: print the number of songs still in queue.
        # ? Or would it be better to clear the queue at this point?

        return
