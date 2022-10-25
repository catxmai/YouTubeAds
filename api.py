# -*- coding: utf-8 -*-

import googleapiclient.discovery  # type: ignore[import]
import googleapiclient.errors  # type: ignore[import]

from keys import API_KEY

from typing import Dict, Any


def get_info(video_id: str) -> Dict[str, Any]:
    """
    Parameters
    ----------
    video_id: the id of the desired YouTube video as a str

    Returns
    -------
    video_data: a dict of select info and stats for the requested video

    """

    # Set up the API and make a call to get video info
    api_service_name: str = "youtube"
    api_version: str = "v3"

    youtube: googleapiclient.discovery.Resource = (
        googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=API_KEY
        )
    )

    request: googleapiclient.http.HttpRequest = youtube.videos().list(
        part="snippet,contentDetails,statistics", id=video_id
    )

    response: Dict[str, Any] = request.execute()

    # The response comes back as a dict with a lot of video data
    # but we only extract the values that we need for the study

    snippet: Dict[str, str] = response["items"][0]["snippet"]
    statistics: Dict[str, str] = response["items"][0]["statistics"]

    video_data: Dict[str, Any] = {}

    video_data["channel_name"] = snippet["channelTitle"]
    video_data["channel_id"] = snippet["channelId"]
    video_data["description"] = snippet["description"]
    video_data["title"] = snippet["title"]
    video_data["date_uploaded"] = snippet["publishedAt"]

    video_data["likes"] = int(statistics["likeCount"])
    video_data["views"] = int(statistics["viewCount"])
    video_data["comments"] = int(statistics["commentCount"])

    return video_data
