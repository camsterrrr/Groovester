import logging as log

import discord
from discord.ext import commands

from src.models.bot_config import get_bot, get_guild_id
from src.models.stream_thread import (
    get_voice_client,
    pause_discord_audio,
)


log.getLogger(__name__)


##########################################################################
##########################   COG CLASS: PAUSE   ##########################
##########################################################################


class Pause(commands.Cog):
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
        Pause command constructor, links the bot object to the class instance.
        """
        self.bot = bot

        return

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        This event listener indicates when the cog has been loaded. Really
            just used for logging purposes and is optional.
        """
        log.debug("Successfully loaded the `Pause` command cog!")

        return

    @commands.command()
    async def pause(self, ctx: commands.Context) -> None:
        """
        This command triggers the bot to pause the audio source it's
            streaming to the voice channel.

        Args:
            ctx {commands.Context): The command that triggered the event.
        """
        res: int = await pause_command_logic(ctx.message.author)

        if res == 1:
            await ctx.send(
                "Groovester is not connected to a voice channel!",
                ephemeral=True,
            )

        elif res == 2:
            await ctx.send(
                (
                    "You must be connected to the same voice channel as "
                    "Groovester to request it to pause."
                ),
                ephemeral=True,
            )

        return


##########################################################################
########################   SLASH COMMAND: PAUSE   ########################
##########################################################################


@get_bot().tree.command(
    name="pause",
    description="Trigger Groovester to pause the song it's currently streaming!",
    guild=get_guild_id(),
)
async def pause_slash(interaction: discord.Interaction) -> None:
    """
    Slash command that listens for requests for the Discord bot to be
        disconnected from a voice channel and acts as one of two entry
        points to the leave_command_logic function.

    Args:
        interaction {discord.Interaction): The slash command that
            triggered the event.
    """
    res: int = await pause_command_logic(interaction.user)

    if res == 1:
        await interaction.response.send_message(
            "Groovester is not connected to a voice channel!",
            ephemeral=True,
        )

    elif res == 2:
        await interaction.response.send_message(
            "You must be connected to the same voice channel as Groovester to request it to stop.",
            ephemeral=True,
        )

    else:
        await interaction.response.send_message(
            ephemeral=True,
        )

    return


##########################################################################
#########################   CORE LOGIC: PAUSE   ##########################
##########################################################################


async def pause_command_logic(requestor: discord.Member) -> int:
    """
    Function that handles the Discord API calls to pause the audio source
        the bot is streaming. Both pause_slash and pause invoke this
        function.

    Args:
        requestor (discord.Member): The author of the request.

    Returns:
        int: Result of the stop command.
        - 0: No errors when leaving.
        - 1: Bot is not connected to a voice channel.
        - 2: Message author is not connected to the same voice channel as
            the bot.
        - 3: Exception occurred when trying to pause the audio stream.
    """
    ret_val: int = 0
    voice_client: discord.VoiceClient = get_voice_client()

    if voice_client is None:
        return 1

    if not voice_client.is_connected():
        return 1

    if not voice_client.channel.name == requestor.voice.channel.name:
        return 2

    try:
        await pause_discord_audio()
        log.debug(
            "!pause successfully paused the audio stream.",
        )

    except discord.ClientException as d_err:
        log.error(
            (
                f"Discord client error, error occurred while trying to "
                f"pause the audio source: {d_err}"
            )
        )
        ret_val = 3

    except Exception as err:
        log.error(
            (
                f"General exception, unexpected error occurred while "
                f"trying to pause the audio source: {err}"
            )
        )
        ret_val = 3

    return ret_val
