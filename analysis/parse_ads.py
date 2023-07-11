import re
import pandas as pd
import json
import csv
import os

# go up one dir
if not os.path.exists("ads/"):
	os.chdir("..")

conspiracy_ids = ["20230527_2230","20230530_1949", "20230615_2208",
                 "20230518_1957", "20230526_1750", "20230620_2248",
                 "20230621_2131", "20230622_2327", "20230623_2257"]

mainstream_ids = ["20230529_2213", "20230606_0332", "20230619_1605",
                  "20230601_1751", "20230606_1947", ]

run_ids = conspiracy_ids + mainstream_ids

def get_preroll_tag(info, database):
    # info is a tuple (video_url, site)
    
    url, site = info
    
    url_db = database[database["preroll_ad_video_url"]==url]
    if len(url_db) != 0:
        return url_db.iloc[0]["tag"], url_db.iloc[0]["is_scam"]
    
    site_db = database[database["preroll_ad_site"]==site]
    if len(site_db) != 0:
        return site_db.iloc[0]["tag"], site_db.iloc[0]["is_scam"]
    
    return None, None


def get_side_tag(info, database):
    # info is a tuple (side_ad_img, site)
    
    img, site = info
    
    img_db = database[database["side_ad_img"]==img]
    if len(img_db) != 0:
        return img_db.iloc[0]["tag"], img_db.iloc[0]["is_scam"]
    
    site_db = database[database["side_ad_site"]==site]
    if len(site_db) != 0:
        return site_db.iloc[0]["tag"], site_db.iloc[0]["is_scam"]
    
    return None, None


def build_preroll_database():

    preroll_db = pd.read_excel("ads/preroll_ads_tagging.xlsx", sheet_name = run_ids)
    dfs = []

    for run_id in run_ids:
        preroll_df = preroll_db.get(run_id)
        preroll_df = preroll_df[preroll_df['preroll_ad_video_url'].notna()]
        preroll_df['run_id'] = run_id
        dfs.append(preroll_df)

    database = pd.concat(dfs, ignore_index=True)
    return database

def build_side_database():
    
    side_db = pd.read_excel("ads/side_ads_tagging.xlsx", sheet_name = run_ids)
    dfs = []

    for run_id in run_ids:

        side_df = side_db.get(run_id)
        side_df = side_df[side_df['side_ad_img'].notna()]
        side_df['run_id'] = run_id
        dfs.append(side_df)

    database = pd.concat(dfs, ignore_index=True)
    return database


if __name__ == "__main__":

	# CHANGE THIS
	id = "0706_0227_happysquare89"

	preroll_database = build_preroll_database()
	side_database = build_side_database()
	

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
	side_header = ["side_ad_img","side_ad_site", "side_ad_text", "side_ad_advertiser", "side_ad_location", "id", "tag", "is_scam", "Notes"] 
	preroll_header = ["preroll_ad_video_url","preroll_ad_site","preroll_ad_advertiser", "preroll_ad_location", "id", "tag", "is_scam", "Notes"]

	vid_count, unavailable_count, ad_count, preroll_count, side_count, promoted_count = 0, 0, 0, 0, 0, 0

	with open(f"output/output_{id}.json", 'r', encoding="utf-8") as f:
		for _ in range(4):
			next(f)
		for line in f:
			line = line.replace("This link opens in new tab", "")
			json_data = json.loads(line)
			if 'video_title' not in json_data:
				unavailable_count += 1
			else:
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
					
							side_ad_img, side_ad_site = json_data['side_ad_img'], json_data['side_ad_site']
							tag, is_scam = get_side_tag((side_ad_img, side_ad_site), side_database)

							data = [side_ad_img, side_ad_site, json_data["side_ad_text"], advertiser, loc, json_data["id"], tag, is_scam, ""]
							side_ad_csv_writer.writerow(data)

						if json_data["preroll_ad_id"] and json_data["preroll_ad_id"] != json_data["video_id"]:
							preroll_count += 1
							if json_data['preroll_ad_info']:
								advertiser, loc = json_data['preroll_ad_info']

							preroll_ad_video_url, preroll_ad_site = json_data["preroll_ad_video_url"], json_data["preroll_ad_site"]
							tag, is_scam = get_preroll_tag((preroll_ad_video_url, preroll_ad_site), preroll_database)

							data = [preroll_ad_video_url, preroll_ad_site, advertiser, loc, json_data["id"], tag, is_scam, ""]
							preroll_ad_csv_writer.writerow(data)


						if json_data["preroll_ad2_id"] and json_data["preroll_ad2_id"] != json_data["video_id"]:
							preroll_count += 1
							if json_data['preroll_ad2_info']:
								advertiser, loc = json_data['preroll_ad2_info']

							preroll_ad2_video_url, preroll_ad2_site = json_data["preroll_ad2_video_url"], json_data["preroll_ad2_site"]
							tag, is_scam = get_preroll_tag((preroll_ad2_video_url, preroll_ad2_site), preroll_database)

							data = [preroll_ad2_video_url, preroll_ad2_site, advertiser, loc, json_data["id"], tag, is_scam, ""]
							preroll_ad_csv_writer.writerow(data)


						if json_data["promoted_video_title"]:
							promoted_count += 1


						ad_count +=1
						break
				

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