from dataclasses import dataclass


@dataclass(frozen=True)
class ClientMessages :
	_helpPlayCommand: str = (
	    "!play usage:\t !play *URL to YouTube URL*\n"
	    + "\tGroovester will download YouTube video and play it in a voice channel!"
	)


@dataclass(frozen=True)
class DebugMessages :
	_logActiveReadersOrWriters: str = (
		_threadGivingUpTimeSlice	
		+ "Groovester has active an reader or writer thread."
	)
	_logActiveVoiceClient: str = (
		_threadGivingUpTimeSlice	
		+ "Groovester's voice client is already playing a song."
	)
	_logAttemptingToPlayAudioSource: str = (
		"Attempting to play audio source: "
	)
	_logClientRunAttempt: str = (
		"Attempting to start Groovester!"
	)
	_logConnectedToVoiceChannel: str = (
		"!join successfully connected to the voice channel: "
	)
	_logDisconnectedFromVoiceChannel: str = (
		"!leave successfully disconnected from the voice channel: "
	)
	_logInactiveVoiceClient: str = (
		_threadGivingUpTimeSlice	
		+ "waiting for Groovester's voice client to connect to a voice channel."
	)
	_logPlaySongsInDiscordAudioThreadStarted: str = (
		"playSongsInDiscordAudioThread has started!"
	)
	_logPlayCmdAddingVideoToQueue: str = (
		"Adding YouTube video URL to queue: " 
	)
	_logQueueEmpty: str = (
		_threadGivingUpTimeSlice	
		+ "waiting for songs to be put in Groovester's queue."
	)
	_logRemovedFileFromFileSystem: str = (
		"Successfully removed the following file from the file system: "
	)
	_logSuccessfullyPlayedAudioSource: str = (
		"Groovester successfully played an audio source: "
	)
	_logUninstantiatedVoiceClient: str = (
		_threadGivingUpTimeSlice	
		+ "waiting for Groovester's voice client to instantiate."
	)
	_threadGivingUpTimeSlice: str = (
		"Thread is giving up it's time slice, "
	)


@dataclass(frozen=True)
class ErrorMessages :
	_exceptionClientRun: str = (
		"An error occurred while trying to start the Groovester client:"
	)
	_exceptionOnReadyChildThread: str = (
		"on_ready failed to spawn child thread:"
	)
	_exceptionPlayFailedToDownloadVideo: str = (
		"!play failed, an error has occurred while downloading the following video:"
	)
	_exceptionTryingToPlayAudioSource: str = (
		"Exception thrown while trying to play an audio source: "
	)
	_exceptionUnableToRemoveFileFromFileSystem: str = (
		"Exception thrown while trying to delete the audio file from the file system: "
	)
	_logAlreadyPlayingAudio: str = (
    	_failedToPlayAudio
        + "Groovester is already playing audio!"
    )
    _logJoinCmdAuthorNotInVoiceChannel: str = (
		"!join failed, message author is not in a voice channel."
    )
    _logLeaveCmdNoActiveVoiceChannel: str = (
    	"!leave failed, Groovester is not in a voice channel."
    )
	_logNotConnectedToVoiceChannel: str = (
		_failedToPlayAudio
        + "Groovester has not connected to a voice channel yet!"
    )
	_sendJoinCmdNoActiveVoiceChannel: str = (
	    "Incorrect !join usage...\n"
	    + "\tYou are not currently in a voice channel."
	)
	_sendLeaveCmdNoActiveVoiceChannel: str = (
	    "Incorrect !leave usage...\n"
	    + "\tGroovester is not actively connected to a voice channel."
	)
	_sendPlayCmdIncorrectDomain: str = (
	    "Incorrect !play usage...\n"
	    + "\tPlease enter a valid domain."
	)
	_sendPlayCmdIncorrectParameters: str = (
	    "Incorrect !play usage...\n"
	    + "\t!play *URL to YouTube video*"
	)
	_sendPlayCmdUnreachableDomain: str = (
	    "Incorrect !play usage...\n"
	    + "\tEnter a valid domain."
	)
	_sendPlayCmdFailedToDownloadAudio: str = (
		"Groovester failed to download the requested video!"
	)

	#! Todo: Is this being used?
	_failedToPlayAudio: str = (
		"Groovester failed to play audio! "
	)

@dataclass(frozen=True)
class InfoMessages :
	_logGroovesterStartedSuccessfully: str = (
		"Groovester started Successfully!"
	)
	_logNewGroovesterInstance: str = (
		"\n===================================================" 
        + "\n\t\t\tNew Groovester instance started!" 
        + "\n==================================================="
    )
    _logPlaySuccessfulyDownloadedVideo: str = (
		"!play successfully downloaded the following video:" 
	)
	_sendJoinCmdSuccessfulVoiceClientConnect: str = (
		"Groovester successfully joined the voice channel!"
        + " Here are some useful commands to get you started: "
        #! Todo: Send a list of useful commands to the text channel.
    )
    _sendStopCmdConditionsNotMet: str = (
		"You must issue \"!join\" in order to use this command!"
	)
	_sendLeaveCmdLeaveVoiceChannel: str = (
		"Bye, bye! :("
	)
    _sendStopCmdNotInVoiceChannel: str = (
    	"Groovester is not in a voice channel!"
    )
    _sendStopCmdNotPlayingAudio: str = (
    	"Groovester is not playing audio!"
    )
