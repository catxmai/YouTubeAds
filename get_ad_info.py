import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver import ActionChains


def check_for_banner(driver: webdriver.Chrome) -> bool:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    banner_present: a bool indicating the presence of a banner ad

    """

    banner_present: bool = False
    try:
        banner = driver.find_element(By.CSS_SELECTOR, ".ytp-ad-overlay-image")
        banner_present = True
    except NoSuchElementException:
        pass
    return banner_present


def check_for_preroll(driver: webdriver.Chrome) -> bool:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    preroll_present: a bool indicating the presence of a preroll ad

    """

    preroll_present: bool = False
    try:
        element = driver.find_element(By.CSS_SELECTOR, ".ytp-ad-text")
        preroll_present = True
    except NoSuchElementException:
        pass
    return preroll_present


def get_why_this_ad_info(driver: webdriver.Chrome) -> list:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    reasons: list of reasons youtube provides for why the ad was served to the user

    """

    reasons: list = []
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

    ad_id: str = ""
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


def get_preroll_advertiser_url(driver: webdriver.Chrome) -> str:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    url: url linked to by the preroll advertisement

    """

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
    url: str = driver.current_url

    # close tab and switch back to main tab
    driver.close()
    driver.switch_to.window(video_tab)

    return url


def get_banner_advertiser(driver: webdriver.Chrome) -> str:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    url: url linked to by the banner advertisement

    """

    banner = driver.find_element(By.CSS_SELECTOR, ".ytp-ad-overlay-image")
    banner.click()

    # save current tab and switch chromedriver's focus to the new tab
    video_tab = driver.current_window_handle
    tabs_open = driver.window_handles
    driver.switch_to.window(tabs_open[1])

    # wait 5 secs to account for possible redirects
    time.sleep(5)
    url: str = driver.current_url

    # close tab and switch back to main tab
    driver.close()
    driver.switch_to.window(video_tab)

    return url


def get_number_of_ads_left(driver: webdriver.Chrome) -> int:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    number_of_ads_left: the number of ads left before the main video plays

    """

    number_of_ads_left: int = 0

    elements = driver.find_elements(By.CSS_SELECTOR, ".ytp-ad-text")
    text: list = [element.text for element in elements]

    if any(["Ad 1 of 2" in msg for msg in text]):
        number_of_ads_left = 1

    return number_of_ads_left


def is_skippable(driver: webdriver.Chrome) -> bool:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    is_skippable: a bool indicating whether the current advertisement is a
    skippable ad

    """

    is_skippable: bool = True

    elements = driver.find_elements(By.CSS_SELECTOR, ".ytp-ad-text")
    text: list = [element.text for element in elements]

    if any(["Ad will end" in msg for msg in text]):
        is_skippable = False

    return is_skippable


def check_for_sparkles_ad(driver: webdriver.Chrome) -> bool:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    sparkles_present: a bool indicating the presence of a "sparkles" ad

    """

    sparkles_present: bool = False
    try:
        element = driver.find_element(By.CSS_SELECTOR, "#sparkles-container")
        sparkles_present = True
    except NoSuchElementException:
        pass
    return sparkles_present


def check_for_promoted_video(driver: webdriver.Chrome) -> bool:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    promoted_video_present: a bool indicating the presence of a promoted at the top
    of the recommended videos list

    """

    promoted_video_present: bool = False
    try:
        element = driver.find_element(
            By.CSS_SELECTOR, "#items > ytd-compact-promoted-video-renderer"
        )
        promoted_video_present = True
    except NoSuchElementException:
        pass
    return promoted_video_present


def get_promoted_video_info(driver: webdriver.Chrome) -> list:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    reasons: list of reasons youtube provides for why the ad was served to the user

    """

    menu_button = driver.find_element(
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
    reasons: list = driver.find_elements(By.CSS_SELECTOR, ".Xkwrgc")
    reasons = [element.text for element in reasons]  # type: ignore[misc]
    exit_button = driver.find_element(
        By.CSS_SELECTOR, ".VfPpkd-Bz112c-LgbsSe.yHy1rc.eT1oJ.mN1ivc.YJBIwf"
    )
    exit_button.click()
    driver.switch_to.default_content()

    return reasons


def get_promoted_video_id(driver: webdriver.Chrome) -> str:
    pass


def get_sparkles_info(driver: webdriver.Chrome) -> list:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    reasons: list of reasons youtube provides for why the ad was served to the user

    """

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
    reasons: list = driver.find_elements(By.CSS_SELECTOR, ".Xkwrgc")
    reasons = [element.text for element in reasons]  # type: ignore[misc]
    exit_button = driver.find_element(
        By.CSS_SELECTOR, ".VfPpkd-Bz112c-LgbsSe.yHy1rc.eT1oJ.mN1ivc.YJBIwf"
    )
    exit_button.click()
    driver.switch_to.default_content()

    return reasons


def get_sparkles_ad_url(driver: webdriver.Chrome) -> str:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)

    Returns
    -------
    url: url linked to by the "sparkles" advertisement

    """

    element = driver.find_element(
        By.CSS_SELECTOR,
        ".style-scope.ytd-promoted-sparkles-web-renderer > yt-button-shape > button",
    )

    element.click()

    # save current tab and switch chromedriver's focus to the new tab
    video_tab = driver.current_window_handle
    tabs_open = driver.window_handles
    driver.switch_to.window(tabs_open[1])

    # wait 5 secs to account for possible redirects
    time.sleep(5)
    url: str = driver.current_url
    driver.close()
    driver.switch_to.window(video_tab)

    return url
