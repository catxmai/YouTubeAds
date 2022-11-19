import time

from selenium import webdriver
from selenium.webdriver.common.by import By


def pause_video(driver: webdriver.Chrome):
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    reasons: list of reasons youtube provides for why the ad was served to the user

    """

    play_button = driver.find_element(
        By.CSS_SELECTOR, "button.ytp-play-button.ytp-button"
    )
    status: str = play_button.get_attribute("data-title-no-tooltip")

    if status == "Pause":
        play_button.send_keys("k")


def play_video(driver: webdriver.Chrome):
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    reasons: list of reasons youtube provides for why the ad was served to the user

    """

    play_button = driver.find_element(
        By.CSS_SELECTOR, "button.ytp-play-button.ytp-button"
    )
    status: str = play_button.get_attribute("data-title-no-tooltip")

    if status == "Play":
        play_button.send_keys("k")


def skip_ad(driver: webdriver.Chrome):
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    reasons: list of reasons youtube provides for why the ad was served to the user

    """

    skip_button = driver.find_element(
        By.CSS_SELECTOR, "button.ytp-ad-skip-button.ytp-button"
    )
    skip_button.click()


def wait_for_ad(driver: webdriver.Chrome):
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    None

    """
    time_left_element = driver.find_element(
        By.CSS_SELECTOR, "span.ytp-ad-duration-remaining > div.ytp-ad-text"
    )
    minutes_left, seconds_left = time_left_element.text.split(":")
    time_left = int(minutes_left) * 60 + int(seconds_left)

    # one second is added to the time left because there is a small buffer period between the end of the ad
    # and the loading of the main video
    play_video(driver)
    time.sleep(time_left + 1)
