from urllib.parse import urlparse, parse_qs
import time
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver import ActionChains


def get_ad_duration(driver):
    time_left_element = driver.find_element(
        By.CSS_SELECTOR, "span.ytp-ad-duration-remaining > div.ytp-ad-text"
    )
    minutes_left, seconds_left = time_left_element.text.split(":")
    time_left = int(minutes_left) * 60 + int(seconds_left)

    return time_left

def get_number_of_ads_left(driver) -> int:

    number_of_ads_left = 0

    elements = driver.find_elements(By.CSS_SELECTOR, ".ytp-ad-text")
    text = [element.text for element in elements]

    if any(["Ad 1 of 2" in msg for msg in text]):
        number_of_ads_left = 1

    return number_of_ads_left

def get_reasons(driver):
    try:
        google_info = driver.find_elements(By.CLASS_NAME, "QVfAMd-wPzPJb-xPjCTc-ibnC6b")
        google_info = [element.get_attribute('textContent') for element in google_info]
    except NoSuchElementException:
        google_info = []
    try:
        other_info = driver.find_elements(By.CLASS_NAME, "zpMl8e-C2o4Ve-wPzPJb-xPjCTc-ibnC6b")
        other_info = [element.get_attribute('innerHTML') for element in other_info] 
    except NoSuchElementException:
        other_info = []
    
    return google_info + other_info


def get_advertiser_info(driver):
    advertiser_name, advertiser_loc = None, None

    try:
        ad_container = driver.find_elements(By.CLASS_NAME, "G5HdJb-fmcmS")
        if ad_container:
            advertiser_name = ad_container[0].get_attribute("innerHTML")
            advertiser_loc = ad_container[1].get_attribute("innerHTML")
    except IndexError:
        return advertiser_name, None
    except NoSuchElementException:
        pass

    return advertiser_name, advertiser_loc


def get_preroll_ad_info(driver):

    try:
        reason_container = driver.find_element(By.CSS_SELECTOR, ".ytp-ad-info-dialog-ad-reasons")
        li = reason_container.find_elements(By.CSS_SELECTOR,"li")
        reasons = [element.get_attribute('innerHTML') for element in li] 
        return reasons, get_advertiser_info(driver)
    except NoSuchElementException:
        pass


    try:
        info_button = driver.find_element(
            By.CSS_SELECTOR,
            "button.ytp-ad-button.ytp-ad-button-link.ytp-ad-clickable",
        )
        driver.execute_script("arguments[0].click();", info_button)
        iframe = driver.find_element(By.ID, "iframe")
        driver.switch_to.frame(iframe) 

        reasons = get_reasons(driver)
        advertiser_info = get_advertiser_info(driver)

        exit_button = driver.find_element(

            By.CSS_SELECTOR, ".VfPpkd-Bz112c-LgbsSe.yHy1rc.eT1oJ.mN1ivc.YJBIwf"
        )
        exit_button.click()
        driver.switch_to.default_content()
    except NoSuchElementException:
        return None, None
    

    return reasons, advertiser_info


def get_preroll_ad_id(driver):

    try:
        # right clicking the video and opening the "stats for nerds" menu
        action = ActionChains(driver)
        video_player = driver.find_element(
            By.CSS_SELECTOR, "#movie_player > div.html5-video-container > video"
        )
        action.context_click(video_player).perform()
        stats_button = driver.find_element(
            By.CSS_SELECTOR,
            "div.ytp-popup.ytp-contextmenu > div > div > div:nth-child(7)",
        )
        stats_button.click()
        id_element = driver.find_element(By.CSS_SELECTOR, ".ytp-sfn-cpn")

        # use split to extract only the video id characters
        ad_id = id_element.text.split()[0]

        exit_button = driver.find_element(
            By.CSS_SELECTOR, "button.html5-video-info-panel-close.ytp-button"
        )
        driver.execute_script("arguments[0].click();", exit_button)
        return ad_id

    except NoSuchElementException:
        return None

    


def get_preroll_ad_site(driver):

    # site is usually the link to advertiser's site, but sometimes it's just the site name
    try:
        element = driver.find_element(
            By.CSS_SELECTOR,
            "button.ytp-ad-button.ytp-ad-visit-advertiser-button.ytp-ad-button-link"
        )

        site = element.get_attribute("aria-label").strip()
        return site
    except NoSuchElementException:
        return None



