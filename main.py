from get_video_info import get_video_info
from video_controls import *
from utils import *

import pandas as pd
import json
import time 
import traceback
import os

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchWindowException

VIDEO_COUNT = 0

def run_video_list(config_path, mode, sleep, video_list, start_index, end_index, output, log_file):
    global VIDEO_COUNT
    
    df = pd.read_csv(video_list)
    url_list = [
        (df_index,"https://www.youtube.com/watch?v="+ i['videoid']) for df_index, i in df[start_index:end_index].iterrows()
    ]

    driver = create_driver(config_path, headless=headless) 

    for df_index, url in url_list:
        log_file.write(f"{df_index}, {url}\n")

        try:
            video_data = get_video_info(url, driver, mode=mode, sleep=sleep)
            video_data["df_index"] = df_index
            video_data["id"] = VIDEO_COUNT

            json.dump(video_data, output, ensure_ascii=True)
            output.write('\n')
            # force write to disk. relatively expensive but data is more important
            output.flush()
            os.fsync(output)
            VIDEO_COUNT += 1

        except (NoSuchWindowException, WebDriverException) as e:
            log_file.write("Browser was closed or connection was lost \n")
            log_file.write("Restarting driver \n")
            driver.quit()
            run_video_list(config_path, mode, sleep, video_list, start_index+VIDEO_COUNT, end_index,
                           output, log_file)
            break

        except Exception as e:
            log_file.write("UNEXPECTED")
            log_file.write(traceback.format_exc() + '\n')
            log_file.flush()
            os.fsync(log_file)


if __name__ == "__main__":
    start_time = time.time()

    # CHANGE THESE BEFORE RUNNING
    ##########################################################
    running_vm = False # on gcp
    headless = True # running without gui
    mode = "collect" # mode is "prime" or "collect"
    sleep = 0 # stay an extra number of seconds per video
    config_path = "config.json" # If no config.json, leave ""
    # video_list = "conspiracy_videos_0_500000.csv"
    video_list = "control_videos_clean.csv"
    start_index = 120
    end_index = 130
    ##########################################################


    dirs = ['logs', 'output']
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)

    # generate timestamp to name the log and output file
    _, test_str = get_test_id()
    log_filename = f"logs/log_{test_str}.txt"
    output_filename = f"output/output_{test_str}.json"
    log_file = open(log_filename, "w")
    output = open(output_filename, 'w', encoding='utf-8')

    # Log username and dataset being used
    username = "anonymous"
    if config_path:
        config_f = open(config_path, 'r')
        config_json = json.load(config_f)
        config_f.close()
        username = config_json['username']
    
    log_file.write(f"Using {username} account \n")
    log_file.write(f"Using {video_list}[{start_index}:{end_index}]\n")
    log_file.write(f"Running on vm: {running_vm} \n")

    output.write(f"Using {username} account \n")
    output.write(f"Using {video_list}[{start_index}:{end_index}]\n")
    output.write(f"Running on vm: {running_vm} \n")

    # Start collecting data
    while VIDEO_COUNT < (end_index-start_index):
        run_video_list(config_path, mode, sleep, video_list,
                       start_index+VIDEO_COUNT, end_index, output, log_file)
        
    output.close()
    log_file.write(f"Finished in {time.time()-start_time}s \n")
    log_file.write("Closing, goodbye")
    log_file.close()


    # Upload log and output to gcp
    project_name = "dontcrimeme"
    bucket_name = "youtube-ads-2023"
    source_files = [output_filename, log_filename]

    for file in source_files:
        upload_blob(project_name, bucket_name, file, file)
