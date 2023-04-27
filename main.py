from selenium import webdriver

from get_video_info import get_video_info
import pandas as pd
import json

def create_driver(config_path=""):
    # config is a json file
    if config_path:
        config = {}
        config_f = open(config_path, 'r')
        config_json = json.load(config_f)
        config_f.close()
        config['username'] = config_json['username']
        config['password'] = config_json['password']
        config['user_data'] = config_json['user_data']
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1540,1080")
    options.add_argument("--no-sandbox")
    if config['user_data']:
        options.add_argument("user-data-dir=" + config['user_data'])

    driver = webdriver.Chrome(options = options)
    return driver


if __name__ == "__main__":
    df = pd.read_csv("control_videos_clean.csv")
    df.drop_duplicates(inplace=True)

    url_list = [
        "https://www.youtube.com/watch?v="+ i for i in df['videoid']
    ]

    driver = create_driver("config.json")
    data: list = []

    for url in url_list:
        try:
            data.append(get_video_info(url, driver))
        except Exception as e:
            pass

    print(data)
