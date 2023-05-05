import logging
import re
import time
import datetime
import json
from typing import Any, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *

import api
from get_ad_info import *
from video_controls import *
from utils import *


def get_video_info(video_url, driver: webdriver.Chrome, use_api = False) -> dict:
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
    try:
        play_video(driver)
    except ElementNotInteractableException:
        return {
            'video_id': video_id,
            'video_unavailable': True
        }

    time.sleep(2)
    pause_video(driver)

    video_data = {}
    video_data["video_id"] = video_id
    load_script_tag(driver)
    video_data["video_title"] = get_video_title()
    video_data["video_url"] = "https://www.youtube.com/watch?v=" + video_id
    video_data["channel_name"] = get_channel_name()
    video_data["channel_id"] = get_channel_id(driver)
    video_data["video_description"] = get_video_description()
    video_data["date_uploaded"] = get_upload_date()
    video_data["likes"] = get_likes(driver)
    video_data["views"] = get_views()
    video_data["comment_count"] = get_comment_count(driver)
    video_data["video_genre"] = get_video_genre()
    video_data["preroll_ad_id"] = get_preroll_ad_id(driver)
    video_data["preroll_ad_reasons"], video_data["preroll_ad_info"] = get_preroll_ad_info(driver)
    video_data["preroll_ad_url"] = get_preroll_ad_url(driver)

    """
    # Skipping this part for now

    # number_of_ads_left = get_number_of_ads_left(driver)
    # print("# of ads left: " + number_of_ads_left)

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

    """

    #if ad is preroll, try to skip, if not then continue
    try:
        play_video(driver)
        skip_ad(driver)
        time.sleep(1)
    except:
        pass

    pause_video(driver)

    video_data["is_paid_promotion"] = check_sponsor_info(driver)

    try:
        video_data["side_ad_reasons"], video_data["side_ad_info"] = get_side_ad_info(driver)
        video_data["side_ad_url"] = get_side_ad_url(driver) 
    except:
        pass


    try:
        video_data["promoted_video_info"] = get_promoted_video_info(driver)
        video_data["promoted_video_id"] = get_promoted_video_id(driver)
    except:
        pass

    return video_data



def get_video_id(driver: webdriver.Chrome) -> str:
    url = driver.current_url
    pattern = r"(?<=watch\?v=).{11}" #capture anything with 11-length after watch?v=
    match = re.search(pattern, url)

    if match:
        return match[0]
    return "-1"

def load_script_tag(driver: webdriver.Chrome):
    # loads a web element with id = "scriptTag" that contains a lot of useful info
    global SCRIPT_TAG
    try:
        time.sleep(2)
        SCRIPT_TAG = json.loads(driver.find_element(By.ID, "scriptTag").get_attribute("innerHTML"))
    except AttributeError:
        pass


def get_video_title():
    try:
        video_title = SCRIPT_TAG['name']
    except:
        video_title = '-1'
    return video_title


def get_views():
    try:
        views = SCRIPT_TAG['interactionCount']
    except:
        views = -1
    return views


def get_channel_name():
    try:
        channel_name = SCRIPT_TAG['author']
    except:
        channel_name = '-1'
    return channel_name


def get_video_description():
    try:
        descr = SCRIPT_TAG['description']
    except:
        descr = '-1'
    return descr


def get_upload_date():
    try:
        date = SCRIPT_TAG['uploadDate']
    except:
        date = '-1'
    return date

def get_video_genre():
    try:
        genre = SCRIPT_TAG['genre']
    except:
        genre = '-1'
    return genre


def get_channel_id(driver):
    try:
        channel_container = driver.find_element(
            By.CSS_SELECTOR, "#watch7-content > meta[itemprop='channelId']")
        channel_id = channel_container.get_attribute('content')
    except:
        channel_id = '-1'
    return channel_id


def get_comment_count(driver):
    # Comment count is not searchable in html element if don't scroll down
    # Returns -1 if can't get comment count
    SCROLL_PAUSE_TIME = .5

    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    found = False
    container = None

    # Sometimes need to scroll page to get comment section to load
    count = 0
    while not found:
        try:
            container = driver.find_element(By.XPATH, '//yt-formatted-string[@class="count-text style-scope ytd-comments-header-renderer"]')
            found = True
        except:
            found = False

        if not found:
            driver.execute_script("window.scrollTo(0, " + str(last_height/4) + ");")
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.documentElement.scrollHeight") 

            if (new_height == last_height) and count > 3:
                driver.execute_script("window.scrollTo(0, 0);")
                return -1
            last_height = new_height

        count += 1


    try:
        comment_count = int("".join(list(filter(str.isdigit, container.text))))
    except:
        comment_count = -1

    driver.execute_script("window.scrollTo(0, 0);")

    return comment_count


def check_if_comments_disabled(driver: webdriver.Chrome) -> bool:

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


def get_likes(driver):

    # Like button's aria-label is "like this video along with 282,068 other people"
    try:
        like_button_container = driver.find_element(
            By.CSS_SELECTOR, "#segmented-like-button > ytd-toggle-button-renderer > yt-button-shape > button")
        aria_label = like_button_container.get_attribute('aria-label')
        aria_label = aria_label.replace(',', '')
        like_count = int(re.findall('\d+', aria_label)[0])
    except:
        return -1

    return like_count



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
    except (NoSuchElementException, JavascriptException) as e:
        pass

    return url



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
