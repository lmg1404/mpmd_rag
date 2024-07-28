"""" 
DAG operators that will deal with accessing the HTTP requests
"""

from dotenv import load_dotenv
from googleapiclient.discovery import build
import requests
from typing import Dict, List, Tuple
import os

load_dotenv()
YOUTUBE_DATA_API_KEY = os.getenv('YOUTUBE_DATA_API_KEY')
API_SERVICE = "youtube"
API_VERSION = "v3"

youtube = build(API_SERVICE, API_VERSION, developerKey=YOUTUBE_DATA_API_KEY)

# TODO: try/except block incase the api is every down for troubleshooting
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
    return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

# TODO
def get_uploaded_videos_raw(playlist_id: str, page_token: str = None):
    """ Get raw videos from the uploaded playlist id
    
    Parameters
    ----------
    playlist_id : str
        Playlist ID which will return us the list of videos
    
    Returns
    -------
    
    """
    videos = []
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=50,
        pageToken=page_token,
        playlistId = playlist_id
    )
    response = request.execute()
    next_page_token = response['nextPageToken']
    for video in response['items']:
        title = video['snippet']['title']
        videoId = video['contentDetails']['videoId']
        videos.append((title, videoId))
    return videos, next_page_token
        

# TODO
def filter_out_shorts():
    pass

# TODO
def get_video_transcripts():
    pass

# playlist_id = get_uploaded_videos_by_channel("moreplatesmoredates")
# videos, next_page_token = get_uploaded_videos_raw(playlist_id)

anatomy = 'https://www.youtube.com/shorts/'
test1 = 'ed9VQ7UoTWQ'
test2 = 'kmZ6NbLC73U'

print(requests.get(anatomy + test1))
print(requests.get(anatomy + test2))

