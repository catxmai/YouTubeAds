from get_video_info import get_video_info
from video_controls import *
from utils import *

import pandas as pd
import json


if __name__ == "__main__":
    df = pd.read_csv("control_videos_clean.csv")
    df.drop_duplicates(inplace=True)

    url_list = [
        "https://www.youtube.com/watch?v="+ i for i in df['videoid']
    ]

    driver = create_driver("config.json")

    data = []

    for url in url_list:
        try:
            data.append(get_video_info(url, driver))
        except:
            pass

    print(data)
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=True, indent=4)
