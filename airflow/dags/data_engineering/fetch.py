"""
    DAG operators that will deal with accessing the HTTP requests
"""

from dotenv import load_dotenv
from googleapiclient.discovery import build
import re
from youtube_transcript_api import YouTubeTranscriptApi
from airflow.decorators import task
import os
import json
from datetime import timedelta
from data_engineering import utils

load_dotenv()
YOUTUBE_DATA_API_KEY = os.getenv('YOUTUBE_DATA_API_KEY')
API_SERVICE = "youtube"
API_VERSION = "v3"
DATA_PATH = utils.create_data_folder()

youtube = build(API_SERVICE, API_VERSION, developerKey=YOUTUBE_DATA_API_KEY)


# TODO: try/except block incase the api is every down for troubleshooting
@task
def get_uploaded_videos_by_channel(channel: str = "moreplatesmoredates") -> str:
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
    response = response['items'][0]['contentDetails']
    return response['relatedPlaylists']['uploads']


@task
def get_uploaded_videos_raw(playlist_id: str, page_token: str = None) -> str:
    """ Get raw videos from the uploaded playlist id

    Parameters
    ----------
    playlist_id : str
        Playlist ID which will return us the list of videos

    Returns
    str
        Gives path of data file
    -------

    """
    videos = []
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=50,
        pageToken=page_token,
        playlistId=playlist_id
    )
    response = request.execute()
    # next_page_token = response['nextPageToken']
    for video in response['items']:
        videoId = video['contentDetails']['videoId']
        videos.append(videoId)
    
    file_name = "raw_videos"
    return utils.write_file(DATA_PATH, file_name, videos)
    

@task
def filter_out_shorts(raw_data_path: str) -> str:
    """ Filter raw videos into videos and leave the shorts behind using API

    Parameters
    ----------
    raw_data_path : str
        path where raw data is located

    Returns
    -------
    str
        Returns the data location of our filtered data
    """
    video_ids = utils.open_file(raw_data_path)
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
            
    file_name = "filter_videos"
    
    return utils.write_file(DATA_PATH, file_name, videos)


@task(retries=5, retry_delay=timedelta(seconds=15))
def get_video_transcripts(filtered_path: str) -> str:
    """ Get video transcripts from cleaned videos

    Parameters
    ----------
    filtered_path : str
        Path location of our filtered data

    Returns
    -------
    str
        Returns path of transcripted data
    """
    video_dict = utils.open_file(filtered_path)
    for video in video_dict:
        video_id = video['video_id']
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        video['transcript'] = transcript
    
    file_name = "transcripted_videos"
    return utils.write_file(DATA_PATH, file_name, video_dict)

if __name__ == "__main__":
    playlist_id = get_uploaded_videos_by_channel() 
    raw_vid_path = get_uploaded_videos_raw(playlist_id)
    filtered_path = filter_out_shorts(raw_vid_path)
    transcripts = get_video_transcripts(filtered_path)
