import re
import datetime

def get_test_id():
    # Generates an id for scraping run based on system time
    d = datetime.datetime.now()
    test_str = '{date:%Y%m%d_%H%M}'.format(date = d)
    test_id = int('{date:%Y%m%d%H%M%S}'.format(date = d))

    return test_id, test_str

if __name__ == "__main__":

	url = "https://www.youtube.com/watch?v=AwO-om6UazY"
	pattern = r"(?<=watch\?v=).{11}" #capture anything with 11-length after watch?v=
	match = re.search(pattern, url)

	print(match[0])

	print(get_test_id())