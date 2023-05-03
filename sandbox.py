import re
import datetime


if __name__ == "__main__":

	url = "https://www.youtube.com/watch?v=AwO-om6UazY"
	pattern = r"(?<=watch\?v=).{11}" #capture anything with 11-length after watch?v=
	match = re.search(pattern, url)

	print(match[0])