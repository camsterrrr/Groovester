import asyncio
import logging as log
import os
from threading import Thread

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

from src.cogs.join import Join
from src.cogs.leave import Leave
from src.cogs.play import Play
from src.cogs.test import TestCog
from src.models.bot_config import get_bot, get_bot_token, get_guild_id
from src.util.threads import get_thread_warden
from src.models.stream_thread import main_stream_thread


##########################################################################
#########################  APPLICATION SETUP   ###########################
##########################################################################


async def load_cogs(bot: commands.Bot, guild_id: discord.Object) -> None:
    """
    Function that associates each of the cog files when the bot starts up.
        This allows for scalable/seperateable code.
    Note that if a cog is added, remember to load it within this function.
    """
    try:
        # await bot.load_extension(f"src.cogs.test")

        # * {guild_id} is user-defined.
        await bot.add_cog(Join(bot), guilds=[guild_id])
        await bot.add_cog(Leave(bot), guilds=[guild_id])
        await bot.add_cog(Play(bot), guilds=[guild_id])
        await bot.add_cog(TestCog(bot), guilds=[guild_id])

        log.debug(f"Succesffully loaded the cogs!")

    except TypeError as t_err:
        log(f"Type error, failed to load the cogs: %s", t_err)

    except discord.ext.commands.CommandError as d_err1:
        log(f"Discord command error, failed to load the cogs: %s", d_err1)

    except discord.ClientException as d_err2:
        log(f"Discord client exception, failed to load the cogs: %s", d_err2)

    except Exception as err:
        log(f"General exception, failed to load the cogs: %s", err)

    return


async def main_bot() -> None:
    """
    Function acts as the entry point for the Discord bot and is used to
        instantiate (start) the bot instance.
    """
    try:
        bot = get_bot()
        bot_token = get_bot_token()
        guild_id = get_guild_id()

        async with bot:
            await load_cogs(bot, guild_id)
            # * {bot_token} is user-defined.
            await bot.start(bot_token)

    except discord.DiscordException as d_err:
        log.error(f"Discord exception, failed to run the bot: %s", d_err)

    except Exception as err:
        log.error(f"General exception, failed to run the bot: %s", err)

    return


##########################################################################
##########################   EVENT LISTENERS   ###########################
##########################################################################


@get_bot().event
async def on_ready() -> None:
    """
    Prints message when the Discord bot successfully runs and triggers
        various helper threads.
    """
    log.info("Groovester started Successfully!")
    print("Groovester started Successfully!")

    # Run worker threads.
    main_stream_thread()

    # # Start various helper threads.
    # play_songs_in_discord_audio_thread = Thread(
    #     target=run_discord_audio_thread, args=()
    # )

    # try:
    #     play_songs_in_discord_audio_thread.start()

    # except Exception as err:
    #     log.error(f"General Exception, on_ready failed to spawn child thread: {err}")
    #     #! TODO: Kill process when this exception is thrown.

    #! TODO: Remove because Discord.py doesn't support slash commands with
    #!  cog structure.
    # # Push offered slash commands to Discord servers.
    # try:
    #     await bot.tree.sync(guild=guild_id)
    #     log.info(f"Successfully synced the slash commands with the server!")

    # except Exception as err:
    #     log.error(
    #         f"General exception, failed to sync the slash commands with the server: {err}"
    #     )

    return
