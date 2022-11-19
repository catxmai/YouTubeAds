from selenium import webdriver

from get_video_info import get_video_info


def create_driver(config=""):
    return webdriver.Chrome()


if __name__ == "__main__":
    url_list: list = [
        "https://www.youtube.com/watch?v=u3sTkewqnkc",
    ]
    driver = create_driver()
    data: list = []

    for url in url_list:
        data.append(get_video_info(url, driver))

    print(data)
