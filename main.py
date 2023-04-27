from selenium import webdriver

from get_video_info import get_video_info
import pandas as pd

def create_driver(config=""):
    return webdriver.Chrome()


if __name__ == "__main__":
    df = pd.read_csv("control_videos_clean.csv")
    df.drop_duplicates(inplace=True)

    url_list = [
        "https://www.youtube.com/watch?v="+ i for i in df['videoid']
    ]

    driver = create_driver()
    data: list = []

    for url in url_list:
        try:
            data.append(get_video_info(url, driver))
        except Exception as e:
            pass

    print(data)
