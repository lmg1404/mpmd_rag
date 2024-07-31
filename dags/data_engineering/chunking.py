# FIXME: some repetitive parts of chunking between 2 strategies
"""
    DAG operators that help chunk for RAG
"""
from typing import List, Dict, Callable
# from airflow.decorators import task

CHARACTER_CHUNK_LENGTH = 500
CHARACTER_OVERLAP = 20
WORD_CHUNK_LENGTH = 100
WORD_OVERLAP = 10

def create_payload(chunk: str, **kwargs) -> Dict[str, str]:
    """ Creates a payload easily from keyword arguments instead of multiple lines
    
    Parameters
    ----------
    chunk : str 
        chunk based on the version used
    **kwargs
        dict that we add to then return
    
    Returns
    -------
    Dict[str, str]
        The payload of our chunk with metadata
    """
    kwargs['chunk'] = chunk
    return kwargs

# FIXME: 2 for loops when this probably could be done in one
# @task
def character_chunking(youtube_video_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """ Character chunks a YouTube video transcript with it's metadata
    
    Parameters
    ----------
    youtube_video_data : 
        Previous iterations of the data structure to chunks
    
    Returns
    -------
    List[Dict[str, str]]
        List of chunks with their metadata
    """
    # keys: video_id, title, tags, 'duration', 'transcript'
        # in transcript: it's a list with 'text', 'start', and 'duration
    payload = []
    video_id = youtube_video_data['video_id']
    title = youtube_video_data['title']
    tags = youtube_video_data['tags']
    duration = youtube_video_data['duration']
    all_text = ""
    for transcript in youtube_video_data['transcript']:
        text = transcript['text']
        all_text += " " + text
        
    for i in range(0, len(all_text), CHARACTER_CHUNK_LENGTH-CHARACTER_OVERLAP):
        chunk = all_text[i:i+CHARACTER_CHUNK_LENGTH]
        p = create_payload(chunk, video_id=video_id, 
                           title=title, tags=tags, duration=duration)
        payload.append(p)
        
    return payload
        
# FIXME: same as character chunking
# @task
def word_chunking(youtube_video_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """ Gets the uploaded videos key from the channel
    
    Parameters
    ----------
    youtube_video_data : List[Dict[str, str]]
        Previous iterations of the data structure to chunks
    
    Returns
    -------
    List[Dict[str, str]]
        List of chunks with their metadata
    """
    payload = []
    video_id = youtube_video_data['video_id']
    title = youtube_video_data['title']
    tags = youtube_video_data['tags']
    duration = youtube_video_data['duration']
    all_text = ""
    for transcript in youtube_video_data['transcript']:
        text = transcript['text']
        all_text += " " + text
    words = all_text.split()
        
    for i in range(0, len(words), WORD_CHUNK_LENGTH-WORD_OVERLAP):
        chunk = ' '.join(words[i:i+WORD_CHUNK_LENGTH])
        p = create_payload(chunk, video_id=video_id, 
                           title=title, tags=tags, duration=duration)
        payload.append(p)
        
    return payload

def chunk(transcripts: List[Dict[str, str]], chunk_func: Callable) -> List[Dict[str, str]]:
    """ Gets the uploaded videos key from the channel
    
    Parameters
    ----------
    transcripts : List[Dict[str, str]]
        Youtube video metadata with raw api transcript
    chunk_func : Callable
        Chunking strategy based on a defined strategy
    
    Returns
    -------
    List[Dict[str, str]]
        List of chunks which is our payload to upload to VDB
    """
    payload = []
    for t in transcripts:
        chunked_transcript = chunk_func(t)
        payload += chunked_transcript
    return payload

# NOTE: instead of this do unit tests next time
# if __name__ == "__main__":
#     import fetch
#     playlist_id = fetch.get_uploaded_videos_by_channel()
#     video_ids = fetch.get_uploaded_videos_raw(playlist_id)
#     videos = fetch.filter_out_shorts(video_ids)
#     transcripts = fetch.get_video_transcripts(videos)
#     payloads = chunk(transcripts, word_chunking)
#     for p in payloads:
#         print(p)
    