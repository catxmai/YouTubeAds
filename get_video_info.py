import logging
import re
from typing import Any

from selenium import webdriver
from selenium.webdriver.common.by import By

import api


def get_video_info(driver: webdriver.Chrome) -> dict:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    video_data: a dict of info and stats for the current video

    """

    video_id = get_video_id(driver)
    video_data = api.get_info(video_id)

    video_data["urls_in_description"] = extract_urls(video_data["description"])
    video_data["comments_disabled"] = check_if_comments_disabled(driver)
    video_data["context_box_present"] = check_for_context_box(driver)
    video_data["merch_info"] = get_merch_info(driver)  # TODO implement
    # TODO: get ad info function
    # TODO: skip ad function
    video_data["is_paid_promotion"] = check_sponsor_info(driver)
    video_data["recommended_videos"] = get_recommended_videos(driver)

    return video_data  # TODO: convert video data to pandas dataframe


def get_video_id(driver: webdriver.Chrome) -> str:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    video_id: the id of the current YouTube video

    """

    video_id: str = ""
    url: str = driver.current_url
    pattern: str = r"^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*"
    match: Any = re.match(pattern, url)

    if match and len(match[7]) == 11:
        video_id = match[7]
    else:
        logging.error("Error unable to extract video id")

    return video_id


def check_if_comments_disabled(driver: webdriver.Chrome) -> bool:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    is_disabled: disable status of comments

    """

    is_disabled: bool = False

    try:
        container = driver.find_element(By.ID, "message")

        # check if either of the following messages is present under the video
        # the first is for static videos the second is for live streams
        if container.text in (
            "Comments are turned off. Learn more",
            "Chat is disabled for this live stream.",
        ):
            is_disabled = True
    except:
        pass

    return is_disabled


def extract_urls(text: str) -> list:
    """
    Parameters
    ----------
    text: a string to be parsed for urls

    Returns
    -------
    urls: a list of urls extracted from the input string


    """

    pattern: str = r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
    matches: Any = re.finditer(pattern, text)
    urls: list = [match.group() for match in matches]

    return urls


def get_merch_info(s):
    pass


def get_recommended_videos(driver):
    pass


def check_sponsor_info(driver: webdriver.Chrome) -> bool:
    """
    NOTE: Must be checked after getting through the ad or it will not work

    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    is_paid_promotion: a bool indicating the presence of a paid promotion
    disclaimer

    """

    is_paid_promotion: bool = False

    try:
        container = driver.find_element(
            By.CSS_SELECTOR, "#movie_player > div.ytp-paid-content-overlay"
        )

        if container.text:
            is_paid_promotion = True
    except:
        pass

    return is_paid_promotion


def check_for_context_box(driver: webdriver.Chrome) -> bool:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    context_box_present: a bool indicating the presence of a context box

    """

    context_box_present: bool = False
    try:
        container = driver.find_element(By.ID, "clarify-box")

        # check if either of the clarify box exists and has text
        if container.text:
            content_box_present = True
    except:
        pass

    return content_box_present
