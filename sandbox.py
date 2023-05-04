import re
import datetime
import pandas as pd


if __name__ == "__main__":

	df = pd.read_csv("control_videos_clean.csv")
	for i, row in df[100:200].iterrows():
		print(i)
		print(row['videoid'])


