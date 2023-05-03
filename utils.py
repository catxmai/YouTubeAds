from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import json
import time
import datetime

def create_driver(config_path=""):
    # config is a json file
    if config_path:
        config = {}
        config_f = open(config_path, 'r')
        config_json = json.load(config_f)
        config_f.close()
        config['username'] = config_json['username']
        config['password'] = config_json['password']
        config['user_data'] = config_json['user_data']
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1540,1080")
    options.add_argument("--no-sandbox")
    if config['user_data']:
        options.add_argument("user-data-dir=" + config['user_data'])

    driver = webdriver.Chrome(options = options)

    try:
        youtube_login(driver, config['username'], config['password'] )
    except:
        pass
    return driver


def youtube_login(driver: webdriver.Chrome, username, password):

    signinurl = "https://accounts.google.com/signin/v2/identifier?service=youtube"
    driver.get(signinurl)

    uEntry = driver.find_element("id","identifierId")
    uEntry.clear()
    uEntry.send_keys(username)

    nextButton = driver.find_element('xpath','//span[text()="Next"]')
    nextButton = nextButton.find_element('xpath','./..')
    nextButton.click()

    WebDriverWait(driver, 4).until(EC.presence_of_element_located(('id', 'password')))
    pEntry = driver.find_element('id',"password")
    pEntry = pEntry.find_element('xpath','.//input[@type="password"]')
    pEntry.clear()
    pEntry.send_keys(password)
    time.sleep(1)
    pEntry.send_keys(Keys.RETURN)
    time.sleep(2)

def remove_prefix(instr, prefix):
    # Remove a substr from the start of a string
    # Returns new string without prefix
    if instr.startswith(prefix):
        return instr[len(prefix):]
    else:
        return instr[:]


def extract_urls(text: str) -> list:
    """
    Parameters
    ----------
    text: a string to be parsed for urls

    Returns
    -------
    urls: a list of urls extracted from the input string

    """

    pattern: str = r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
    matches: Any = re.finditer(pattern, text)
    urls: list = [match.group() for match in matches]

    return urls


def get_test_id():
    # Generates an id for scraping run based on system time
    d = datetime.datetime.now()
    test_str = '{date:%Y%m%d_%H%M}'.format(date = d)
    test_id = int('{date:%Y%m%d%H%M%S}'.format(date = d))

    return test_id, test_str
