import logging
import re
import time
import datetime
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from get_ad_info import *
from video_controls import *

from utils import *


def get_video_info(video_url, driver: webdriver.Chrome) -> dict:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    video_data: a dict of info and stats for the current video

    """
    if not driver:
        return
    driver.get(video_url)
    time.sleep(2)
    video_id = get_video_id(driver)
    try:
        play_video(driver)
    except ElementNotInteractableException:
        return {
            'video_id': video_id,
            'video_unavailable': True
        }

    pause_video(driver)

    load_script_tag(driver)
    video_title = get_video_title()

    preroll_ad_id, preroll_ad_reasons, preroll_ad_info, preroll_ad_site = None, None, None, None
    preroll_ad_id = get_preroll_ad_id(driver)
    if preroll_ad_id == video_id:
        preroll_ad_id = None
    else:
        preroll_ad_reasons, preroll_ad_info = get_preroll_ad_info(driver)
        preroll_ad_site = get_preroll_ad_site(driver)
        
    channel_name = get_channel_name()
    video_description = get_video_description()
    date_uploaded = get_upload_date()
    likes = get_likes(driver)
    views = get_views()
    comment_count = get_comment_count(driver)
    video_genre = get_video_genre()

    MAX_WAIT_TIME = 45 
    preroll_ad2_id, preroll_ad2_reasons, preroll_ad2_info, preroll_ad2_site = None, None, None, None
    if get_number_of_ads_left(driver) == 1:
        time_left = get_ad_duration(driver)
        if time_left < MAX_WAIT_TIME:
            play_video(driver)
            time.sleep(time_left + 10)
            preroll_ad2_id = get_preroll_ad_id(driver)
            if preroll_ad2_id == video_id:
                preroll_ad2_id = None
            else:
                preroll_ad2_reasons, preroll_ad2_info = get_preroll_ad_info(driver)
                preroll_ad2_site = get_preroll_ad_site(driver)
            
    play_video(driver)
    skip_ad(driver)
    pause_video(driver)

    side_ad_reasons, side_ad_info = get_side_ad_info(driver)
    side_ad_site = get_side_ad_site(driver) 
    side_ad_text = get_side_ad_text(driver)
    side_ad_img = get_side_ad_img(driver)

    promoted_video_reasons, promoted_video_info = get_promoted_video_info(driver)
    promoted_video_url = get_promoted_video_url(driver)
    promoted_video_title = get_promoted_video_title(driver)
    promoted_video_channel = get_promoted_video_channel(driver)
    channel_id = get_channel_id(driver)

    video_url = "https://www.youtube.com/watch?v=" + video_id
    preroll_ad_video_url = "https://www.youtube.com/watch?v=" + preroll_ad_id if preroll_ad_id else None
    preroll_ad2_video_url = "https://www.youtube.com/watch?v=" + preroll_ad2_id if preroll_ad2_id else None

    video_data = {
        'video_id': video_id,
        'video_title': video_title,
        'video_url': video_url,
        'channel_name': channel_name,
        'channel_id': channel_id,
        'video_genre': video_genre,
        'video_description': video_description,
        'date_uploaded': date_uploaded,
        'likes': likes,
        'views': views,
        'comment_count': comment_count,

        'preroll_ad_id': preroll_ad_id,
        'preroll_ad_video_url': preroll_ad_video_url,
        # 'preroll_ad_url': preroll_ad_url,
        'preroll_ad_site': preroll_ad_site,
        'preroll_ad_reasons': preroll_ad_reasons,
        'preroll_ad_info': preroll_ad_info,

        'preroll_ad2_id': preroll_ad2_id,
        'preroll_ad2_video_url': preroll_ad2_video_url,
        'preroll_ad2_site': preroll_ad2_site,
        'preroll_ad2_reasons': preroll_ad2_reasons,
        'preroll_ad2_info': preroll_ad2_info,
        
        # 'side_ad_url': side_ad_url,
        'side_ad_site': side_ad_site,
        'side_ad_text': side_ad_text,
        'side_ad_img': side_ad_img,
        'side_ad_reasons': side_ad_reasons, 
        'side_ad_info': side_ad_info,

        'promoted_video_title': promoted_video_title,
        'promoted_video_url': promoted_video_url,
        'promoted_video_channel': promoted_video_channel,
        'promoted_video_reasons': promoted_video_reasons,
        'promoted_video_info': promoted_video_info,
        
    }

    return video_data



def get_video_id(driver: webdriver.Chrome) -> str:
    url = driver.current_url
    pattern = r"(?<=watch\?v=).{11}" #capture anything with 11-length after watch?v=
    match = re.search(pattern, url)

    if match:
        return match[0]
    return None

def load_script_tag(driver: webdriver.Chrome):
    # loads a web element with id = "scriptTag" that contains a lot of useful info
    global SCRIPT_TAG
    try:
        time.sleep(1)
        SCRIPT_TAG = json.loads(driver.find_element(By.ID, "scriptTag").get_attribute("innerHTML"))
    except NoSuchElementException:
        pass


def get_video_title():
    try:
        title = SCRIPT_TAG['name']
        return title
    except (TypeError, KeyError) as e:
        return None
    

def get_views():
    try:
        views = SCRIPT_TAG['interactionCount']
        return views
    except (TypeError, KeyError) as e:
        return None
    

def get_channel_name():
    try:
        name = SCRIPT_TAG['author']
        return name
    except (TypeError, KeyError) as e:
        return None
    

def get_video_description():
    try:
        description = SCRIPT_TAG['description']
        return description
    except (TypeError, KeyError) as e:
        return None
    

def get_upload_date():
    try:
        date = SCRIPT_TAG['uploadDate']
        return date
    except (TypeError, KeyError) as e:
        return None
    

def get_video_genre():
    try:
        genre = SCRIPT_TAG['genre']
        return genre
    except (TypeError, KeyError) as e:
        return None
    


def get_channel_id(driver):

    try:
        container = driver.find_element(
            By.CSS_SELECTOR, ".ytp-ce-channel-title.ytp-ce-link.style-scope.ytd-player")
        channel_url = container.get_attribute('href')
        pattern = r"(?<=\/channel\/).{24}"
        match = re.search(pattern, channel_url)

        if match:
            channel_id = match[0] 
    except NoSuchElementException:
        return None

    return channel_id


def get_comment_count(driver):
    # Comment count is not searchable in html element if don't scroll down

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
                return None
            last_height = new_height

        count += 1


    try:
        comment_count = int("".join(list(filter(str.isdigit, container.text))))
    except:
        comment_count = None

    driver.execute_script("window.scrollTo(0, 0);")

    return comment_count


def get_likes(driver):

    # Like button's aria-label is "like this video along with 282,068 other people"
    try:
        like_button_container = driver.find_element(
            By.CSS_SELECTOR, "#segmented-like-button > ytd-toggle-button-renderer > yt-button-shape > button")
        aria_label = like_button_container.get_attribute('aria-label')
        aria_label = aria_label.replace(',', '')
        like_count = int(re.findall('\d+', aria_label)[0])
    except:
        return None

    return like_count


def check_for_context_box(driver: webdriver.Chrome) -> bool:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    context_box_present: a bool indicating the presence of a context box

    """

    context_box_present = False
    try:
        container = driver.find_element(By.ID, "clarify-box")

        # check if either of the clarify box exists and has text
        if container.text:
            context_box_present = True
    except:
        pass

    return context_box_present
