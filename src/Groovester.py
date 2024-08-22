import logging as log
from threading import Condition, Lock

import discord
from validators import url

from src.constants import ClientHelpMessages, DebugMessages, ErrorMessages, InfoMessages
from src.helpers import downloadYouTubeAudio, PyTube

log.getLogger(__name__)  # Set same logging parameters as client.py.


class GroovesterEventHandler:

	def __init__(self):

		# List to store absolute path of audio files to play.
		self.listOfDownloadedSongsToPlay = []

		# Synchronization variables.
		# Either one reader or one writer at a time.
		self.numReaders = 0
		self.numWriters = 0
		self._readerLock = (
			Lock()
		)  # Used when the Discord bot will load next song to local variable.
		self._writerLock = Lock()  # Used when commands like "!play" are issued.
		self.readerCv = Condition(lock=self._readerLock)
		self.writerCv = Condition(lock=self._writerLock)

		self.audioSource = None
		self.voiceClient = None

		self.lastChannelCommandWasEntered = None

	async def joinClientEvent(self, message):
		"""Client event, which is used to connect Groovester to a Voice Channel."""

		# Validate author is in a voice channel.
		if message.author.voice:
			# Connect Groovester to voice channel.
			try:
				voiceChannel = message.author.voice.channel
				self.voiceClient = await voiceChannel.connect()
				log.debug(
					"%s %s", DebugMessages._logConnectedToVoiceChannel, voiceChannel.name
				)
			except discord.ClientException as err:
				log.error(err)
				return False
			except Exception as err:
				log.error(err)
				return False
		else:
			log.error(ErrorMessages._logJoinCmdAuthorNotInVoiceChannel)
			await message.channel.send(ErrorMessages._sendJoinCmdNoActiveVoiceChannel)
			return False

		with self.readerCv:
			self.readerCv.notify()

		await message.channel.send(
			ClientHelpMessages._sendJoinCmdSuccessfulVoiceClientConnect
		)

		return True

	async def leaveClientEvent(self, message):
		"""Client event, which is used to disconnect Groovester from a Voice Channel."""

		#! Todo: Verify if user is in the same voice channel as Groovester.
		# Validate Groovester is in a voice channel.
		if not self.voiceClient == None:
			# If connected to a voice channel, disconnect Groovester.
			if self.voiceClient.is_connected():
				try:
					voiceChannel = message.author.voice.channel
					self.voiceClient = await self.voiceClient.disconnect()
					log.debug(
						"%s %s", InfoMessages._logDisconnectedFromVoiceChannel, voiceChannel.name
					)
				except discord.ClientException as err:
					log.error(err)
					return False
				except Exception as err:
					log.error(err)
					return False
		else:
			log.error(ErrorMessages._logLeaveCmdNoActiveVoiceChannel)
			await message.channel.send(ErrorMessages._sendLeaveCmdNoActiveVoiceChannel)

			return False

		await message.channel.send(
			InfoMessages._sendLeaveCmdLeaveVoiceChannel
		)
		#! Todo: print the number of songs still in queue.

		return True

	async def playClientEvent(self, message):
		"""Client event to download a song and place it in the queue."""

		# Input validation.

		# Isolate URL parameter from command.
		linkToYouTubeVideo = str(message.content)

		# Ensure format of "!play " (emphasis on ' '), not "!play-" or "!play#"
		if len(message.content) > 5 and linkToYouTubeVideo[5] == " ":
			linkToYouTubeVideo = message.content.split(" ")[1]
		else:
			await message.channel.send(ErrorMessages._sendPlayCmdIncorrectParameters)
			return False

		# Check domain is what is expected.
		if not linkToYouTubeVideo.startswith("https://www.youtube.com/"):
			await message.channel.send(ErrorMessages._sendPlayCmdIncorrectDomain)
			return False

		# Test if the Domain is reachable and valid. (Emphasis on Domain)
		if not url(linkToYouTubeVideo):
			await message.channel.send(ErrorMessages._sendPlayCmdUnreachableDomain)
			return False

		#! Todo: Add logic to limit the number of downloaded videos to ten.
		# Download the YouTube video.
		pytubeObj = downloadYouTubeAudio(linkToYouTubeVideo)
		if pytubeObj is None:
			await message.channel.send(
				ErrorMessages._sendPlayCmdFailedToDownloadAudio
			)
			return False

		# Acquire lock and await signal.
		with self.writerCv:
			while (  # Fall through if there are no active readers or writers.
				self.numReaders > 0 and self.numWriters > 0
			):

				self.writerCv.wait()
			self.numWriters = self.numWriters + 1

			# Enter mutual exclusion and add song to queue.
			self.listOfDownloadedSongsToPlay.append(pytubeObj)
			log.debug(
				"%s %s", DebugMessages._logPlayCmdAddingVideoToQueue, pytubeObj.absPathToFile
			)

			self.numWriters = self.numWriters - 1
			# Signal any threads waiting to run.
			with self.readerCv:
				self.readerCv.notify()
			self.writerCv.notify()

	#! Todo: I think it would be better to stream the song instead of download it to the filesystem.
	async def speakInVoiceChannel(self, absPathToVideoToPlay: str):
		"""Function used to allow Groovester to stream audio to the voice channel."""

		# await self.lastChannelCommandWasEntered.send("Let's play some audio!")
		# ffmpegKwargs = { # Optimized settings for ffmpeg for audio streaming, https://stackoverflow.com/questions/75493436/why-is-the-ffmpeg-process-in-discordpy-terminating-without-playing-anything
		# #   'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
		#   'options': '-vn -filter:a "volume=0.75"'
		# }
		#! Todo: Optimize settings for audio streaming.
		self.audioSource = discord.FFmpegOpusAudio(
			executable="/usr/bin/ffmpeg", source=absPathToVideoToPlay
		)

		# Check that bot is in voice channel.
		if not self.voiceClient.is_connected():
			log.error(
				ErrorMessages._logNotConnectedToVoiceChannel
			)
			return False

		# Check if Groovester is already playing a song.
		if self.voiceClient.is_playing():
			log.error(
				ErrorMessages._logAlreadyPlayingAudio
			)
			return False

		try:
			log.debug(
				"%s %s", DebugMessages._logAttemptingToPlayAudioSource, absPathToVideoToPlay
			)
			self.voiceClient.play(self.audioSource)
			log.debug(
				"%s %s", DebugMessages._logSuccessfullyPlayedAudioSource, absPathToVideoToPlay,
			)
		except discord.ClientException as err:
			self.voiceClient.stop()
			log.error("%s %s", ErrorMessages._exceptionTryingToPlayAudioSource, err)
			return False

		return True

	async def stopClientEvent(self, channel):
		"""Helper function, used to stop Groovester from streaming audio to the voice channel."""

		if self.voiceClient is not None:
			if not self.voiceClient.is_connected():
				await channel.send(InfoMessages._sendStopCmdNotInVoiceChannel)
				return False
			if not self.voiceClient.is_playing():
				await channel.send(InfoMessages._sendStopCmdNotPlayingAudio)
				return False

			self.voiceClient.stop()

		else:
			await channel.send(
				InfoMessages._sendStopCmdConditionsNotMet
			)
			return False

		return True
