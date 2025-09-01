import logging as log
import os
from pathlib import Path
from time import sleep

from src.util.file_system import file_in_use
from src.util.helpers import DownloadedMedia
from src.util.threads import get_thread_warden


log.getLogger(__name__)  # Set same logging parameters as main.py.


##########################################################################
#######################   CORE MUSIC  QUEUE LOGIC  #######################
##########################################################################


class MusicQueue():
    """
    Maintains references to the music queue used by the application.
    """
    
    def __init__(self):
        self.queue: list[DownloadedMedia] = []


    def add_to_queue(
        self,
        downloaded_media: DownloadedMedia
    ) -> None:
        """
        Function that adds media to the music queue. The queue is shared among
            the different threads, so locks and condition variables are used 
            to control the execution of threads.

        Args:
            downloaded_media (DownloadedMedia): Object representing media a
                user requested the bot to play.
        """
        # * Enter mutual exclusion zone.
        thread_warden = get_thread_warden()
        thread_warden.acquire_writer_lock()

        log.info(
            f"Adding the following media to the song queue: {downloaded_media.path_to_file}",
        )
        self.queue.append(downloaded_media)
            
        # * Exit mutual exclusion zone.
        thread_warden.release_writer_lock()

        return
    
    
    def play_next_in_queue(self) -> DownloadedMedia:
        """
        Function that pops the heads of the queue and returns the object
            removed.

        Returns:
            DownloadedMedia: 
        """

        return self.song_queue.pop()


    #! TODO: This function doesn't actually check the queue yet...
    def delete_song_in_queue(self):
        """
        Thread that executes every 10 seconds and verifies that any
            song on the file system exists in the queue. If not, it
            will delete the file because it is presumably no longer
            needed.
        """
        cwd = os.getcwd()

        while True:
            list_dir = os.listdir()

            if len(list_dir) == 0:
                return

            for list_item in list_dir:
                path_to_list_item = Path(cwd + list_item)

                # Check that the file exists and check that its not in use
                #   before deleting it.
                if os.path.exists(path_to_list_item):
                    if file_in_use(path_to_list_item):
                        try:
                            os.remove(path_to_list_item)
                            log.debug(
                                f"Successfully removed the following song from the file system: {path_to_list_item}",
                            )

                        except OSError as os_err:
                            log.error(
                                f"OS exception, error occurred while trying to delete a song: {os_err}"
                            )

                            continue

                        except Exception as err:
                            log.error(
                                f"General exception, unexpected error occurred while trying to delete a song: {err}"
                            )

                            continue

            #! Todo: Create another synchronization variable to signal
            #!  when this thread can run.
            sleep(10)

        return


    # def queued_songs_are_exist(self):
    #     """
    #     Thread that executes every 10 seconds and verifies the next ten
    #         songs exist on the local file system. If not, it downloads
    #         them.
    #     """
    #     # Thread should continue through the duration of Groovester's execution.
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


##########################################################################
############################   MUSIC QUEUE   #############################
##########################################################################


MUSIC_QUEUE: MusicQueue = MusicQueue()


##########################################################################
##############################   GETTERS   ###############################
##########################################################################


def get_music_queue() -> MusicQueue:
    """
    Function that returns a reference to the global MUSIC_QUEUE object.

    Returns:
        MusicQueue: Object that maintains references to the songs that
            users have requested.
    """
    return MUSIC_QUEUE
