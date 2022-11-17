from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
import time
from selenium.webdriver import ActionChains


def check_for_banner(driver):
    banner_present = False
    try:
        banner = driver.find_element(By.CSS_SELECTOR, ".ytp-ad-overlay-image")
        banner_present = True
    except NoSuchElementException:
        pass
    return banner_present


def check_for_preroll(driver):
    preroll_present = False
    try:
        element = driver.find_element(By.CSS_SELECTOR, ".ytp-ad-text")
        preroll_present = True
    except NoSuchElementException:
        pass
    return preroll_present


def get_why_this_ad_info(driver: webdriver.Chrome):
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    reasons: list of reasons youtube provides for why the ad was served to the user


    """
    reasons = []
    try:
        info_button = driver.find_element(
            By.CSS_SELECTOR,
            "button.ytp-ad-button.ytp-ad-button-link.ytp-ad-clickable",
        )
        info_button.click()
        iframe = driver.find_element(By.ID, "iframe")
        driver.switch_to.frame(iframe)
        reasons = driver.find_elements(By.CSS_SELECTOR, ".Xkwrgc")
        reasons = [element.text for element in reasons]  # type: ignore[misc]
        exit_button = driver.find_element(
            By.CSS_SELECTOR, ".VfPpkd-Bz112c-LgbsSe.yHy1rc.eT1oJ.mN1ivc.YJBIwf"
        )
        exit_button.click()
        driver.switch_to.default_content()

    except:
        pass

    return reasons


def get_ad_id(driver: webdriver.Chrome) -> str:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    ad_id: the video id of the youtube ad


    """

    ad_id = ""
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
        exit_button.click()
    except:
        pass
    return ad_id


def get_preroll_advertiser_url(driver):
    element = driver.find_element(
        By.CSS_SELECTOR,
        "button.ytp-ad-button.ytp-ad-visit-advertiser-button.ytp-ad-button-link",
    )

    element.click()

    # save current tab and switch chromedriver's focus to the new tab
    video_tab = driver.current_window_handle
    tabs_open = driver.window_handles
    driver.switch_to.window(tabs_open[1])

    # wait 5 secs to account for possible redirects
    time.sleep(5)
    url = driver.current_url
    driver.close()
    driver.switch_to.window(video_tab)

    return url


def get_banner_advertiser(driver):
    banner = driver.find_element(By.CSS_SELECTOR, ".ytp-ad-overlay-image")
    banner.click()

    # save current tab and switch chromedriver's focus to the new tab
    video_tab = driver.current_window_handle
    tabs_open = driver.window_handles
    driver.switch_to.window(tabs_open[1])

    # wait 5 secs to account for possible redirects
    time.sleep(5)
    url = driver.current_url
    driver.close()
    driver.switch_to.window(video_tab)

    return url


def get_number_of_ads_left(driver):
    elements = driver.find_elements(By.CSS_SELECTOR, ".ytp-ad-text")
    text = [element.text for element in elements]
    if any(["Ad 1 of 2" in msg for msg in text]):
        return 1
    else:
        return 0


def is_skippable(driver):
    elements = driver.find_elements(By.CSS_SELECTOR, ".ytp-ad-text")
    text = [element.text for element in elements]
    if any(["Ad will end" in msg for msg in text]):
        return False
    else:
        return True


def skip_ad(driver):
    skip_button = driver.find_element(
        By.CSS_SELECTOR, "button.ytp-ad-skip-button.ytp-button"
    )
    skip_button.click()


def check_for_sparkles_ad(driver):
    sparkles_present = False
    try:
        element = driver.find_element(By.CSS_SELECTOR, "#sparkles-container")
        sparkles_present = True
    except NoSuchElementException:
        pass
    return sparkles_present


def check_for_promoted_video(driver):
    promoted_video_present = False
    try:
        element = driver.find_element(
            By.CSS_SELECTOR, "#items > ytd-compact-promoted-video-renderer"
        )
        promoted_video_present = True
    except NoSuchElementException:
        pass
    return promoted_video_present


def get_promoted_video_info(driver):
    menu_button = element = driver.find_element(
        By.CSS_SELECTOR,
        ".style-scope.ytd-compact-promoted-video-renderer > yt-icon-button > button",
    )
    menu_button.click()
    info_button = driver.find_element(
        By.CSS_SELECTOR,
        "#items > ytd-menu-navigation-item-renderer:nth-child(2) > a > tp-yt-paper-item",
    )

    info_button.click()
    iframe = driver.find_element(By.ID, "iframe")
    driver.switch_to.frame(iframe)
    reasons = driver.find_elements(By.CSS_SELECTOR, ".Xkwrgc")
    reasons = [element.text for element in reasons]  # type: ignore[misc]
    exit_button = driver.find_element(
        By.CSS_SELECTOR, ".VfPpkd-Bz112c-LgbsSe.yHy1rc.eT1oJ.mN1ivc.YJBIwf"
    )
    exit_button.click()
    driver.switch_to.default_content()

    return reasons


def get_sparkles_info(driver):
    menu_button = driver.find_element(
        By.CSS_SELECTOR,
        ".style-scope.ytd-promoted-sparkles-web-renderer > yt-icon-button > button",
    )
    menu_button.click()
    info_button = driver.find_element(
        By.CSS_SELECTOR,
        "#items > ytd-menu-navigation-item-renderer.style-scope.ytd-menu-popup-renderer.iron-selected > a > tp-yt-paper-item",
    )
    info_button.click()
    iframe = driver.find_element(By.ID, "iframe")
    driver.switch_to.frame(iframe)
    reasons = driver.find_elements(By.CSS_SELECTOR, ".Xkwrgc")
    reasons = [element.text for element in reasons]  # type: ignore[misc]
    exit_button = driver.find_element(
        By.CSS_SELECTOR, ".VfPpkd-Bz112c-LgbsSe.yHy1rc.eT1oJ.mN1ivc.YJBIwf"
    )
    exit_button.click()
    driver.switch_to.default_content()


def get_sparkles_ad_url(driver):
    element = driver.find_element(
        By.CSS_SELECTOR, "#action-button > ytd-button-renderer > a"
    )

    element.click()

    # save current tab and switch chromedriver's focus to the new tab
    video_tab = driver.current_window_handle
    tabs_open = driver.window_handles
    driver.switch_to.window(tabs_open[1])

    # wait 5 secs to account for possible redirects
    time.sleep(5)
    url = driver.current_url
    driver.close()
    driver.switch_to.window(video_tab)

    return url


def check_for_ads(driver):
    pass
