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

if __name__ == "__main__":
    start_time = time.time()

    # CHANGE THESE BEFORE RUNNING
    running_vm = False # on gcp
    headless = False # running without gui
    config_path = "config.json" # If no config.json, leave ""
    # video_list = "conspiracy_videos_0_500000.csv"
    video_list = "control_videos_clean.csv"
    

    df = pd.read_csv(video_list)
    url_list = [
        (df_index,"https://www.youtube.com/watch?v="+ i['videoid']) for df_index, i in df[129:140].iterrows()
    ]

    
    driver = create_driver(config_path, headless=headless)

    dirs = ['logs', 'output', 'gcp_logs', 'pretty_output']
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)

    # generate timestamp to name the log and output file
    _, test_str = get_test_id()
    log_filename = f"logs/log_{test_str}.txt"
    output_filename = f"output/output_{test_str}.json"
    gcp_log_filename = f"gcp_logs/gcp_log_{test_str}.json"
    pretty_output_filename = f"pretty_output/pretty_output_{test_str}.json"

    log_file = open(log_filename, "w")
    pretty_output = open(pretty_output_filename, "w")

    # Log username and dataset being used
    username = "anonymous"
    if config_path:
        config_f = open(config_path, 'r')
        config_json = json.load(config_f)
        config_f.close()
        username = config_json['username']
    
    log_file.write(f"Using {username} account \n")
    log_file.write(f"Using {video_list} \n")
    log_file.write(f"Running on vm: {running_vm} \n")

    pretty_output.write(f"Using {username} account \n")
    pretty_output.write(f"Using {video_list} \n")
    pretty_output.write(f"Running on vm: {running_vm} \n")


    with open(output_filename, 'w', encoding='utf-8') as output:
        output.write(f"Using {username} account \n")
        output.write(f"Using {video_list} \n")
        output.write(f"Running on vm: {running_vm} \n")

        i = 0

        for df_index, url in url_list:
            print(f"{df_index}, {url}")
            log_file.write(f"{df_index}, {url}\n")

            try:
                video_data = get_video_info(url, driver)
                video_data['df_index'] = df_index
                video_data["id"] = i

                json.dump(video_data, output, ensure_ascii=True)
                output.write('\n')
                # force write to disk. relatively expensive but data is more important
                output.flush()
                os.fsync(output)

                # pretty output
                json.dump(video_data, pretty_output, ensure_ascii=True, indent=4)
                pretty_output.write('\n')
                pretty_output.flush()
                os.fsync(pretty_output)

            except (NoSuchWindowException, WebDriverException) as e:
                log_file.write("Browser was closed or connection was lost \n")
                log_file.write(traceback.format_exc() + '\n')
                break
            except Exception as e:
                print(traceback.format_exc())
                log_file.write(traceback.format_exc() + '\n')
                log_file.flush()
                os.fsync(log_file)
                pass
            finally:
                i += 1


    output.close()
    pretty_output.close()
    driver.quit()
    log_file.write(f"Finished in {time.time()-start_time}s \n")
    log_file.write("Closing, goodbye")
    log_file.close()


    # Upload log and output to gcp
    # if not is_test:
    #     gcp_log = open(gcp_log_filename, "w")
    #     project_name = "dontcrimeme"
    #     bucket_name = "youtube-ads-2023"
    #     source_files = [output_filename, log_filename]

    #     for file in source_files:
    #         try:
    #             upload_blob(project_name, bucket_name, file, file)
    #             gcp_log.write(f"uploaded {file} to {bucket_name}/{file} \n")
    #         except Exception as e:
    #             gcp_log.write(traceback.format_exc() + '\n')
    #             gcp_log.flush()
    #             os.fsync(gcp_log)

    #     gcp_log.close()
