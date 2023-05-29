import re
import datetime
import pandas as pd
import json
import csv
from utils import *


if __name__ == "__main__":


	id = "20230518_1957"
	ads = open(f"ads/ads_{id}.json", "w", encoding="utf-8")
	side_ad_csv_file = open(f"ads/side_ads_{id}.csv", "w", encoding="utf-8")
	preroll_ad_csv_file = open(f"ads/preroll_ads_{id}.csv", "w", encoding="utf-8")
	side_ad_csv_writer = csv.writer(side_ad_csv_file,
                            delimiter = ",",
                            quotechar = '"',
                            quoting = csv.QUOTE_MINIMAL,
                           lineterminator = "\n")
	preroll_ad_csv_writer = csv.writer(preroll_ad_csv_file,
							delimiter = ",",
                            quotechar = '"',
                            quoting = csv.QUOTE_MINIMAL,
                           lineterminator = "\n")


	ad_attributes = ["preroll_ad_id", "preroll_ad2_id", "side_ad_site", "promoted_video_title"]


	drops = ['video_id', 'video_title', 'video_url', 'channel_name', 'channel_id', 'video_genre', 'video_description',
		'date_uploaded', 'likes', 'views','comment_count', 'preroll_ad_reasons', 'preroll_ad_id', 'preroll_ad2_id', 'preroll_ad2_reasons',
		'promoted_video_channel', 'promoted_video_reasons', 'promoted_video_info', 
		'side_ad_img', 'side_ad_reasons', 'promoted_video_channel', 'promoted_video_reasons', 'promoted_video_info', ]


	non_preroll = ["side_ad_site", "side_ad_text", "side_ad_info", "promoted_video_title", "promoted_video_url", "side_ad_img", 'side_ad_reasons']

	side_ad_attributes = ["side_ad_site", "side_ad_text", "side_ad_img"]


	count = 0

	with open(f"output/output_{id}.json", 'r', encoding="utf-8") as f:
		for _ in range(3):
			next(f)
		for line in f:
			json_data = json.loads(line)
			if 'video_title' in json_data:
				for att in ad_attributes:
					if json_data[att]:
						json.dump(json_data, ads, ensure_ascii=True)
						ads.write('\n')	

						side_header = ["side_ad_img","side_ad_site", "side_ad_text", "side_ad_advertiser", "side_ad_location", "id"] 
						preroll_header = ["preroll_ad_video_url","preroll_ad_site","preroll_ad_advertiser", "preroll_ad_location", "id"]
						header = ["preroll_ad_video_url","preroll_ad_site","preroll_ad_advertiser", "preroll_ad_location", "id"]
						header2 = ["preroll_ad2_video_url","preroll_ad2_site","preroll_ad2_info"]

						if count == 0:
							side_ad_csv_writer.writerow(side_header)
							preroll_ad_csv_writer.writerow(preroll_header)

						if json_data["side_ad_site"]:
							if json_data['side_ad_info']:
								advertiser, loc = json_data['side_ad_info']
							data = [json_data["side_ad_img"], json_data["side_ad_site"], json_data["side_ad_text"], advertiser, loc, json_data["id"]]
							side_ad_csv_writer.writerow(data)

						if json_data["preroll_ad_video_url"]:
							if json_data['preroll_ad_info']:
								advertiser, loc = json_data['preroll_ad_info']
							data = [json_data["preroll_ad_video_url"], json_data["preroll_ad_site"], advertiser, loc, json_data["id"]]

							preroll_ad_csv_writer.writerow(data)


						if json_data["preroll_ad2_video_url"]:
							if json_data['preroll_ad2_info']:
								advertiser, loc = json_data['preroll_ad2_info']
							data = [json_data["preroll_ad2_video_url"], json_data["preroll_ad2_site"], advertiser, loc, json_data["id"]]

							preroll_ad_csv_writer.writerow(data)


						count +=1
						break


	f.close()
	ads.close()
	side_ad_csv_file.close()
	preroll_ad_csv_file.close()

	project_name = "dontcrimeme"
	bucket_name = "youtube-ads-2023"
	# upload_from_directory(project_name, bucket_name, "UserData_catmaimx/", "UserData_catmaimx/")



