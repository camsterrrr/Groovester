import asyncio
import logging as log
import os
from threading import Thread

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

from src.Groovester import GroovesterEventHandler
from src.threads import playDownloadedSongViaDiscordAudio
from src.cogs.test import TestCog


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
#* Note that the command prefix was removed in recent versions. This 
#*  doesn't do anything.

load_dotenv()
guild_id = discord.Object(id=int(os.getenv("guild_id"))) # Unique identifier of the server.
bot_token = os.getenv("bot_token")

# Create instance for custom event handler.
GROOVESTER_EVENT_HANDLER = GroovesterEventHandler()


async def load_cogs() -> None: 
    """
        Function that associates each of the cog files when the 
            bot starts up. This allows for scalable/seperateable code.
    """
    try:
        for filename in os.listdir("./src/cogs"):
            truncated_filename=filename[:-3]
            if filename.endswith(".py"):
                # await bot.load_extension(f"src.cogs.{truncated_filename}")
                await bot.add_cog(TestCog(bot))
                log.debug(f"Succesffully loaded the {filename} cog.")

    except TypeError as t_err:
        log(f"Type error, failed to load the cogs: %s", t_err)
        
    except discord.ext.commands.CommandError as d_err1:
        log(f"Discord command error, failed to load the cogs: %s", d_err1)
        
    except discord.ClientException as d_err2:
        log(f"Discord client exception, failed to load the cogs: %s", d_err2)
        
    except Exception as err:
        log(f"General exception, failed to load the cogs: %s", err)

    return


async def run_discord_bot() -> None:
    """
        This function is used to instantiate an instance for the Discord 
            client.
    """
    try:
        async with bot:
            await load_cogs()
            await bot.start(bot_token)
            
    except discord.DiscordException as d_err:
        log.error(f"Discord exception, failed to run the bot: %s", d_err)
        
    except Exception as err:
        log.error(f"General exception, failed to run the bot: %s", err)

    return


def run_play_songs_in_discord_audio_thread() -> None:
    """
        Function used to start a new thread. This was needed because the
            "playDownloadedSongViaDiscordAudio" is an asynchronous 
            function.
    """
    asyncio.run(
        playDownloadedSongViaDiscordAudio(
            GROOVESTER_EVENT_HANDLER,
        )
    )
    
    return


@bot.event
async def on_ready() -> None:
    """
        Prints message when Groovester successfully starts and starts 
            helper threads.
    """

    log.info("Groovester started Successfully!")
    print("Groovester started Successfully!")

    # Start various helper threads.
    play_songs_in_discord_audio_thread = Thread(
        target=run_play_songs_in_discord_audio_thread, args=()
    )
    
    try:
        play_songs_in_discord_audio_thread.start()
    except Exception as err:
        log.error(f"General Exception, on_ready failed to spawn child thread: %s", err)
        #! TODO: Kill process when this exception is thrown.
    
    # Push offered slash commands to Discord servers.
    try:
        await bot.tree.sync(guild=guild_id)
        log.info(f"Successfully synced the slash commands with the server!")
    except Exception as err:
        log.error(f"General exception, failed to sync the slash commands with the server: %s", err)
        

    return


# @bot.tree.command(name="hello", description="say hello", guild=guild_id)
# async def hello(interaction: discord.Interaction):
#     await interaction.response.send_message("Hellow!")


# @CLIENT_OBJ.event
# async def on_message(message: discord.message.Message) -> None:
#     """
#         Function that acts as the message procedure for the application.
#             When an event occurs, Groovester will determine how to handle.
        
#         Args:
#             message: The message that triggered the message procedure.
#     """

#     # Groovester won't respond to itself.
#     if message.author == CLIENT_OBJ.user:
#         return

#     log.debug("Message received from %s: %s", message.author, message.content)
#     GROOVESTER_EVENT_HANDLER.lastChannelCommandWasEntered = message.channel

#     if message.content == "!help":
#         await message.channel.send(        
#             "!play usage:\t !play *URL to YouTube URL*\n"
#             + "\tGroovester will download YouTube video and play it in a voice channel.\n"
#         )

#     # !join, Groovester will connect to the voice channel that the user is connected to.
#     elif message.content == "!join":
#         return await GROOVESTER_EVENT_HANDLER.joinClientEvent(message)

#     # !leave, Groovester will disconnect from the voice channel it is currently connected to.
#     elif message.content == "!leave":
#         return await GROOVESTER_EVENT_HANDLER.leaveClientEvent(message)

#     # !play: Downloads video to local file system and enrolls song in queue.
#     elif message.content.startswith("!play"):
#         return await GROOVESTER_EVENT_HANDLER.playClientEvent(message)

#     elif message.content == "!stop":
#         return await GROOVESTER_EVENT_HANDLER.stopClientEvent(message.channel)

#     #! Todo: !clear, which clears the queue and deletes any downloaded videos.
#     elif message.content == "!clear":
#         pass

#     #! Todo: !next, skips to the next song and deletes the current song being played.
#     elif message.content == "!next":
#         pass

#     #! Todo: !pause, which pauses the audio the bot is playing.
#     elif message.content == "!pause":
#         pass

#     #! Todo: !queue, list the items stored in queue.
#     elif message.content == "!queue":
#         pass

#     #! Todo: !remove, removes a specific song/index from the queue.
#     elif message.content.startswith("!remove"):
#         pass

#     return
