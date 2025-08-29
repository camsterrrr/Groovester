import asyncio
import logging as log
from pathlib import Path
from threading import Thread
from time import sleep

import discord

from src.util.helpers import remove_media_file
from src.util.threads import get_thread_warden

log.getLogger(__name__)  # Set same logging parameters as main.py.
voice_client: discord.VoiceClient = None


##########################################################################
############################   ENTRY POINT   #############################
##########################################################################


def main_stream_thread() -> None:
    """
    Function used to start a new thread dedicated to preparing and
        streaming songs via voice channels.
    """
    # Start various helper threads.
    start_stream_thread = Thread(
        target=run_stream_thread, args=()
    )

    try:
        start_stream_thread.start()

    except Exception as err:
        log.error(f"General Exception, on_ready failed to spawn child thread: {err}")
        #! TODO: Kill process when this exception is thrown.
        #! TODO: The reason this function is needed, is because on_ready
        #!  uses Thread class, which can't run asynchronous functions.
        #!  See if asyncio can resolve this and remove this function.

    return


def run_stream_thread() -> None:
    """
    Function used to start a new thread dedicated to preparing and
        streaming songs via voice channels.
    """
    #! TODO: The reason this function is needed, is because on_ready
    #!  uses Thread class, which can't run asynchronous functions.
    #!  See if asyncio can resolve this and remove this function.
    asyncio.run(prepare_discord_audio())

    return


##########################################################################
######################   CORE APPLICATION LOGIC   ########################
##########################################################################


# Get signaled to play audio in a Discord channel.
async def prepare_discord_audio():
    """
    Thread that is used to stream audio when Groovester is in a voice channel.
        If there is no song to play, it awaits a signal from client thread.
    """
    # This thread will spin forever. It will only stream audio
    #   when various conditions are met.
    loop_count: int = 0
    while True:
        thread_warden = get_thread_warden()
        with thread_warden.reader_cv:

            loop_count += 1
            log.debug(f"prepare_discord_audio loop #{loop_count}")

            # voice_client = get_voice_client() #? Legacy code

            try:
                # * 1. Check that there are songs in the queue.
                #! Todo: while true and replace whiles with if
                #!  statements. Otherwise, checks can be by passed.
                if len(thread_warden.song_queue) == 0:
                    log.debug(
                        "Giving up this time slice because there are no songs in the queue."
                    )
                    thread_warden.reader_cv.wait()
                    continue

                # * 2. Check that the bot is connected to voice
                #   channel audio.
                #! Todo: User can get past this check, then crash
                #!  the program by issuing the !leave command.
                elif voice_client == None:
                    log.debug(
                        "Giving up this time slice because the bot's voice client has not been instantiated."
                    )
                    self.reader_cv.wait()
                    continue

                # * 3. Check that the bot is connected to voice
                #   channel audio.
                elif not voice_client.is_connected():
                    log.debug(
                        "Giving up this time slice because the bot is not connected to a voice channel."
                    )
                    thread_warden.reader_cv.wait()
                    continue

                # * 4. Check if the bot is already playing a song.
                elif voice_client.is_playing():
                    log.debug(
                        "Giving up this time slice because the voice client is already playing a song."
                    )
                    thread_warden.reader_cv.wait()
                    continue

                # * 5. Check if there are active reader or writer
                #   threads.
                elif thread_warden.num_readers or thread_warden.num_writers:
                    log.debug(
                        "Giving up this time slice because there is an active an reader or writer thread."
                    )
                    thread_warden.reader_cv.wait()
                    continue

                else:
                    log.debug("Passed all prepare_discord_audio checks.")
                    # * Enter mutual exlcusion zone.
                    thread_warden.num_readers += 1

                    # At this point, the Discord bot can safely start
                    #   playing audio.

                    # Store the next song's file path and remove it
                    #   from queue.
                    path_to_file = thread_warden.song_queue.pop().path_to_file
                    log.debug(f"Attempting to play the following media: {path_to_file}")

                    thread_warden.num_readers -= 1
                    # * End of mutual exlcusion zone.

                    # Play song through the Discord voice channel.
                    log.debug("Attempting to invoke stream_discord_audio")
                    await stream_discord_audio(path_to_file)
                    #! TODO: Look into alternatives for this sleep function call.
                    #!  Allows child thread time to open file descriptor. Maybe
                    #!  signal writerCv from speakInVoiceChannel thread?
                    sleep(5)

                    #! TODO: Move this section to a worker thread that clears the
                    #!  file system of songs not in the queue.
                    # Delete the downloaded file after song ends.
                    remove_media_file(path_to_file)

            except Exception as err:
                log.error("General exception, unexpected error caught while trying to ")

    return  # This shouldn't ever be reached.


async def stream_discord_audio(path_to_file: Path) -> None:
    """
    Function used to stream raw data to the Discord voice channel via
        the Discord bot.

    Args:
        path_to_file (Path): Path to media that user's want to stream
            to the Discord voice channel.
    """
    log.debug("stream_discord_audio has been invoked.")

    # voice_client = get_voice_client() #? Legacy code

    try:
        log.debug(f"Attempting to play audio source: {path_to_file}")

        # await self.lastChannelCommandWasEntered.send("Let's play some audio!")
        # ffmpegKwargs = { # Optimized settings for ffmpeg for audio streaming, https://stackoverflow.com/questions/75493436/why-is-the-ffmpeg-process-in-discordpy-terminating-without-playing-anything
        # #   'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        #   'options': '-vn -filter:a "volume=0.75"'
        # }
        #! TODO: Optimize settings for audio streaming.
        #! TODO: This works on linux, but what about Windows?
        #! TODO: Update README with insturcitons to install FFMPEG.
        #! TODO: I think it would be better to stream the song instead of
        #!  download it to the filesystem.

        # Covert the .mp4 file to a raw format for streaming.
        audio_source = discord.FFmpegOpusAudio(
            executable="/usr/bin/ffmpeg", source=path_to_file
        )
        # Have the bot stream the audio to the voice channel.
        voice_client.play(audio_source)
        log.debug(f"Successfully streamed the audio source: {path_to_file}")

    except discord.ClientException as d_err:
        voice_client.stop()
        log.error(
            f"Discord client exception, error occurred while trying to play an audio source: {d_err}",
        )

        return

    except Exception as err:
        voice_client.stop()
        log.error(
            f"General exception, unexpected error occurred while trying to play an audio source: {err}",
        )

        return

    return


##########################################################################
##############################   GETTERS   ###############################
##########################################################################


def get_voice_client() -> discord.VoiceClient:
    """
    Function that returns a reference to the global VOICE_CLIENT variable
        to other parts of the program.

    Returns:
        discord.VoiceClient: Object representing the state of the Discord
            bot's voice client capabilities.
    """
    return VOICE_CLIENT


##########################################################################
##############################   SETTERS   ###############################
##########################################################################


def set_voice_client(voice_client_operation: discord.VoiceClient) -> None:
    """
    Function that sets the voice channel global variable as the Discord
        bot is connected and disconnected from voice channels.

    Args:
        voice_client_operation (discord.VoiceClient): Represents the
            object returned after calling voice_channel.connect() or
            voice_channel.disconnect().
    """
    global VOICE_CLIENT
    VOICE_CLIENT = voice_client_operation

    return
