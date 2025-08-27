import os
from pathlib import Path

# from pytube import YouTube
from pytubefix import YouTube

from src.helpers import *


def test_downloading_youtube_video():
    """
    Function to test that the `pytubefix` library can download YouTube 
        videos. Tests the functionality of various file system helper 
        functions too.
    """
    assert setup_media_directory()

    # Download a random YouTube video.
    youtube_obj = YouTube("https://youtu.be/QC8iQqtG0hg?si=zJXhXDfwGs7rWn74")
    audio_stream = youtube_obj.streams.get_audio_only(
        subtype="mp4"
    )
    path_to_file = Path(audio_stream.download(filename=f"{youtube_obj.video_id}.mp4"))
    
    # Verify the file actually exists on the file system, then remove it.
    assert os.path.exists(path_to_file)
    assert remove_media_file(path_to_file)


def test_validate_url():
    assert validate_url_domain("www.youtube.com")
    assert validate_url_domain("www.youtu.be")
    assert validate_url_domain("https://www.youtube.com/watch?v=HI1wiy4-lrg")
    assert not validate_url_domain("www.youtu.b")
    assert not validate_url_domain("    ")
    assert not validate_url_domain("")
    assert not validate_url_domain("!play www.youtube.com")


def main():
    return


if "__name__" == "__main__":
    main()
