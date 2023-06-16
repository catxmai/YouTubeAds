import re
import datetime
import pandas as pd
import json
import csv
from utils import *


if __name__ == "__main__":

	project_name = "dontcrimeme"
	bucket_name = "youtube-ads-2023"

	# upload_from_directory(project_name, bucket_name, "UserData_catmaimx/", "UserData_catmaimx/")
	upload_blob(project_name, bucket_name, "output/output_20230615_2208.json", "output/output_20230615_2208.json")

	# driver = create_driver("config.json", headless=False)
	# collect_interests(driver)
	# collect_brands(driver)

	# output = open(f"output_20230616_0406.json", "w", encoding="utf-8")

	# with open(f"output/output_20230616_0405.json", 'r', encoding="utf-8") as f:
	# 	for _ in range(3):
	# 		next(f)
	# 	for line in f:
	# 		json_data = json.loads(line)
	# 		json_data["id"] = json_data["id"] - 12000
	# 		json.dump(json_data, output, ensure_ascii=True)
	# 		output.write('\n')
	# output.close()
