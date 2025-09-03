import logging as log
from threading import Condition, Lock


log.getLogger(__name__)  # Set same logging parameters as client.py.


LIMIT_OF_SONGS_TO_DOWNLOAD: int = 10


class ThreadWarden:
    """
    Maintains references to the locks that are used to control the
        execution of threads.
    """

    def __init__(self):
        self.num_readers: int = 0  # C++ style locks 😉
        self.num_writers: int = 0
        self.reader_lock: Lock = Lock()
        self.writer_lock: Lock = Lock()
        self.reader_cv: Condition = Condition(lock=self.reader_lock)
        self.writer_cv: Condition = Condition(lock=self.writer_lock)
        # self.song_queue: list[DownloadedMedia] = []

    def acquire_reader_lock(self) -> None:
        """
        Function to acquire the reader lock if there are no active readers
            or writers.
        """
        with self.reader_cv:
            while self.num_readers or self.num_writers:
                self.reader_cv.wait()
            self.num_readers += 1

        return

    def acquire_writer_lock(self) -> None:
        """
        Function to acquire the writer lock if there are no active readers
            or writers.
        """
        # Acquire the writer lock and await signal.
        with self.writer_cv:

            # Fall through, only if there are no active readers or writers.
            while self.num_readers or self.num_writers:
                self.writer_cv.wait()

            # * Enter mutual exclusion zone.
            self.num_writers += 1  # Lock

        return

    def notify_threads(self) -> None:
        """
        Function to notify any threads waiting to be signaled.
        """
        # Signal any threads waiting to run.
        with self.writer_cv:
            self.writer_cv.notify()

        with self.reader_cv:
            self.reader_cv.notify()

        return

    def release_reader_lock(self) -> None:
        """
        Function to release the reader lock and notify both reader and
            writer threads.
        """
        # * End of mutual exclusion zone.
        # Signal any threads waiting to run.
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
        # * Exit mutual exclusion zone.
        # Signal any threads waiting to run.
        with self.writer_cv:
            self.num_writers -= 1  # Unlock
            self.writer_cv.notify()

        with self.reader_cv:
            self.reader_cv.notify()

        return

    # def add_media_to_queue(self, downloaded_media: DownloadedMedia) -> None:
    #     """
    #     Function that adds media to the queue. The queue is shared among
    #         the different threads, so locks and condition variables are
    #         used to control the execution of threads.

    #     Args:
    #         downloaded_media (DownloadedMedia): Object representing media
    #             a user requested the bot to play.
    #     """
    #     # Acquire the writer lock and await signal.
    #     with THREAD_WARDEN.writer_cv:

    #         # Fall through, only if there are no active readers or writers.
    #         while THREAD_WARDEN.num_readers or THREAD_WARDEN.num_writers:
    #             THREAD_WARDEN.writer_cv.wait()

    #         # * Enter mutual exclusion zone.
    #         THREAD_WARDEN.num_writers += 1  # Lock

    #         log.info(
    #             f"Adding the following media to the song queue: {downloaded_media.path_to_file}",
    #         )
    #         THREAD_WARDEN.song_queue.append(downloaded_media)

    #         THREAD_WARDEN.num_writers -= 1  # Unlock
    #         # * Exit mutual exclusion zone.

    #         # Signal any threads waiting to run.
    #         with THREAD_WARDEN.reader_cv:
    #             THREAD_WARDEN.reader_cv.notify()
    #         THREAD_WARDEN.writer_cv.notify()

    #     return


##########################################################################
###########################   THREAD WARDEN   ############################
##########################################################################


THREAD_WARDEN: ThreadWarden = ThreadWarden()


##########################################################################
##############################   GETTERS   ###############################
##########################################################################


def get_thread_warden() -> ThreadWarden:
    """
    Function that returns a reference to the global THREAD_WARDEN variable
        to other parts of the program.

    Returns:
        ThreadWarden: Object that controls the execution of threads within
            the application.
    """
    return THREAD_WARDEN
