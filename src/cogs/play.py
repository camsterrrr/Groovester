import logging as log

import discord
from discord.ext import commands

from src.cogs.join import join_command_logic
from src.models.bot_config import get_bot, get_guild_id
from src.models.music_queue import get_music_queue
from src.models.stream_thread import get_voice_client
from src.util.helpers import download_youtube_audio, validate_url, validate_url_domain
from src.util.threads import get_thread_warden


log.getLogger(__name__)


##########################################################################
##########################   COG CLASS: PLAY   ###########################
##########################################################################


class Play(commands.Cog):
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

        Args:
            ctx {commands.Context): The command that triggered the event.
        """
        # Input validation: The command should be in the format of:
        #   '!play https://youtube.com/arbitrary/url'
        media_url: str = strip_url_from_command(ctx.message.content)

        # Attempt to download the song and add it to the queue.
        res: int = await play_command_logic(media_url, ctx.message.author)

        if res == 1:
            await ctx.send(
                "The URL you entered is invalid, please enter a valid domain!"
            )

        elif res == 2:
            await ctx.send("Groovester failed to download the requested video!")

        else:
            await ctx.send(
                "Successfully downloaded the song and added it to the queue!"
            )

        return


##########################################################################
#########################   MODAL CLASS: PLAY   ##########################
##########################################################################


class PlayModal(discord.ui.Modal, title="Enter the URL that you want played! 😁"):
    """
    Class to make a Modal window render in the Discord client. This modal
        prompts users to enter a URL.

    Args:
        discord (discord.ui.Modal): Base Modal class, must be inherited.
        title (str, optional): Title of the modal window. Defaults to
            "Enter the URL that you want played! 😁".
    """

    media_url: str = discord.ui.TextInput(
        label="Media URL",
        max_length=128,
        placeholder="https://youtube.com/arbitrary/url",
        required=True,
        style=discord.TextStyle.short,
    )

    async def on_submit(self, interaction: discord.Interaction):
        """
        Listener event that gets invoked when the user clicks the "Submit"
            button on the Modal.

        Args:
            interaction (discord.Interaction): The represents a user's
                interaction with the modal.
        """
        res: int = await play_command_logic(str(self.media_url), interaction.user)

        if res == 1:
            await interaction.response.send_message(
                "The URL you entered is invalid, please enter a valid domain!",
                ephemeral=True,
            )

        elif res == 2:
            await interaction.response.send_message(
                "Groovester failed to download the requested video!", ephemeral=True
            )

        else:
            await interaction.response.send_message(
                "Successfully downloaded the song and added it to the queue!",
                ephemeral=True,
            )

        return


##########################################################################
########################   SLASH COMMAND: PLAY   #########################
##########################################################################


@get_bot().tree.command(
    name="play",
    description="Trigger Groovester to play a song!",
    guild=get_guild_id(),
)
async def play_slash(interaction: discord.Interaction) -> None:
    """
    Slash command that listens for requests for the Discord bot to be
        disconnected from a voice channel and acts as one of two entry points
        to the leave_command_logic function.

    Args:
        interaction {discord.Interaction): The slash command that
            triggered the event.
    """
    await interaction.response.send_modal(PlayModal())

    return


##########################################################################
#########################   CORE LOGIC: PLAY   ###########################
##########################################################################


def strip_url_from_command(play_command: str) -> str:
    """
    Function that performs input validation and strips the URL the command
        requestor wants to play in the voice channel from the rest of the
        command.

    Args:
        play_command (str): The command from the requestor.

    Returns:
        str: The media URL the requestor wants to be played in the voice
            channel.
    """
    media_url: str = ""

    if play_command == "!play":
        pass

    elif (
        len(play_command) > 5 and play_command[:5] == "!play" and play_command[5] == " "
    ):
        media_url = play_command[6:]
        log.debug(f"Stripped message: {media_url}")

    return media_url


async def play_command_logic(media_url: str, requestor: discord.Member) -> int:
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

    # Test if the Domain is reachable and valid. Emphasis on Domain.
    if not validate_url_domain(media_url) or not validate_url(media_url):
        ret_val = 1
        return ret_val

    #! TODO: Add logic to limit the number of downloaded videos to ten.
    #!  Download the YouTube video.
    # Download the song via Pytube API.
    downloaded_media = download_youtube_audio(media_url, requestor)
    if downloaded_media is None:
        ret_val = 2

    # Add the song to the queue to be played in the voice channel.
    get_music_queue().add_to_queue(downloaded_media)

    # Connect the bot to the requestors voice channel if it's not already
    #   connected to one.
    if get_voice_client() is None:
        await join_command_logic(requestor)

    get_thread_warden().notify_threads()

    return ret_val
