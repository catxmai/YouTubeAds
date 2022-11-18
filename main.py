from selenium import webdriver

from get_video_info import get_video_info


def create_driver(config=""):
    return webdriver.Chrome()


if __name__ == "__main__":
    url_list: list = []
    driver = create_driver()
    data: list = []

    for url in url_list:
        data.append(get_video_info(url, driver))
