"""" 
File for fetching and making sure the HTTP request work as intended before moving on
"""

from dotenv import load_dotenv
from googleapiclient.discovery import build
from typing import Dict, List
import os

load_dotenv()
YOUTUBE_DATA_API_KEY = os.getenv('YOUTUBE_DATA_API_KEY')
API_SERVICE = "youtube"
API_VERSION = "v3"

youtube = build(API_SERVICE, API_VERSION, developerKey=YOUTUBE_DATA_API_KEY)


def get_uploaded_videos_by_channel(channel: str = "moreplatesmoredates") -> Dict[str, str]:
    """ Gets the uploaded videos key from the channel
    
    Parameters
    ----------
    channel : str
        Channel name we are looking for
    
    Returns
    -------
    str
        Key for the playlist called uploaded videos
    """
    request = youtube.channels().list(
        part="contentDetails",
        forHandle=channel
    )

    response = request.execute()
    response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

