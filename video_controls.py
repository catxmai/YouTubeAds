from selenium import webdriver
from selenium.webdriver.common.by import By


def pause_video(driver):
    play_button = driver.find_element(
        By.CSS_SELECTOR, "button.ytp-play-button.ytp-button"
    )
    status = play_button.get_attribute("data-title-no-tooltip")

    if status == "Pause":
        play_button.send_keys("k")


def play_video(driver):
    play_button = driver.find_element(
        By.CSS_SELECTOR, "button.ytp-play-button.ytp-button"
    )
    status = play_button.get_attribute("data-title-no-tooltip")

    if status == "Play":
        play_button.send_keys("k")
