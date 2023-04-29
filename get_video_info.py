import logging
import re
import time
from typing import Any, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *

import api
from get_ad_info import *
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

    # video_data["urls_in_description"] = extract_urls(video_data["description"])
    video_data["comments_disabled"] = check_if_comments_disabled(driver)
    video_data["context_box_present"] = check_for_context_box(driver)
    video_data["merch_info"] = get_merch_info(driver)

    is_preroll = check_for_preroll(driver)

    if is_preroll:
        video_data["preroll_ad_id"] = get_ad_id(driver)
        video_data["preroll_ad_info"] = get_why_this_ad_info(driver)
        video_data["preroll_ad_url"] = get_preroll_advertiser_url(driver)

        # Skipping this part since watching in entirety the first ad will skip the second ad

        # number_of_ads_left = get_ad_info.get_number_of_ads_left(driver)

        # if number_of_ads_left == 1:
        #     preroll_ad_2: Dict[str, str] = {}
        #     wait_for_ad(driver)
        #     play_video(driver)
        #     time.sleep(2)
        #     pause_video(driver)
        #     preroll_ad_2["ad_id"] = get_ad_info.get_ad_id(driver)
        #     preroll_ad_2["why_info"] = str(
        #         get_ad_info.get_why_this_ad_info(driver)
        #     )  # Warn: list to str conversion
        #     preroll_ad_2["ad_url"] = get_ad_info.get_preroll_advertiser_url(
        #         driver
        #     )
        #     preroll_data.append(preroll_ad_2)

        try:
            play_video(driver)
            skip_ad(driver)
            time.sleep(1)
        except:
            pass

        pause_video(driver)

    # check for banner ads

    video_data["is_paid_promotion"] = check_sponsor_info(driver)

    try:
        video_data["side_ad_info"] = get_side_ad_info(driver) 
        video_data["side_ad_url"] = get_side_ad_url(driver) 
    except:
        pass


    try:
        video_data["promoted_video_info"] = get_promoted_video_info(driver)
        video_data["promoted_video_id"] = get_promoted_video_id(driver)
    except:
        pass

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

    video_id = ""
    url = driver.current_url
    pattern = r"^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*"
    match = re.match(pattern, url)

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

    url = ""
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
