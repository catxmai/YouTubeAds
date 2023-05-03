from get_video_info import get_video_info
from video_controls import *
from utils import *

import pandas as pd
import json

from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchWindowException

if __name__ == "__main__":
    df = pd.read_csv("control_videos_clean.csv")
    # df.drop_duplicates(inplace=True)

    url_list = [
        "https://www.youtube.com/watch?v="+ i for i in df['videoid']
    ]

    driver = create_driver("config.json")

    data = []

    for url in url_list:
        try:
            data.append(get_video_info(url, driver))
        except Exception as e:
            print(type(e))
            print(e)
        except NoSuchWindowException:
            driver.quit()

    with open('output.json', 'w', encoding='utf-8') as f:
        i = 0
        for video in data:
            video["id"] = i
            json.dump(video, f, ensure_ascii=True, indent=4)
            f.write('\n')
            i += 1
    driver.quit()
