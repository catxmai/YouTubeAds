import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException


def pause_video(driver: webdriver.Chrome):

    play_button = driver.find_element(
        By.CSS_SELECTOR, "button.ytp-play-button.ytp-button"
    )
    if play_button:
        status = play_button.get_attribute("data-title-no-tooltip")

        if status == "Pause":
            try:
                play_button.send_keys("k")
            except Exception as e:
                pass


def play_video(driver: webdriver.Chrome):

    play_button = driver.find_element(
        By.CSS_SELECTOR, "button.ytp-play-button.ytp-button"
    )
    status: str = play_button.get_attribute("data-title-no-tooltip")

    if status == "Play":
        play_button.send_keys("k")


def skip_ad(driver: webdriver.Chrome):

    def click_skip_button(driver):
        skip_button = driver.find_element(
            By.CSS_SELECTOR, 'button.ytp-ad-skip-button.ytp-button'
        )
        skip_button.click()

    try:
        click_skip_button(driver)
        
    except (NoSuchElementException, ElementNotInteractableException) as e:
        try:
            time.sleep(5)
            click_skip_button(driver)
        except (NoSuchElementException, ElementNotInteractableException) as e:
            pass
            

    