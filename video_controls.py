import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


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
        try:
            play_button.send_keys("k")
        except Exception as e:
            pass


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

    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.ytp-ad-skip-button-container.ytp-button')))
    skip_button = driver.find_element(
        By.CSS_SELECTOR, 'button.ytp-ad-skip-button-container.ytp-button'
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

def youtube_login(driver: webdriver.Chrome, username, password):

    signinurl = "https://accounts.google.com/signin/v2/identifier?service=youtube"
    driver.get(signinurl)

    uEntry = driver.find_element("id","identifierId")
    uEntry.clear()
    uEntry.send_keys(username)

    nextButton = driver.find_element('xpath','//span[text()="Next"]')
    nextButton = nextButton.find_element('xpath','./..')
    nextButton.click()

    WebDriverWait(driver, 4).until(EC.presence_of_element_located(('id', 'password')))
    pEntry = driver.find_element('id',"password")
    pEntry = pEntry.find_element('xpath','.//input[@type="password"]')
    pEntry.clear()
    pEntry.send_keys(password)
    time.sleep(1)
    pEntry.send_keys(Keys.RETURN)
    time.sleep(2)
