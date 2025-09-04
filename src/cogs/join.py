import logging as log

import discord
from discord.ext import commands

from src.models.bot_config import get_bot, get_guild_id
from src.models.stream_thread import get_voice_client, set_voice_client


log.getLogger(__name__)


##########################################################################
##########################   COG CLASS: JOiN   ###########################
##########################################################################


class Join(commands.Cog):
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
        Command that listens for requests for the Discord bot to be
            connected to a voice channel and acts as one of two entry
            points to the join_command_logic function.

        Args:
            ctx {commands.Context): The command that triggered the event.
        """
        res: int = await join_command_logic(ctx.message.author)

        #! TODO: Allow a user parameter that enables non-ephemeral
        #!  messages.
        if res == 1:
            await ctx.send(
                "Groovester is already connected to a voice channel!",
                ephemeral=True,
            )

        elif res == 2:
            await ctx.send(
                "You are not currently connected to a voice channel!",
                ephemeral=True,
            )

        ## Send some helpful commands to the user.
        # await ctx.send(
        #     "Groovester successfully joined the voice channel!",
        #     ephemeral=True
        # )
        # await ctx.send(
        #     ("Groovester successfully joined the voice channel!"
        #     + " Here are some useful commands to get you started:\n"
        #     + "!join usage:\t!join\n"
        #     + "\tGroovester will join the voice channel that the message author is connected to.\n"
        #     + "!leave usage:\t!leave\n"
        #     + "\tGroovester will leave the voice channel it is currently connected to.\n"
        #     + "!play usage:\t!play *URL to YouTube URL*\n"
        #     + "\tGroovester will download YouTube video and play it in a voice channel.\n"),
        #     ephemeral=True
        # )

        return


##########################################################################
########################   SLASH COMMAND: JOIN   #########################
##########################################################################


@get_bot().tree.command(
    name="join",
    description="Trigger Groovester to join the voice channel you're connected to!",
    guild=get_guild_id(),
)
async def join_slash(interaction: discord.Interaction) -> None:
    """
    Slash command that listens for requests for the Discord bot to be
        connected to a voice channel and acts as one of two entry points
        to the join_command_logic function.

    Args:
        interaction {discord.Interaction): The slash command that
            triggered the event.
    """
    res: int = await join_command_logic(interaction.user)

    if res == 1:
        await interaction.response.send_message(
            "Groovester is already connected to a voice channel!",
            ephemeral=True,
        )

    elif res == 2:
        await interaction.response.send_message(
            "You are not connected to a voice channel!",
            ephemeral=True,
        )

    else:
        await interaction.response.send_message(
            "Groovester joined the voice channel! 😉",
            ephemeral=True,
        )

    return


##########################################################################
##########################   CORE LOGIC: JOIN   ##########################
##########################################################################


async def join_command_logic(requestor: discord.Member) -> int:
    """
    Function that handles the Discord API calls to join the Discord bot
        to the message author's voice channel. Both join_slash and join
        invoke this function.

    Args:
        requestor (discord.Member): The author of the request.

    Returns:
        int: Result of the join command.
        - 0: No errors when joining.
        - 1: Bot is already connected to a voice channel.
        - 2: Message author is not connected to a voice channel.
        - 3: Exception occurred when trying to connect to voice channel.
    """
    ret_val: int = 0

    # Validate message author is connected to a voice channel.
    if requestor.voice is not None:
        try:
            voice_channel = requestor.voice.channel
            if voice_channel:
                set_voice_client(await voice_channel.connect())

            log.debug(
                f"!join successfully connected to the voice channel: {voice_channel.name}"
            )

        except discord.ClientException as d_err:
            log.error(
                f'Discord client error, error occurred while trying to connect to the "{voice_channel}" voice channel: {d_err}'
            )
            ret_val = 3

        except Exception as err:
            log.error(
                f'General exception, unexpected error occurred while trying to connect to the "{voice_channel}" voice channel: {err}'
            )
            ret_val = 3

    # The bot is already connected to a voice channel.
    elif (voice_client := get_voice_client()) is not None:
        if voice_client.is_connected():
            log.error(
                "!join failed, Groovester is already connected to the voice channel."
            )
            ret_val = 1

    # Message author is not connect to a voice channel.
    else:
        log.error("!join failed, message author is not in a voice channel.")
        ret_val = 2

    return ret_val
