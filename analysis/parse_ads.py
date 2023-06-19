import re
import datetime
import pandas as pd
import json
import csv
import os


if __name__ == "__main__":

	# go up one dir
	os.chdir('..')

	# CHANGE THIS
	id = "20230615_2208"
	


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


	ad_attributes = ["preroll_ad_id", "preroll_ad2_id", "side_ad_site", "side_ad_img", "promoted_video_title"]
	side_header = ["side_ad_img","side_ad_site", "side_ad_text", "side_ad_advertiser", "side_ad_location", "id"] 
	preroll_header = ["preroll_ad_video_url","preroll_ad_site","preroll_ad_advertiser", "preroll_ad_location", "id"]

	vid_count, unavailable_count, ad_count, preroll_count, side_count, promoted_count = 0, 0, 0, 0, 0, 0

	with open(f"output/output_{id}.json", 'r', encoding="utf-8") as f:
		for _ in range(3):
			next(f)
		for line in f:
			line = line.replace("This link opens in new tab", "")
			json_data = json.loads(line)
			if 'video_title' in json_data:
				vid_count += 1
				for att in ad_attributes:
					if json_data[att]:
						json.dump(json_data, ads, ensure_ascii=True)
						ads.write('\n')	

						if ad_count == 0:
							side_ad_csv_writer.writerow(side_header)
							preroll_ad_csv_writer.writerow(preroll_header)

						if json_data["side_ad_img"]:
							side_count += 1
							if json_data['side_ad_info']:
								advertiser, loc = json_data['side_ad_info']
							data = [json_data["side_ad_img"], json_data["side_ad_site"], json_data["side_ad_text"], advertiser, loc, json_data["id"]]
							side_ad_csv_writer.writerow(data)

						if json_data["preroll_ad_id"] and json_data["preroll_ad_id"] != json_data["video_id"]:
							preroll_count += 1
							if json_data['preroll_ad_info']:
								advertiser, loc = json_data['preroll_ad_info']
							data = [json_data["preroll_ad_video_url"], json_data["preroll_ad_site"], advertiser, loc, json_data["id"]]

							preroll_ad_csv_writer.writerow(data)


						if json_data["preroll_ad2_id"] and json_data["preroll_ad2_id"] != json_data["video_id"]:
							preroll_count += 1
							if json_data['preroll_ad2_info']:
								advertiser, loc = json_data['preroll_ad2_info']
							data = [json_data["preroll_ad2_video_url"], json_data["preroll_ad2_site"], advertiser, loc, json_data["id"]]

							preroll_ad_csv_writer.writerow(data)


						if json_data["promoted_video_title"]:
							promoted_count += 1


						ad_count +=1
						break

			else:
				unavailable_count += 1

	print(f"Unavailable videos: {unavailable_count}")
	print(f"Available videos: {vid_count}")
	print(f"Preroll ads: {preroll_count}")
	print(f"Side ads: {side_count}")
	print(f"Promoted videos: {promoted_count}")
	print(f"Number of ads: {preroll_count+side_count+promoted_count}")
	print(f"Number of videos with one or more ads: {ad_count}")


	f.close()
	ads.close()
	side_ad_csv_file.close()
	preroll_ad_csv_file.close()