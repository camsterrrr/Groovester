import asyncio
import logging as log
import os
from threading import Thread

import discord
from dotenv import load_dotenv

from src.constants import ClientHelpMessages, DebugMessages, ErrorMessages, InfoMessages
from src.Groovester import GroovesterEventHandler
from src.threads import playDownloadedSongViaDiscordAudio


# Create Discord's client connection object.
intents = discord.Intents.default()
intents.message_content = True
CLIENT_OBJ = discord.Client(intents=intents)

# Create instance for custom event handler.
GROOVESTER_EVENT_HANDLER = GroovesterEventHandler()


def create_discord_client_instance() -> discord.Client:
    """
        This function is used to instantiate an instance for the Discord 
            client.

    Returns:
        Client: Object that represents the applications connection to
            Discord, and is used interact with various web APIs.
    """
    
    if CLIENT_OBJ:
        # Retrieve Groovester's API token from the .env file located somewhere in the
        #   project directory.
        load_dotenv()
        CLIENT_OBJ.run(os.getenv("botToken"))
    else: 
        log.warn("Discord Client object has not been instantiated! Check logic if this occurs...")
    
    return CLIENT_OBJ

def runPlaySongsInDiscordAudioThread() -> None:
    """
    Function used to start a new thread. This was needed because the
        "playDownloadedSongViaDiscordAudio" is asynchronous.
    """
    asyncio.run(
        playDownloadedSongViaDiscordAudio(
            GROOVESTER_EVENT_HANDLER,
        )
    )


@CLIENT_OBJ.event
async def on_ready() -> None:
    """
        Prints message when Groovester successfully starts and starts 
            helper threads.
    """

    log.info("%s", InfoMessages._logGroovesterStartedSuccessfully)
    print(InfoMessages._logGroovesterStartedSuccessfully)

    # Start various helper threads.
    playSongsInDiscordAudioThread = Thread(
        target=runPlaySongsInDiscordAudioThread, args=()
    )
    try:
        playSongsInDiscordAudioThread.start()
    except Exception as err:
        log.error("%s %s", ErrorMessages._exceptionOnReadyChildThread, err)
        #! TODO: Kill process when this exception is thrown.

    return True


@CLIENT_OBJ.event
async def on_message(message: discord.message.Message) -> None:
    """
        Function that acts as the message procedure for the application.
            When an event occurs, Groovester will determine how to handle.
        
        Args:
            message: The message that triggered the message procedure.
    """

    # Groovester won't respond to itself.
    if message.author == CLIENT_OBJ.user:
        return

    log.debug("Message received from %s: %s", message.author, message.content)
    GROOVESTER_EVENT_HANDLER.lastChannelCommandWasEntered = message.channel

    if message.content == "!help":
        await message.channel.send(ClientMessages._helpPlayCmd)

    # !join, Groovester will connect to the voice channel that the user is connected to.
    elif message.content == "!join":
        return await GROOVESTER_EVENT_HANDLER.joinClientEvent(message)

    # !leave, Groovester will disconnect from the voice channel it is currently connected to.
    elif message.content == "!leave":
        return await GROOVESTER_EVENT_HANDLER.leaveClientEvent(message)

    # !play: Downloads video to local file system and enrolls song in queue.
    elif message.content.startswith("!play"):
        return await GROOVESTER_EVENT_HANDLER.playClientEvent(message)

    elif message.content == "!stop":
        return await GROOVESTER_EVENT_HANDLER.stopClientEvent(message.channel)

    #! Todo: !clear, which clears the queue and deletes any downloaded videos.
    elif message.content == "!clear":
        pass

    #! Todo: !next, skips to the next song and deletes the current song being played.
    elif message.content == "!next":
        pass

    #! Todo: !pause, which pauses the audio the bot is playing.
    elif message.content == "!pause":
        pass

    #! Todo: !queue, list the items stored in queue.
    elif message.content == "!queue":
        pass

    #! Todo: !remove, removes a specific song/index from the queue.
    elif message.content.startswith("!remove"):
        pass

    return