def get_side_ad_info(driver):
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    reasons: list of reasons youtube provides for why the ad was served to the user

    """

    try:
        menu_button = driver.find_element(
            By.CSS_SELECTOR,
            ".style-scope.ytd-promoted-sparkles-web-renderer > yt-icon-button > button",
        )
        driver.execute_script("arguments[0].click();", menu_button)

        info_button = driver.find_element(
            By.CSS_SELECTOR,
            "#items > ytd-menu-navigation-item-renderer.style-scope.ytd-menu-popup-renderer.iron-selected > a > tp-yt-paper-item",
        )

        driver.execute_script("arguments[0].click();", info_button)

        iframe = driver.find_element(By.ID, "iframe")
        driver.switch_to.frame(iframe)

        reasons = get_reasons(driver)
        advertiser_info = get_advertiser_info(driver)

        exit_button = driver.find_element(

            By.CSS_SELECTOR, ".VfPpkd-Bz112c-LgbsSe.yHy1rc.eT1oJ.mN1ivc.YJBIwf"
        )
        exit_button.click()
        driver.switch_to.default_content()
    except NoSuchElementException:
        return None, None
    
    return reasons, advertiser_info


def get_side_ad_site(driver):

    # site is usually the link to advertiser's site, but sometimes it's just the site name

    try:
        side_ad_container = driver.find_element(By.CSS_SELECTOR, "#website-text")
        site = side_ad_container.get_attribute("innerHTML").strip()
        return site
    except NoSuchElementException:
        return None



def click_side_ad(driver):

    try:

        element = driver.find_element(
            By.CSS_SELECTOR,
            ".style-scope.ytd-promoted-sparkles-web-renderer > yt-button-shape > button"
        )

        driver.execute_script("arguments[0].click();", element)
    except NoSuchElementException:
        return None

    # save current tab and switch chromedriver's focus to the new tab
    video_tab = driver.current_window_handle
    tabs_open = driver.window_handles
    driver.switch_to.window(tabs_open[1])
    
    url = driver.current_url
    while url == "about:blank":
        url = driver.current_url
    driver.execute_script("window.stop();")
    url = driver.current_url
    driver.close()
    driver.switch_to.window(video_tab)
    return url

def click_preroll_ad(driver):

    try:
        element = driver.find_element(
            By.CSS_SELECTOR,
            "button.ytp-ad-button.ytp-ad-visit-advertiser-button.ytp-ad-button-link"
        )

        driver.execute_script("arguments[0].click();", element)
    except NoSuchElementException:
        return None

    # save current tab and switch chromedriver's focus to the new tab
    video_tab = driver.current_window_handle
    tabs_open = driver.window_handles
    driver.switch_to.window(tabs_open[1])
    
    url = driver.current_url
    while url == "about:blank":
        url = driver.current_url
    driver.execute_script("window.stop();")
    url = driver.current_url
    driver.close()
    driver.switch_to.window(video_tab)
    return url

def get_side_ad_text(driver):

    title, body = "", ""

    try:
        title_container = driver.find_element(By.CSS_SELECTOR, "#title.style-scope.ytd-promoted-sparkles-web-renderer.yt-simple-endpoint")
        title = title_container.get_attribute("innerHTML").strip()
    except NoSuchElementException:
        pass

    try:
        body_container = driver.find_element(By.CSS_SELECTOR, "#description.style-scope.ytd-promoted-sparkles-web-renderer.yt-simple-endpoint")
        body = body_container.get_attribute("innerHTML").strip()
    except NoSuchElementException:
        pass

    text = title + body
    text = text if text else None
    return text


def get_side_ad_img(driver):

    try:
        img_container = driver.find_element(By.CSS_SELECTOR, "#thumbnail.style-scope.ytd-promoted-sparkles-web-renderer > img")
        img_src = img_container.get_attribute("src")
    except NoSuchElementException:
        return None

    return img_src


def get_promoted_video_title(driver):

    try:
        container = driver.find_element(By.CSS_SELECTOR, "#video-title.style-scope.ytd-compact-promoted-video-renderer")
        title = container.get_attribute("title")
    except NoSuchElementException:
        return None

    return title


def get_promoted_video_channel(driver):

    try:
        ad_container = driver.find_element(By.CSS_SELECTOR, "#endpoint-link.yt-simple-endpoint.style-scope.ytd-compact-promoted-video-renderer")
        channel_container = ad_container.find_element(By.CSS_SELECTOR, "#text > a")
        channel = channel_container.get_attribute("innerHTML")
    except NoSuchElementException:
        return None

    return channel


def get_promoted_video_info(driver: webdriver.Chrome):

    reasons, advertiser_info = None, None

    try:
        menu_button = driver.find_element(
            By.CSS_SELECTOR,
            ".style-scope.ytd-compact-promoted-video-renderer > yt-icon-button > button")


        driver.execute_script("arguments[0].click();", menu_button)
        
        info_button = driver.find_element(
            By.CSS_SELECTOR,
            "#items > ytd-menu-navigation-item-renderer > a > tp-yt-paper-item"
        )

        driver.execute_script("arguments[0].click();", info_button)

        iframe = driver.find_element(By.ID, "iframe")
        driver.switch_to.frame(iframe)
        reasons = get_reasons(driver)
        advertiser_info = get_advertiser_info(driver)
        exit_button = driver.find_element(
            By.CSS_SELECTOR, ".VfPpkd-Bz112c-LgbsSe.yHy1rc.eT1oJ.mN1ivc.YJBIwf"
        )
        driver.execute_script("arguments[0].click();", exit_button)
        driver.switch_to.default_content()
    except NoSuchElementException:
        pass

    return reasons, advertiser_info


def get_promoted_video_url(driver: webdriver.Chrome) -> str:

    try:
        element = driver.find_element(
            By.CSS_SELECTOR,
            "#rendering-content > ytd-compact-promoted-video-renderer > div > a",
        )

        raw_url = element.get_attribute("href")
        pattern = r"(?<=video_id=).{11}"
        match = re.search(pattern, raw_url)

        if match:
            return "https://www.youtube.com/watch?v=" + match[0]

    except NoSuchElementException:
        pass

    return None



