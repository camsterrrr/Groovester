import os
import logging as log
from pathlib import Path
from threading import Condition, Lock
from time import sleep

import discord

from src.constants import ClientHelpMessages, DebugMessages, ErrorMessages, InfoMessages
from src.Groovester import GroovesterEventHandler
from src.helpers import download_youtube_audio, file_in_use, VOICE_CLIENT

log.getLogger(__name__)  # Set same logging parameters as client.py.


LIMIT_OF_SONGS_TO_DOWNLOAD = 10


class ThreadWarden:
    """
    Maintains references to the locks that are used to control the
        execution of threads.
    """

    def __init__(self):
        self.num_readers = 0  # C++ style locks 😉
        self.num_writers = 0
        self.reader_lock = Lock()
        self.writer_lock = Lock()
        self.reader_cv = Condition(lock=self.reader_lock)
        self.writer_cv = Condition(lock=self.writer_lock)

        self.song_queue = []

    def acquire_reader_lock(self) -> None:
        """
        Function to acquire the reader lock if there are no active readers
            or writers.
        """
        with self.reader_cv:
            while self.num_readers or self.num_writers or self.song_queue.size() == 0:
                self.reader_cv.wait()
            self.num_readers += 1

        return

    def acquire_writer_lock(self) -> None:
        """
        Function to acquire the writer lock if there are no active readers
            or writers.
        """
        with self.writer_cv:
            while self.num_readers or self.num_writers:
                self.writer_cv.wait()
            self.num_writers += 1

        return

    def release_reader_lock(self) -> None:
        """
        Function to release the reader lock and notify both reader and
            writer threads.
        """
        with self.reader_cv:
            self.num_readers -= 1
            self.reader_cv.notify()

        with self.writer_cv:
            self.writer_cv.notify()

        return

    def release_writer_lock(self) -> None:
        """
        Function to release the writer lock and notify both reader and
            writer threads.
        """
        with self.writer_cv:
            self.num_writers -= 1
            self.writer_cv.notify()

        with self.reader_cv:
            self.reader_cv.notify()

        return

    # Get signaled to play audio in a Discord channel.

    async def prepare_discord_audio(self):
        """
        Thread that is used to stream audio when Groovester is in a voice channel.
            If there is no song to play, it awaits a signal from client thread.
        """
        log.debug("stream_discord_audio has been invoked")

        while True:

            with self.reader_cv:

                # This thread will spin forever. It will only stream audio
                #   when various conditions are met.
                while True:

                    # * 1. Check that there are songs in the queue.
                    #! Todo: while true and replace whiles with if
                    #!  statements. Otherwise, checks can be by passed.
                    if len(self.song_queue) == 0:
                        log.debug(DebugMessages._logQueueEmpty)
                        self.reader_cv.wait()
                        continue

                    # * 2. Check that the bot is connected to voice
                    #   channel audio.
                    #! Todo: User can get past this check, then crash
                    #!  the program by issuing the !leave command.
                    elif VOICE_CLIENT is None:
                        log.debug(
                            "Giving up this time slice because the bot's voice client has not been instantiated."
                        )
                        self.reader_cv.wait()
                        continue

                    # * 3. Check that the bot is connected to voice
                    #   channel audio.
                    elif not VOICE_CLIENT.is_connected():
                        log.debug(
                            "Giving up this time slice because the bot is not connected to a voice channel."
                        )
                        self.reader_cv.wait()
                        continue

                    # * 4. Check if the bot is already playing a song.
                    elif VOICE_CLIENT.is_playing():
                        log.debug(
                            "Giving up this time slice because the voice client is already playing a song."
                        )
                        self.reader_cv.wait()
                        continue

                    # * 5. Check if there are active reader or writer
                    #   threads.
                    elif self.num_readers or self.num_writers:
                        log.debug(
                            "Giving up this time slice because there is an active an reader or writer thread."
                        )
                        self.reader_cv.wait()
                        continue

                    else:
                        break

                # * Enter mutual exlcusion zone.
                self.num_readers += 1

                # At this point, Groovester can start playing audio.

                # Store the song's file path and remove it from queue.
                path_to_file = self.song_queue[0].path_to_file
                self.song_queue = self.song_queue[1:]

                self.release_reader_lock()
                # * End of mutual exlcusion zone.

            # Play song through the Discord voice channel.
            await self.stream_discord_sudio(path_to_file)
            #! TODO: Look into alternatives for this sleep function call.
            #!  Allows child thread time to open file descriptor. Maybe
            #!  signal writerCv from speakInVoiceChannel thread?
            sleep(5)

            #! TODO: Move this section to a worker thread that clears the
            #!  file system of songs not in the queue.
            # Delete the downloaded file after song ends.
            if os.path.exists(path_to_file):
                try:
                    os.remove(path_to_file)
                    log.debug(
                        f"Successfully removed the following file from the file system: {path_to_file}"
                    )
                except OSError as os_err:
                    log.error(
                        f"OS exception, error occurred while trying to delete the audio file from the file system: {os_err}"
                    )

                    return

        return

    #! TODO: I think it would be better to stream the song instead of
    #!  download it to the filesystem.
    async def stream_discord_sudio(self, path_to_file: Path):
        """Function used to allow Groovester to stream audio to the voice channel."""

        # await self.lastChannelCommandWasEntered.send("Let's play some audio!")
        # ffmpegKwargs = { # Optimized settings for ffmpeg for audio streaming, https://stackoverflow.com/questions/75493436/why-is-the-ffmpeg-process-in-discordpy-terminating-without-playing-anything
        # #   'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        #   'options': '-vn -filter:a "volume=0.75"'
        # }
        #! Todo: Optimize settings for audio streaming.
        #! Todo: This works on linux, but what about Windows?
        #! Todo: Update README with insturcitons to install FFMPEG.
        audio_source = discord.FFmpegOpusAudio(
            executable="/usr/bin/ffmpeg", source=path_to_file
        )

        # Check that bot is in voice channel.
        if not VOICE_CLIENT.is_connected():
            log.error(
                "Failed to play audio because the bot has not connected to a voice channel yet."
            )

            return

        # Check if the bot is already playing a song.
        if VOICE_CLIENT.is_playing():
            log.error("Failed to play audio because the bot is already playing audio!")

            return

        try:
            log.debug(f"Attempting to play audio source: {path_to_file}")
            VOICE_CLIENT.play(audio_source)
            log.debug(f"Successfully streaming an audio source: {path_to_file}")

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

    # def queued_songs_are_exist(self):
    #     """
    #     Thread that executes every 10 seconds and verifies the next ten
    #         songs exist on the local file system. If not, it downloads
    #         them.
    #     """
    #     # Thread should continue through the duartion of Groovester's execution.
    #     while True:

    #         # Claim reader lock and condition variable.
    #         self.acquire_reader_lock()

    #         if len(self.song_queue):
    #             # Scope the range of iterations for upcoming "for" loop. By default,
    #             #     only download the first ten songs in queue.
    #             itrRange = 0
    #             if len(self.song_queue) < LIMIT_OF_SONGS_TO_DOWNLOAD:
    #                 itrRange = len(self.song_queue)

    #             else:
    #                 itrRange = 10

    #             # Iterate queue and validate songs have been downloaded to local
    #             #     file system.
    #             for idx in range(itrRange):
    #                 if not os.path.exists(self.song_queue[idx]):
    #                     #! TODO: invoke download video function.
    #                     #! TODO: Add new class to track URL and absolute file
    #                     #!  path on local file system.
    #                     download_youtube_audio("")

    #         # Unclaim reader lock and signal readers and writers.
    #         self.release_reader_lock()

    #         sleep(10)

    #     return

    # #! TODO: This function doesn't actually check the queue yet...
    # def delete_songs(self):
    #     """
    #     Thread that executes every 10 seconds and verifies that any
    #         song on the file system exists in the queue. If not, it
    #         will delete the file because it is presumably no longer
    #         needed.
    #     """
    #     cwd = os.getcwd()

    #     while True:
    #         list_dir = os.listdir()

    #         if len(list_dir) == 0:
    #             return

    #         for list_item in list_dir:
    #             path_to_list_item = Path(cwd + list_item)

    #             # Check that the file exists and check that its not in use
    #             #   before deleting it.
    #             if os.path.exists(path_to_list_item):
    #                 if file_in_use(path_to_list_item):
    #                     try:
    #                         os.remove(path_to_list_item)
    #                         log.debug(
    #                             f"Successfully removed the following song from the file system: {path_to_list_item}",
    #                         )

    #                     except OSError as os_err:
    #                         log.error(
    #                             f"OS exception, error occured while trying to delete a song: {os_err}"
    #                         )

    #                         continue

    #                     except Exception as err:
    #                         log.error(
    #                             f"General exception, unexpected error occured while trying to delete a song: {err}"
    #                         )

    #                         continue

    #         #! Todo: Create another synchronization variable to signal
    #         #!  when this thread can run.
    #         sleep(10)

    #     return
