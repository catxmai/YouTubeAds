from get_video_info import get_video_info
from video_controls import *
from utils import *

import pandas as pd
import json
import time 

from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchWindowException

if __name__ == "__main__":
    start_time = time.time()
    df = pd.read_csv("control_videos_clean.csv")
    # df.drop_duplicates(inplace=True)

    url_list = [
        (df_index,"https://www.youtube.com/watch?v="+ i['videoid']) for df_index, i in df[:500].iterrows()
    ]

    driver = create_driver("config.json", headless=True)

    data = []

    _, test_str = get_test_id()
    log_file = open(f"log_{test_str}.txt", "w")

    for df_index, url in url_list:
        print(f"{df_index}, {url}")
        log_file.write(f"{df_index}, {url}\n")
        try:
            video_data = get_video_info(url, driver)
            video_data['df_index'] = df_index
            data.append(video_data)
        except NoSuchWindowException:
            break
        except Exception as e:
            print(e)
            log_file.write(e + '\n')

    
    with open(f"output_{test_str}.json", 'w', encoding='utf-8') as f:
        for i, video in enumerate(data):
            video["id"] = i
            json.dump(video, f, ensure_ascii=True, indent=4)
            f.write('\n')

    driver.quit()
    log_file.write(f"Finished in {time.time()-start_time}s \n")
    log_file.write("Closing, goodbye")
    log_file.close()