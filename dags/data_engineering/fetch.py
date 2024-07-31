"""
    DAG operators that will deal with accessing the HTTP requests
"""

from dotenv import load_dotenv
from googleapiclient.discovery import build
import re
from youtube_transcript_api import YouTubeTranscriptApi
from typing import Dict, List
# from airflow.decorators import task
import os

load_dotenv()
YOUTUBE_DATA_API_KEY = os.getenv('YOUTUBE_DATA_API_KEY')
API_SERVICE = "youtube"
API_VERSION = "v3"

youtube = build(API_SERVICE, API_VERSION, developerKey=YOUTUBE_DATA_API_KEY)

# TODO: try/except block incase the api is every down for troubleshooting
# @task
def get_uploaded_videos_by_channel(
    channel: str = "moreplatesmoredates") -> str:
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
# @task
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
        videoId = video['contentDetails']['videoId']
        videos.append(videoId)
    return videos#, next_page_token

# TODO
# @task
def filter_out_shorts(video_ids: List[str]) -> List[Dict[str, str]]:
    """ Filter raw videos into videos and leave the shorts behind using API
    
    Parameters
    ----------
    video_ids : List[str]
        Video IDs which will be going into the API
    
    Returns
    -------

    """
    videos = []
    pattern = r"(\d+)([A-Z]?)"
    time_factor = {'H': 3600, 'M': 60, 'S': 1}
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=",".join(video_ids)
    )
    response = request.execute()
    for i, item in enumerate(response['items']):
        matches = re.findall(pattern, item['contentDetails']['duration'])
        cumulative_time = 0
        for num, time in matches:
            cumulative_time += int(num) * time_factor[time]
        if cumulative_time > 60:
            videos.append({
                'video_id': video_ids[i],
                'title': item['snippet']['title'],
                'tags': item['snippet']['tags'],
                'duration': str(cumulative_time)
            })
    return videos

# TODO
# @task
def get_video_transcripts(video_dict: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """ Get video transcripts from cleaned videos
    
    Parameters
    ----------
    video_dict : List[Dict[str, str]]
        Video dictionary with will give us the id and place to store transcripts
    
    Returns
    -------

    """
    for video in video_dict:
        video_id = video['video_id']
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        video['transcript'] = transcript
    
    return video_dict
