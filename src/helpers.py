import logging as log
import os

import discord
from pytube import YouTube

from src.constants import ClientHelpMessages, DebugMessages, ErrorMessages, InfoMessages

ABS_PATH_TO_TMP_GROOVESTER_DOWNLOADS = None
log.getLogger(__name__)  # Set same logging parameters as client.py.


#! Todo: Make class that can store URL and absolute file path on local file
#!  system.
def downloadYouTubeAudio(linkToYouTubeVideo: str):
	"""Helper function used to download a YouTube video given a valid URL."""

	#!  Todo: Ensure that the local file system has enough space for the video.
	ytObj = YouTube(linkToYouTubeVideo)
	audioStream = ytObj.streams.get_audio_only()  # Only download audio and save it as .mp4.

	# Download video via pytube API.
	try:
		absPathToDownloadedVideo = audioStream.download()
	except OSError as err:
		log.error("%s %s", ErrorMessages._exceptionPlayFailedToDownloadVideo, err)
		return None
	except Exception as err:
		log.error(err)
		return None

	if not os.path.exists(absPathToDownloadedVideo):
		return None
	log.debug("%s %s", InfoMessages._logPlaySuccessfulyDownloadedVideo, linkToYouTubeVideo)

	# Store key information relating to the video in a PyTube object.
	pytubeObj = PyTube(absPathToDownloadedVideo, linkToYouTubeVideo, ytObj)

	return pytubeObj


#!  Todo: Pass system argument to identify if OS is Linux or Windows. Helps setup FS.
#!  Todo: Create a thread that goes through and verifies the videos stored in /tmp are still there.
#!	   Compare against list.
def setupTmpDirectory():
	"""Used to setup the directory to store YouTube videos."""

	global ABS_PATH_TO_TMP_GROOVESTER_DOWNLOADS
	ABS_PATH_TO_TMP_GROOVESTER_DOWNLOADS = os.getcwd() + "/"

	ABS_PATH_TO_TMP_GROOVESTER_DOWNLOADS = ABS_PATH_TO_TMP_GROOVESTER_DOWNLOADS + "tmp/"
	if not os.path.exists(ABS_PATH_TO_TMP_GROOVESTER_DOWNLOADS):
		try:
			os.mkdir(ABS_PATH_TO_TMP_GROOVESTER_DOWNLOADS)
		except OSError as err:
			log.error(err)
			return False
		except Exception as err:
			log.error(err)
			return False

	ABS_PATH_TO_TMP_GROOVESTER_DOWNLOADS = (
		ABS_PATH_TO_TMP_GROOVESTER_DOWNLOADS + "downloads/"
	)
	if not os.path.exists(ABS_PATH_TO_TMP_GROOVESTER_DOWNLOADS):
		try:
			os.mkdir(ABS_PATH_TO_TMP_GROOVESTER_DOWNLOADS)
		except OSError as err:
			log.error(err)
			return False
		except Exception as err:
			log.error(err)
			return False

	os.chdir(ABS_PATH_TO_TMP_GROOVESTER_DOWNLOADS)

	return True


class PyTube:

	def __init__(self, absPathToFile: str, url: str, pytube: YouTube):
		self.absPathToFile = absPathToFile
		self.url = url
		self.pytube = pytube
