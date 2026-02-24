import os
import random
import zipfile
import requests
import platform

from status import *
from config import *

AUDIO_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".m4a",
    ".aac",
    ".ogg",
    ".flac",
}


def _get_audio_files(songs_dir: str) -> list[str]:
    """Returns all playable audio files inside songs_dir."""
    return [
        file_name
        for file_name in os.listdir(songs_dir)
        if os.path.isfile(os.path.join(songs_dir, file_name))
        and os.path.splitext(file_name)[1].lower() in AUDIO_EXTENSIONS
    ]

def close_running_selenium_instances() -> None:
    """
    Closes any running Selenium instances.

    Returns:
        None
    """
    try:
        info(" => Closing running Selenium instances...")

        # Kill all running Firefox instances
        if platform.system() == "Windows":
            os.system("taskkill /f /im firefox.exe")
        else:
            os.system("pkill firefox")

        success(" => Closed running Selenium instances.")

    except Exception as e:
        error(f"Error occurred while closing running Selenium instances: {str(e)}")

def build_url(youtube_video_id: str) -> str:
    """
    Builds the URL to the YouTube video.

    Args:
        youtube_video_id (str): The YouTube video ID.

    Returns:
        url (str): The URL to the YouTube video.
    """
    return f"https://www.youtube.com/watch?v={youtube_video_id}"

def rem_temp_files() -> None:
    """
    Removes temporary files in the `.mp` directory.

    Returns:
        None
    """
    # Path to the `.mp` directory
    mp_dir = os.path.join(ROOT_DIR, ".mp")

    files = os.listdir(mp_dir)

    for file in files:
        if not file.endswith(".json"):
            os.remove(os.path.join(mp_dir, file))

def fetch_songs() -> None:
    """
    Downloads songs into songs/ directory to use with geneated videos.

    Returns:
        None
    """
    try:
        info(f" => Fetching songs...")

        files_dir = os.path.join(ROOT_DIR, "Songs")
        if not os.path.exists(files_dir):
            os.mkdir(files_dir)
            if get_verbose():
                info(f" => Created directory: {files_dir}")
        elif _get_audio_files(files_dir):
            # Skip if songs are already downloaded
            return

        # Download songs
        response = requests.get(get_zip_url() or "https://filebin.net/bb9ewdtckolsf3sg/drive-download-20240209T180019Z-001.zip")

        # Save the zip file
        with open(os.path.join(files_dir, "songs.zip"), "wb") as file:
            file.write(response.content)

        # Unzip the file
        with zipfile.ZipFile(os.path.join(files_dir, "songs.zip"), "r") as file:
            file.extractall(files_dir)

        # Remove the zip file
        os.remove(os.path.join(files_dir, "songs.zip"))

        success(" => Downloaded Songs to ../Songs.")

    except Exception as e:
        error(f"Error occurred while fetching songs: {str(e)}")

def choose_random_song() -> str | None:
    """
    Chooses a random song from the songs/ directory.

    Returns:
        str: The path to the chosen song.
    """
    songs_dir = os.path.join(ROOT_DIR, "Songs")
    songs = _get_audio_files(songs_dir)
    if not songs:
        error(
            "Error occurred while choosing random song: "
            "No supported audio files found in Songs/. "
            "Please run setup again or add audio files manually."
        )
        return None

    song = random.choice(songs)
    success(f" => Chose song: {song}")
    return os.path.join(songs_dir, song)
