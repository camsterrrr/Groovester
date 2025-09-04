import asyncio
import logging as log
from pathlib import Path
from threading import Thread
from time import sleep

import discord

from src.models.music_queue import get_music_queue
from src.util.file_system import remove_media_file
from src.util.threads import get_thread_warden

log.getLogger(__name__)  # Set same logging parameters as main.py.
VOICE_CLIENT: discord.VoiceClient = None


##########################################################################
############################   ENTRY POINT   #############################
##########################################################################


def main_stream_thread() -> None:
    """
    Function used to start a new thread dedicated to preparing and
        streaming songs via voice channels.
    """
    # Start various helper threads.
    start_stream_thread = Thread(target=run_stream_thread, args=())

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


async def pause_discord_audio() -> None:
    """
    Function that pauses the voice client while playing music.
    """
    try:
        log.debug(f"Attempting to pause the voice client.")

        VOICE_CLIENT.pause()
        log.info(f"Successfully paused the voice client.")

    except discord.ClientException as d_err:
        VOICE_CLIENT.stop()
        log.error(
            f"Discord client exception, error occurred while trying to pause Discord audio: {d_err}",
        )

    except Exception as err:
        VOICE_CLIENT.stop()
        log.error(
            f"General exception, unexpected error occurred while trying to pause Discord audio: {err}",
        )

    return


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
        music_queue = get_music_queue()

        with thread_warden.reader_cv:
            loop_count += 1
            log.debug(f"prepare_discord_audio loop #{loop_count}")

            # VOICE_CLIENT = get_voice_client() #? Legacy code

            try:
                # * 1. Check that there are songs in the queue.
                #! TODO: while true and replace whiles with if
                #!  statements. Otherwise, checks can be by passed.
                if len(music_queue.queue) == 0:
                    log.debug(
                        "Giving up this time slice because there are no songs in the queue."
                    )
                    thread_warden.reader_cv.wait()
                    continue

                # * 2. Check that the bot is connected to voice
                #   channel audio.
                #! TODO: User can get past this check, then crash
                #!  the program by issuing the !leave command.
                elif VOICE_CLIENT is None:
                    log.debug(
                        "Giving up this time slice because the bot's voice client has not been instantiated."
                    )
                    thread_warden.reader_cv.wait()
                    continue

                # * 3. Check that the bot is connected to voice
                # *     channel audio.
                elif not VOICE_CLIENT.is_connected():
                    log.debug(
                        "Giving up this time slice because the bot is not connected to a voice channel."
                    )
                    thread_warden.reader_cv.wait()
                    continue

                # * 4. Check if the bot is already playing a song.
                elif VOICE_CLIENT.is_playing():
                    log.debug(
                        "Giving up this time slice because the voice client is already playing a song."
                    )
                    thread_warden.reader_cv.wait()
                    continue

                # * 5. Check if there are active reader or writer
                # *     threads.
                elif thread_warden.num_readers or thread_warden.num_writers:
                    log.debug(
                        "Giving up this time slice because there is an active reader or writer thread."
                    )
                    thread_warden.reader_cv.wait()
                    continue

                else:
                    log.debug("Passed all prepare_discord_audio checks.")

                    # * Enter mutual exclusion zone.
                    thread_warden.num_readers += 1

                    # At this point, the Discord bot can safely start
                    #   playing audio.

                    # Store the next song's file path and remove it
                    #   from queue.
                    path_to_file = music_queue.play_next_in_queue().path_to_file
                    log.debug(f"Attempting to play the following media: {path_to_file}")

                    thread_warden.num_readers -= 1
                    # * End of mutual exclusion zone.

                    # Play song through the Discord voice channel.
                    log.debug("Attempting to invoke stream_discord_audio")
                    await stream_discord_audio(path_to_file)

                    #! TODO: Move this section to a worker thread that clears the
                    #!  file system of songs not in the queue.
                    # Delete the downloaded file after song ends.
                    # remove_media_file(path_to_file)
                    #! TODO: Can't delete because the file is in use.

            except Exception as err:
                log.error(
                    f"General exception, unexpected error caught while trying to {err}"
                )

    return  # This shouldn't ever be reached.


async def resume_discord_audio() -> None:
    """
    Function that resumes the voice client's audio sources from where it
        was paused.
    """
    try:
        log.debug(f"Attempting to resume the voice client.")

        VOICE_CLIENT.resume()
        log.info(f"Successfully resumed the voice client.")

    except discord.ClientException as d_err:
        VOICE_CLIENT.stop()
        log.error(
            f"Discord client exception, error occurred while trying to resume Discord audio: {d_err}",
        )

    except Exception as err:
        VOICE_CLIENT.stop()
        log.error(
            f"General exception, unexpected error occurred while trying to resume Discord audio: {err}",
        )

    return


async def stop_discord_audio() -> None:
    """
    Function that stops the voice client from playing music. This stops
        the audio source and it can't be resumed.
    """
    try:
        log.debug(f"Attempting to stop the voice client.")

        VOICE_CLIENT.stop()
        log.info(f"Successfully stopped the voice client.")

    except discord.ClientException as d_err:
        VOICE_CLIENT.stop()
        log.error(
            f"Discord client exception, error occurred while trying to stop Discord audio: {d_err}",
        )

    except Exception as err:
        VOICE_CLIENT.stop()
        log.error(
            f"General exception, unexpected error occurred while trying to stop Discord audio: {err}",
        )

    return


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
        #! TODO: Update README with instructions to install FFMPEG.
        #! TODO: I think it would be better to stream the song instead of
        #!  download it to the filesystem.

        #! TODO: User parameter to specify the path to ffmpeg.
        # ? which ffmpeg to find where stored. -> ffmpeg or ffmpeg.exe
        # Covert the .mp4 file to a raw format for streaming.
        audio_source = discord.FFmpegOpusAudio(
            executable="/usr/bin/ffmpeg", source=path_to_file
        )
        # Have the bot stream the audio to the voice channel.
        VOICE_CLIENT.play(audio_source)
        log.debug(f"Successfully streamed the audio source: {path_to_file}")

        #! TODO: Look into alternatives for this sleep function call.
        #!  Allows child thread time to open file descriptor. Maybe
        #!  signal writerCv from speakInVoiceChannel thread?
        sleep(5)

    except discord.ClientException as d_err:
        VOICE_CLIENT.stop()
        log.error(
            f"Discord client exception, error occurred while trying to play an audio source: {d_err}",
        )

        return

    except Exception as err:
        VOICE_CLIENT.stop()
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
