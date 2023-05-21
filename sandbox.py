import re
import datetime
import pandas as pd
import json
import csv
from utils import *


if __name__ == "__main__":


	ads = open("ads/ads_20230517_2238_combined.json", "w", encoding="utf-8")
	ad_attributes = ["preroll_ad_id", "preroll_ad2_id", "side_ad_site", "promoted_video_title"]

	csv_file = open("ads/preroll_ads_20230517_2238_combined.csv", "w", encoding="utf-8")
	csv_writer = csv.writer(csv_file,
                            delimiter = ",",
                            quotechar = '"',
                            quoting = csv.QUOTE_MINIMAL,
                           lineterminator = "\n")

	drops = ['video_id', 'video_title', 'video_url', 'channel_name', 'channel_id', 'video_genre', 'video_description',
		'date_uploaded', 'likes', 'views','comment_count', 'preroll_ad_reasons', 'preroll_ad_id', 'preroll_ad2_id', 'preroll_ad2_reasons',
		'side_ad_img', 'side_ad_reasons', 'promoted_video_channel', 'promoted_video_reasons', 'promoted_video_info', 'id',]

	non_preroll = ["side_ad_site", "side_ad_text", "side_ad_info", "promoted_video_title", "promoted_video_url"]


	count = 0
	with open("output/output_20230517_2238_combined.json", 'r', encoding="utf-8") as f:
		for _ in range(3):
			next(f)
		for line in f:
			json_data = json.loads(line)
			if 'video_title' in json_data:
				for att in ad_attributes:
					if json_data[att]:
						json.dump(json_data, ads, ensure_ascii=True)
						ads.write('\n')
						
						for cate in drops + non_preroll:
							json_data.pop(cate, None)

						header = ["preroll_ad_video_url","preroll_ad_site","preroll_ad_advertiser", "preroll_ad_location", "df_index"]
						header2 = ["preroll_ad2_video_url","preroll_ad2_site","preroll_ad2_info"]
						if count == 0:
							csv_writer.writerow(header)

						if json_data["preroll_ad_video_url"]:
							if json_data['preroll_ad_info']:
								advertiser, loc = json_data['preroll_ad_info']
							data = [json_data["preroll_ad_video_url"], json_data["preroll_ad_site"], advertiser, loc, json_data["df_index"]]
							csv_writer.writerow(data)

						if json_data["preroll_ad2_video_url"]:
							if json_data['preroll_ad2_info']:
								advertiser, loc = json_data['preroll_ad2_info']
							data = [json_data["preroll_ad2_video_url"], json_data["preroll_ad2_site"], advertiser, loc, json_data["df_index"]]
							csv_writer.writerow(data)

						count +=1
						break


	f.close()
	ads.close()
	csv_file.close()

	# wonder if sumblime is injecting "open file" character since would get error if running 2 snippets together
	# fix by generating ads.json, view + save the ads.json file, then run the loads
	
	with open("ads/ads_20230517_2238_combined.json",'r', encoding="utf-8") as f:
		count = 0
		for line in f:
			try:
				data = json.loads(line)
				count += 1
			except:
				# print(line)
				print(count)
			
			
	# df = pd.read_csv("ads/ads_20230517_2238_combined.csv")
	# df.drop(['video_id', 'video_title', 'video_url', 'channel_name', 'channel_id', 'video_genre', 'video_description',
	# 	'date_uploaded', 'likes', 'views','comment_count', 'preroll_ad_reasons', 'preroll_ad_id', 'preroll_ad2_id', 'preroll_ad2_reasons',
	# 	'side_ad_img', 'side_ad_reasons', 'promoted_video_channel', 'promoted_video_reasons', 'promoted_video_info', 'id'],
	# 	 axis=1, inplace=True)
	# print(df)
	# df.to_csv("ads/ads_20230517_2238_combined.csv")

	project_name = "dontcrimeme"
	bucket_name = "youtube-ads-2023"
	# upload_from_directory(project_name, bucket_name, "UserData_catmaimx/", "UserData_catmaimx/")



