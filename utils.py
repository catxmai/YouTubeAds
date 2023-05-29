from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from google.cloud import storage

import json
import time
import datetime
import glob
import os


def upload_blob(project_name, bucket_name, source_file_name, destination_blob_name):
    # upload to gcp

    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)


def upload_from_directory(project_name, bucket_name, source_dir, destination_dir):

    rel_paths = glob.glob(source_dir + '**', recursive=True)
    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(bucket_name)
    for local_file in rel_paths:
        remote_path = f'{destination_dir}{"/".join(local_file.split(os.sep)[1:])}'
        if os.path.isfile(local_file):
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_file)


def create_driver(config_path="", headless=True):
    # config is a json file
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1540,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--mute-audio")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    if headless:
        options.add_argument("--headless")

    if config_path:
        config = {}
        config_f = open(config_path, 'r')
        config_json = json.load(config_f)
        config_f.close()
        config['username'] = config_json['username']
        config['password'] = config_json['password']
        config['user_data'] = config_json['user_data']
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


def get_test_id():
    # Generates an id for scraping run based on system time
    d = datetime.datetime.now()
    test_str = '{date:%Y%m%d_%H%M}'.format(date = d)
    test_id = int('{date:%Y%m%d%H%M%S}'.format(date = d))

    return test_id, test_str


def collect_interests(driver):
    
    driver.get("https://myadcenter.google.com/customize")
    interest_cards = driver.find_elements(By.CLASS_NAME, "YcxLyd")
    interests = [i.get_attribute("innerHTML") for i in interest_cards]

    return interest_cards
