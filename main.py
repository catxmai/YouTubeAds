from get_video_info import get_video_info
from video_controls import *
from utils import *

import pandas as pd
import json
import time 
import traceback
import os

from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchWindowException

if __name__ == "__main__":
    start_time = time.time()
    df = pd.read_csv("control_videos_clean.csv")

    url_list = [
        (df_index,"https://www.youtube.com/watch?v="+ i['videoid']) for df_index, i in df[127:150].iterrows()
    ]

    # If no config.json, leave empty e.g. driver = create_driver("", headless=False)
    driver = create_driver("config.json", headless=False)

    if os.path.exists('logs') and os.path.exists('output') and os.path.exists('gcp_logs'):
        pass
    else:
        os.makedirs('logs')
        os.makedirs('output')
        os.makedirs('gcp_logs')

    # generate timestamp to name the log and output file
    _, test_str = get_test_id()
    log_filename = f"logs/log_{test_str}.txt"
    output_filename = f"output/output_{test_str}.json"
    gcp_log_filename = f"gcp_logs/gcp_log_{test_str}.json"


    log_file = open(log_filename, "w")

    with open(output_filename, 'w', encoding='utf-8') as f:
        i = 0

        for df_index, url in url_list:
            print(f"{df_index}, {url}")
            log_file.write(f"{df_index}, {url}\n")

            try:
                video_data = get_video_info(url, driver)
                video_data['df_index'] = df_index
                video_data["id"] = i
                json.dump(video_data, f, ensure_ascii=True)
                f.write('\n')
                # force write to disk. relatively expensive but data is more important
                f.flush()
                os.fsync(f)

            except NoSuchWindowException:
                break
            except Exception as e:
                print(e)
                log_file.write(str(type(e)) + '\n')
                log_file.write(str(e) + '\n')
                log_file.write(traceback.format_exc() + '\n')
                log_file.flush()
                os.fsync(log_file)
                pass
            finally:
                i += 1


    f.close()
    driver.quit()
    log_file.write(f"Finished in {time.time()-start_time}s \n")
    log_file.write("Closing, goodbye")
    log_file.close()


    # Upload log and output to gcp
    gcp_log = open(gcp_log_filename, "w")
    project_name = "dontcrimeme"
    bucket_name = "youtube-ads-2023"
    source_files = [output_filename, log_filename]

    for file in source_files:
        try:
            upload_blob(project_name, bucket_name, file, file)
            gcp_log.write(f"uploaded {file} to {bucket_name}/{file} \n")
        except Exception as e:
            gcp_log.write(str(type(e)) + '\n')
            gcp_log.write(str(e) + '\n')
            gcp_log.write(traceback.format_exc() + '\n')
            gcp_log.flush()
            os.fsync(gcp_log)
