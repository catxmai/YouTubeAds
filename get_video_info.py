import logging
import re
import time
from typing import Any, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *

import api
import get_ad_info
from video_controls import *


def get_video_info(video_url, driver: webdriver.Chrome) -> dict:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    video_data: a dict of info and stats for the current video

    """

    driver.get(video_url)
    video_id = get_video_id(driver)
    time.sleep(2)

    # selenium + youtube has strange behaviour when paused immediately after
    # retrieving a url and will sometimes skip the ad prematurely, so we play
    # the video for two seconds before collecting info
    play_video(driver)
    time.sleep(2)
    pause_video(driver)
    video_data = api.get_info(video_id)

    video_data["urls_in_description"] = extract_urls(video_data["description"])
    video_data["comments_disabled"] = check_if_comments_disabled(driver)
    video_data["context_box_present"] = check_for_context_box(driver)
    video_data["merch_info"] = get_merch_info(driver)

    is_preroll = get_ad_info.check_for_preroll(driver)
    video_data["is_preroll"] = str(is_preroll)

    video_data["preroll_data"] = ""

    if is_preroll:
        preroll_data = []
        preroll_ad_1: Dict[str, str] = {}
        preroll_ad_1["ad_id"] = get_ad_info.get_ad_id(driver)
        preroll_ad_1["why_info"] = str(
            get_ad_info.get_why_this_ad_info(driver)
        )  # Warn: list to str conversion
        preroll_ad_1["ad_url"] = get_ad_info.get_preroll_advertiser_url(driver)

        preroll_data.append(preroll_ad_1)

        number_of_ads_left = get_ad_info.get_number_of_ads_left(driver)
        if number_of_ads_left == 1:
            preroll_ad_2: Dict[str, str] = {}
            wait_for_ad(driver)
            play_video(driver)
            time.sleep(2)
            pause_video(driver)
            preroll_ad_2["ad_id"] = get_ad_info.get_ad_id(driver)
            preroll_ad_2["why_info"] = str(
                get_ad_info.get_why_this_ad_info(driver)
            )  # Warn: list to str conversion
            preroll_ad_2["ad_url"] = get_ad_info.get_preroll_advertiser_url(
                driver
            )
            preroll_data.append(preroll_ad_2)

        video_data["preroll_data"] = str(
            preroll_data
        )  # Warn: list to str conversion

        if get_ad_info.is_skippable(driver):
            play_video(driver)
            # wait 5 seconds for ad to become skippable
            time.sleep(6)
            skip_ad(driver)
            # wait 1 second for main video to load
            time.sleep(1)
        else:
            wait_for_ad(driver)

        pause_video(driver)

    # check for banner ads

    video_data["is_paid_promotion"] = check_sponsor_info(driver)

    video_data["sparkles_ad_present"] = "False"
    video_data["sparkles_ad_info"] = ""
    video_data["sparkles_url"] = ""

    if get_ad_info.check_for_sparkles_ad(driver):
        video_data["sparkles_ad_present"] = "True"
        video_data["sparkles_ad_info"] = get_ad_info.get_sparkles_info(driver)
        video_data["sparkles_url"] = get_ad_info.get_sparkles_ad_url(driver)

    video_data["promoted_video_present"] = "False"
    video_data["promoted_video_info"] = ""
    video_data["promoted_video_id"] = ""

    if get_ad_info.check_for_promoted_video(driver):
        video_data["promoted_video_present"] = "True"
        video_data["promoted_video_info"] = get_ad_info.get_promoted_video_info(
            driver
        )
        video_data["promoted_video_id"] = get_ad_info.get_promoted_video_id(
            driver
        )

    video_data["recommended_videos"] = get_recommended_videos(driver)

    return video_data


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


def get_merch_info(driver: webdriver.Chrome) -> str:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    url: url of the merch store or a blank string if no merch store is found

    """

    url: str = ""
    try:
        merch_shelf = driver.find_element(
            By.CSS_SELECTOR,
            "a.yt-simple-endpoint.style-scope.ytd-merch-shelf-item-renderer",
        )
        merch_shelf.click()

        # save current tab and switch chromedriver's focus to the new tab
        video_tab = driver.current_window_handle
        tabs_open = driver.window_handles
        driver.switch_to.window(tabs_open[1])

        # wait 5 secs to account for possible redirects
        time.sleep(5)
        url = driver.current_url
        driver.close()

        # return control to original tab
        driver.switch_to.window(video_tab)
    except NoSuchElementException:
        pass

    return url


def get_recommended_videos(driver):
    pass


def check_sponsor_info(driver: webdriver.Chrome) -> bool:
    """
    NOTE:

    Must be checked after getting through the ad or it will not work.

    Also be aware that it disappears after several seconds so it must be captured
    within the first few seconds.

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
            context_box_present = True
    except:
        pass

    return context_box_present
