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
    play_video(driver)
    time.sleep(2)
    pause_video(driver)
    if use_api:
        video_data = api.get_info(video_id)
    else:
        video_data = {}
        video_data["video_id"] = video_id
        video_data["video_title"] = get_video_title(driver)
        video_data["video_url"] = "https://www.youtube.com/watch?v=" + video_id
        video_data["channel_id"], video_data["channel_name"] = get_channel_info(driver)
        video_data["video_description"] = get_video_description(driver)
        video_data["date_uploaded"], _ = get_upload_date(driver)
        video_data["likes"] = get_likes(driver)
        video_data["views"] = get_views(driver)
        video_data["comment_count"] = get_comment_count(driver)
        
        
    video_data["comments_disabled"] = check_if_comments_disabled(driver)
    video_data["context_box_present"] = check_for_context_box(driver)
    video_data["merch_info"] = get_merch_info(driver)

    is_preroll = check_for_preroll_ad(driver)

    if is_preroll:
        video_data["preroll_ad_id"] = get_preroll_ad_id(driver)
        video_data["preroll_ad_info"] = get_preroll_ad_info(driver)
        video_data["preroll_ad_url"] = get_preroll_ad_url(driver)

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
        video_data["side_ad_info"] = get_side_ad_info(driver) 
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
        # logging.error("Error unable to extract video id")
        video_id = -1

    return video_id



def get_video_title(driver: webdriver.Chrome) -> str:
    # Get video title
    return driver.find_element(By.XPATH, '//yt-formatted-string[@class="style-scope ytd-video-primary-info-renderer"]').text


def get_views(driver):
    # Get number of views
    # Returns -1 if we cant find the view count
    try:
        container = driver.find_element(By.XPATH, '//span[@class="view-count style-scope ytd-video-view-count-renderer"]')
        views = int("".join(list(filter(str.isdigit, container.text))))
    except:
        return -1

    return views


def get_channel_info(driver):
    container = driver.find_element(By.XPATH, '//ytd-channel-name[@id="channel-name"]')
    channel = container.find_element(By.XPATH, './/a[@class="yt-simple-endpoint style-scope yt-formatted-string"]')

    link = channel.get_attribute('href')
    link = remove_prefix(link, 'https://www.youtube.com')

    if '/channel/' not in link:
        ID = link
    else:
        ID = remove_prefix(link, '/channel/')

    return ID, channel.text


def get_video_description(driver):
    try:
        description_container = driver.find_element(By.ID, "scriptTag")
        descr = json.loads(description_container.get_attribute("innerHTML"))
        descr = descr['description']

    except AttributeError:
        return "-1"

    return descr


def get_comment_count(driver):
    # Get number of comments
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


def get_upload_date(driver):
    # Get date uploaded
    # Returns date as string and timestamp
    container = driver.find_element(By.XPATH, '//div[@id="info-strings"]')
    date = container.find_element(By.XPATH,'.//yt-formatted-string[@class="style-scope ytd-video-primary-info-renderer"]').text

    pattern = "(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?) \d{1,2}, \d{4}"
    
    search = re.search(pattern, date)
    if search is not None:
        date = search.group()

    try:
        date_time_object = datetime.datetime.strptime(date, '%b %d, %Y')
    except: 
        return date, datetime.datetime(1990,1,1).timestamp()
    
    return date, int(date_time_object.timestamp())


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


def get_likes(driver):

    like_count = -1

    # Like button aria-label is e.g. "like this video along with 282,068 other people"
    like_button_container = driver.find_element(
        By.CSS_SELECTOR, "#segmented-like-button > ytd-toggle-button-renderer > yt-button-shape > button")

    aria_label = like_button_container.get_attribute('aria-label')
    aria_label = aria_label.replace(',', '')
    like_count = int(re.findall('\d+', aria_label)[0])

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
    except NoSuchElementException:
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
