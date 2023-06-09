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

	driver = create_driver("config.json", headless=True)
	collect_interests(driver)
	collect_brands(driver)