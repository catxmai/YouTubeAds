import re
import datetime
import pandas as pd
import json


if __name__ == "__main__":

	with open("output/output_20230509_1746.json", 'r') as f:
		for line in f:
			json_data = json.loads(line)
			print(json_data["side_ad_reasons"])

	# with open("output/output_20230503_1841.json", 'r') as f:
	# 	i = 0
	# 	for line in f:
	# 		while i < 1:
	# 			print(line)
	# 			i += 1

			





