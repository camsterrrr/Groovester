import os
import logging as log
from threading import Condition
from time import sleep

from src.constants import ClientHelpMessages, DebugMessages, ErrorMessages, InfoMessages
from src.Groovester import GroovesterEventHandler
from src.helpers import downloadYouTubeAudio

log.getLogger(__name__)  # Set same logging parameters as client.py.

LIMIT_OF_SONGS_TO_DOWNLOAD = 10


def acquireReaderLock(handler: GroovesterEventHandler):
	with handler.readerCv:
		while (  # Fall through if there are no active readers or writers.
			handler.numReaders > 0
			or handler.numWriters > 0
			or handler.listOfDownloadedSongsToPlay.size() == 0
		):
			handler.readerCv.wait()
		handler.numReaders = handler.numReaders + 1

	return True


def acquireWriterLock(handler: GroovesterEventHandler):
	# Acquire lock and await signal.
	with handler.writerCv:
		while (  # Fall through if there are no active readers or writers.
			handler.numReaders > 0 or handler.numWriters > 0
		):
			handler.writerCv.wait()
		handler.numWriters = handler.numWriters + 1

	return True


def releaseReaderLock(handler: GroovesterEventHandler):
	with handler.readerCv:
		handler.numReaders = handler.numReaders - 1
		handler.readerCv.notify()

	with handler.writerCv:
		handler.writerCv.notify()

	return True


def releaseWriterLock(handler: GroovesterEventHandler):
	with handler.writerCv:
		handler.numWriters = handler.numWriters - 1
		handler.writerCv.notify()

	with handler.readerCv:
		handler.readerCv.notify()

	return True


def checkSongsInQueueExistOnFileSystem(handler: GroovesterEventHandler):
	"""
	Thread that executes every 10 seconds and verifies the next ten
		songs exist on the local file system. If not, it downloads
		them.
	"""

	queue = handler.listOfDownloadedSongsToPlay

	# Thread should continue through the duartion of Groovester's execution.
	while True:

		# Claim reader lock and condition variable.
		acquireReaderLock(handler)

		if len(queue) < 0:

			# Scope the range of iterations for upcoming "for" loop. By default,
			# 	only download the first ten songs in queue.
			itrRange = 0
			if len(queue) < LIMIT_OF_SONGS_TO_DOWNLOAD:
				itrRange = len(queue)
			else:
				itrRange = 10

			# Iterate queue and validate songs have been downloaded to local
			# 	file system.
			for idx in range(itrRange):
				if not os.path.exists(queue[idx]):
					#! Todo: invoke download video function.
					#! Todo: Add new class to track URL and absolute file path
					#! 	on local file system.
					downloadYouTubeAudio("")

		# Unclaim reader lock and signal readers and writers.
		releaseReaderLock(handler)

		sleep(10)

	return True


# Get signaled to play audio in a Discord channel.
async def playDownloadedSongViaDiscordAudio(handler: GroovesterEventHandler):
	"""
	Thread that is used to stream audio when Groovester is in a voice channel.
		If there is no song to play, it awaits a signal from client thread.
	"""
	log.debug("%s", DebugMessages._logPlaySongsInDiscordAudioThreadStarted)

	queue = handler.listOfDownloadedSongsToPlay

	while True:

		with handler.readerCv:

			# Spin lock until various conditions are met.
			while True:
				
				# Check that there are songs in the queue.
				#! Todo: while true and replace whiles with if statements. Otherwise, checks can be by passed.
				if len(queue) == 0:
					log.debug(DebugMessages._logQueueEmpty)
					handler.readerCv.wait()
					continue

				# Check if the Voice Cleint has been instantiated.
				#! Todo: User can get past this check, then crash the program by issuing the !leave command.
				elif handler.voiceClient is None:
					log.debug(
						"%s", DebugMessages._logUninstantiatedVoiceClient
					)
					handler.readerCv.wait()
					continue

				# Check if the Voice Client is connected to a Voice Channel.
				elif not handler.voiceClient.is_connected():
					log.debug(
						"%s", DebugMessages._logInactiveVoiceClient
					)
					handler.readerCv.wait()
					continue 

				# Check if the Voice Client instance is already playing a song.
				elif handler.voiceClient.is_playing():
					log.debug(
						"%s", DebugMessages._logActiveVoiceClient
					)
					handler.readerCv.wait()
					continue

				# Fall through if there are no active readers or writers.
				elif (  
					handler.numReaders > 0 or handler.numWriters > 0
				):
					log.debug("%s", DebugMessages._logActiveReadersOrWriters)
					handler.readerCv.wait()
					continue
				else: 
					break

			handler.numReaders = handler.numReaders + 1

		# At this point, Groovester can start playing audio.

		# Store absolute path to downloaded song to play and remove it from queue.
		absPathToDownloadedVideoToPlay = queue[0].absPathToFile
		handler.listOfDownloadedSongsToPlay = queue[1:]

		releaseReaderLock(handler)

		# Play song through the Discord voice channel.
		await handler.speakInVoiceChannel(absPathToDownloadedVideoToPlay)
		sleep(1) #! Todo: Look into alternatives for this sleep function call. Allows child thread time to open file descriptor. Maybe signal writerCv from speakInVoiceChannel thread?

		# Delete the downloaded file after song ends.
		if os.path.exists(absPathToDownloadedVideoToPlay):
			try:
				os.remove(absPathToDownloadedVideoToPlay)
				log.debug(
					"%s %s", DebugMessages._logRemovedFileFromFileSystem, absPathToDownloadedVideoToPlay
				)
			except OSError as err:
				log.error(
					"%s %s", ErrorMessages._exceptionUnableToRemoveFileFromFileSystem, err
				)
				return False

	return True
