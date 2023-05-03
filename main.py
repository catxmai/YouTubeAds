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
        "https://www.youtube.com/watch?v="+ i for i in df['videoid'][143:243]
    ]

    driver = create_driver("config.json", headless=True)

    data = []

    _, test_str = get_test_id()
    # Logging
    log_file = open(f"log_{test_str}.txt", "w")

    for i, url in enumerate(url_list):
        print(f"{i}, {url}")
        log_file.write(f"{i}, {url}\n")
        try:
            data.append(get_video_info(url, driver))
        except ElementNotInteractableException:
            pass
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