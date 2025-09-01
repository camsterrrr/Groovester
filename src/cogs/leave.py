import logging as log

import discord
from discord.ext import commands

from src.models.bot_config import get_bot, get_guild_id
from src.models.stream_thread import get_voice_client, set_voice_client


log.getLogger(__name__)


#! TODO: Add more messages and send a random messages when leaving the
#!  voice channel.
LIST_OF_LEAVE_MESSAGES: list = ["Bye, bye! 😔", "Damn son, I'll leave 😖"]


##########################################################################
##########################   COG CLASS: LEAVE   ##########################
##########################################################################


class Leave(commands.Cog):
    """
    Cog class for better command organization. A cog is a collection of
        commands, listeners, and optional state to help group commands
        together.

    Args:
        commands (commands.Cog): The base class that all cogs must inherit
            from.
    """

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
        Command that listens for requests for the Discord bot to be
            disconnected from a voice channel and acts as one of two entry
            points to the leave_command_logic function.

        Args:
            interaction {commands.Context): The command that triggered the
                event.
        """
        res: int = await leave_command_logic(ctx.message.author)

        if res == 1:
            await ctx.send("Groovester is not connected to a voice channel!")

        elif res == 2:
            await ctx.send(
                "You must be connected to the same voice channel as Groovester to request it to disconnect."
            )

        else:
            await ctx.send("Groovester left the voice channel! 😔")

        #! TODO: print the number of songs still in queue.
        # ? Or would it be better to clear the queue at this point?

        return


##########################################################################
#######################   SLASH COMMAND: LEAVE   #########################
##########################################################################


@get_bot().tree.command(
    name="leave",
    description="Trigger Groovester to leave the voice channel its connected to!",
    guild=get_guild_id(),
)
async def leave_slash(interaction: discord.Interaction) -> None:
    """
    Slash command that listens for requests for the Discord bot to be
        disconnected from a voice channel and acts as one of two entry points
        to the leave_command_logic function.

    Args:
        interaction {discord.Interaction): The slash command that
            triggered the event.
    """
    res: int = await leave_command_logic(interaction.user)

    if res == 1:
        await interaction.response.send_message(
            "Groovester is not connected to a voice channel!",
            ephemeral=True,
        )

    elif res == 2:
        await interaction.response.send_message(
            "You must be connected to the same voice channel as Groovester to request it to disconnect.",
            ephemeral=True,
        )

    else:
        await interaction.response.send_message(
            "Groovester left the voice channel! 😔",
            ephemeral=True,
        )

    return


##########################################################################
#########################   CORE LOGIC: LEAVE   ##########################
##########################################################################


async def leave_command_logic(requestor: discord.Member) -> int:
    """
    Function that handles the Discord API calls to disconnect the Discord
        bot from the voice channel its connected to. Both leave_slash and
        leave invoke this function.

    Args:
        requestor (discord.Member): The author of the request.

    Returns:
        int: Result of the leave command.
        - 0: No errors when leaving.
        - 1: Bot is not connected to a voice channel.
        - 2: Message author is not connected to the same voice channel as
            the bot.
        - 3: Exception occurred when trying to disconnect to voice
            channel.
    """
    ret_val: int = 0
    voice_client: discord.VoiceClient | None = get_voice_client()

    # Disconnect the bot from the voice channel its connected to.
    if voice_client is not None:
        # Verify that the bot is connected to a voice channel.
        if voice_client.is_connected():

            # Verify that the requestor and the bot are in the same voice
            #   channel.
            if voice_client.channel.name == requestor.voice.channel.name:
                try:
                    set_voice_client(await voice_client.disconnect())
                    log.debug(
                        f"!leave successfully disconnected from the voice channel: {voice_client.channel.name}",
                    )

                except discord.ClientException as d_err:
                    log.error(
                        f'Discord client error, error occurred while trying to disconnect from the "{voice_client.channel.name}" voice channel: {d_err}'
                    )
                    ret_val = 3

                except Exception as err:
                    log.error(
                        f'General exception, unexpected error occurred while trying to connect to the "{voice_client.channel.name}" voice channel: {err}'
                    )
                    ret_val = 3

            else:
                log.error(
                    "!leave failed, requestor is not connected to the same voice channel as the bot."
                )
                ret_val = 2

        # This shouldn't be reached, if the bot is not connected to a
        #   voice channel the voice_client object will be None.
        else:
            log.error("!leave failed, Groovester is not in a voice channel.")
            ret_val = 1

    else:
        log.error("!leave failed, Groovester is not in a voice channel.")
        ret_val = 1

    return ret_val
