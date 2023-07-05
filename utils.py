from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *

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

    config = {}
    if config_path:
        config_f = open(config_path, 'r')
        config = json.load(config_f)
        config_f.close()
        if config['user_data']:
            options.add_argument("user-data-dir=" + config['user_data'])
        
    driver = webdriver.Chrome(options = options)

    try:
        youtube_login(driver, config['username'], config['password'])
    except:
        pass

    if 'username' in config:
        check_login(driver, config['username']+"@gmail.com")

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



def check_login(driver, email):
    driver.get("https://www.gmail.com")
    time.sleep(1)
    if email not in driver.title:
        print("Login not successful")
        # Assuming headless is False, can do verification step here
        time.sleep(10000)


def get_test_id():
    # Generates an id for scraping run based on system time
    d = datetime.datetime.now()
    test_str = '{date:%m%d_%H%M}'.format(date = d)

    return test_str


def collect_interests(driver):
    
    try:
        driver.get("https://myadcenter.google.com/customize")
        interest_cards = driver.find_elements(By.CLASS_NAME, "YcxLyd")
        interests = [i.get_attribute("innerHTML") for i in interest_cards]

        return interests
    except (IndexError, NoSuchElementException) as e:
        return None


def collect_brands(driver):

    try:
        driver.get("https://myadcenter.google.com/customize")
        brand_button = driver.find_elements(By.CSS_SELECTOR, ".VfPpkd-AznF2e.WbUJNb.FEsNhd")[1]
        tab_name = brand_button.find_element(By.CSS_SELECTOR, ".VfPpkd-jY41G-V67aGc").get_attribute("innerHTML")

        if tab_name == "Brands":
            driver.execute_script("arguments[0].click();", brand_button)
            time.sleep(1)
            brand_list = driver.find_elements(By.CLASS_NAME, "ByHevf")
            brands = [i.get_attribute("innerHTML") for i in brand_list]
        else:
            return None

        return brands
    except (IndexError, NoSuchElementException) as e:
        return None 
    

def turn_on_ad_personalization(driver):
    time.sleep(1)
    driver.get("https://myadcenter.google.com/")

    try:
        toggle_button = driver.find_element(By.CSS_SELECTOR, ".ie6Hvb-eIzVJe-LgbsSe.nOY0Nb.sly7Kb.DmnIhf")
        driver.execute_script("arguments[0].click();", toggle_button)
    except NoSuchElementException:
        driver.find_element(By.CSS_SELECTOR, ".ie6Hvb-eIzVJe-LgbsSe.nOY0Nb.sly7Kb.YFjIb")
        print("Ad personalization is already on")
        return
    
    time.sleep(1)

    possible_buttons = driver.find_elements(By.CSS_SELECTOR, "button.mUIrbf-LgbsSe.mUIrbf-LgbsSe-OWXEXe-dgl2Hf")
    found = False
    for button in possible_buttons:
        if button.get_attribute("data-mdc-dialog-action") == "ok":
            driver.execute_script("arguments[0].click();", button)
            found = True
            break
    
    if not found:
        raise AssertionError("turn on button is not accessible")
    
    time.sleep(1)
    try:
        got_it_button = driver.find_element("xpath", '//span[text()="Got it"]')
        got_it_button.click()
    except NoSuchElementException:
        pass

    print("Ad personalization is turned on")
    

def turn_off_ad_personalization(driver):
    time.sleep(1)
    driver.get("https://myadcenter.google.com/")

    try:
        toggle_button = driver.find_element(By.CSS_SELECTOR, ".ie6Hvb-eIzVJe-LgbsSe.nOY0Nb.sly7Kb.YFjIb")
        driver.execute_script("arguments[0].click();", toggle_button)
    except NoSuchElementException:
        driver.find_element(By.CSS_SELECTOR, ".ie6Hvb-eIzVJe-LgbsSe.nOY0Nb.sly7Kb.DmnIhf")
        print("Ad personalization is already off")
        return
    
    time.sleep(1)

    possible_buttons = driver.find_elements(By.CSS_SELECTOR, "button.mUIrbf-LgbsSe.mUIrbf-LgbsSe-OWXEXe-dgl2Hf")
    found = False
    for button in possible_buttons:
        if button.get_attribute("data-mdc-dialog-action") == "ok":
            driver.execute_script("arguments[0].click();", button)
            found = True
            break
    
    if not found:
        raise AssertionError("turn off button is not accessible")
    
    time.sleep(1)
    try:
        got_it_button = driver.find_element("xpath", '//span[text()="Got it"]')
        got_it_button.click()
    except NoSuchElementException:
        pass
    
    print("Ad personalization is turned off")
    
    

def turn_on_activity(driver):
    activity_controls_url = "https://myactivity.google.com/activitycontrols?settings=search"
    time.sleep(1)
    driver.get(activity_controls_url)

    try:
        turn_on_button = driver.find_element("xpath", '//span[text()="Turn on"]')
        turn_on_button.click()
    except NoSuchElementException:
        driver.find_element("xpath", '//span[text()="Turn off"]')
        print("Activity is already on")
        return
    
    time.sleep(1)
    # Scroll to bottom of popup to enable Turn on activity
    popup = driver.find_element(By.CSS_SELECTOR, ".cSvfje")
    driver.execute_script("arguments[0].scroll(0, arguments[0].scrollHeight);", popup)

    time.sleep(1)

    final_button = driver.find_element(
        By.CSS_SELECTOR,
        "button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.nCP5yc.AjY5Oe.DuMIQc.LQeN7.QWgF9b",
    )
    final_button.click()

    time.sleep(1)
    try:
        got_it_button = driver.find_element("xpath", '//span[text()="Got it"]')
        got_it_button.click()
    except NoSuchElementException:
        pass

    print("Activity is turned on")



def turn_off_activity(driver):
    activity_controls_url = "https://myactivity.google.com/activitycontrols?settings=search"
    time.sleep(1)
    driver.get(activity_controls_url)

    try:
        turn_off_button = driver.find_element("xpath", '//span[text()="Turn off"]')
        turn_off_button.click()
    except NoSuchElementException:
        driver.find_element("xpath", '//span[text()="Turn on"]')
        print("Activity is already off")
        return

    time.sleep(2)
    final_button = driver.find_element(
        By.CSS_SELECTOR, "li.FFr0qd.VfPpkd-StrnGf-rymPhb-ibnC6b"
    )
    final_button.click()

    time.sleep(1)
    try:
        got_it_button = driver.find_element("xpath", '//span[text()="Got it"]')
        got_it_button.click()
    except NoSuchElementException:
        pass

    print("Activity is turned off")



def turn_off_youtube_history(driver):
    history_controls_url = "https://myactivity.google.com/product/youtube/controls"
    time.sleep(1)
    driver.get(history_controls_url)

    try:
        turn_off_button = driver.find_element("xpath", '//span[text()="Turn off"]')
        turn_off_button.click()
    except NoSuchElementException:
        driver.find_element("xpath", '//span[text()="Turn on"]')
        print("YouTube history is already off")
        return
    
    time.sleep(1)
    pause_button = driver.find_element(
        By.CSS_SELECTOR, "button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.nCP5yc.AjY5Oe.DuMIQc.LQeN7.yARu6e"
    ) 
    pause_button.click()

    time.sleep(1)
    try:
        got_it_button = driver.find_element("xpath", '//span[text()="Got it"]')
        got_it_button.click()
    except NoSuchElementException:
        pass

    print("YouTube history is turned off")


def turn_on_youtube_history(driver):
    history_controls_url = "https://myactivity.google.com/product/youtube/controls"
    time.sleep(1)
    driver.get(history_controls_url)
    
    try:
        turn_on_button = driver.find_element("xpath", '//span[text()="Turn on"]')
        turn_on_button.click()
    except NoSuchElementException:
        driver.find_element("xpath", '//span[text()="Turn off"]')
        print("YouTube history is already on")
        return

    time.sleep(1)
    try:
        final_button = driver.find_element(
            By.CSS_SELECTOR,
            "button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.nCP5yc.AjY5Oe.DuMIQc.LQeN7.yARu6e",
        )
        final_button.click()
    except NoSuchElementException:
        pass

    time.sleep(1)
    try:
        got_it_button = driver.find_element("xpath", '//span[text()="Got it"]')
        got_it_button.click()
    except NoSuchElementException:
        pass

    print("YouTube history is turned on")


def delete_activity(driver):

    activity_history_url = "https://myactivity.google.com/myactivity"
    time.sleep(1)
    driver.get(activity_history_url)

    delete_button = driver.find_element("xpath", '//span[text()="Delete"]')
    driver.execute_script("arguments[0].click();", delete_button)

    all_time_button = driver.find_element(
        By.CSS_SELECTOR, "div.cSvfje > ul > li:nth-child(3)"
    )
    all_time_button.click()

    time.sleep(2)

    delete_button = driver.find_element("xpath", '//span[text()="Delete"]')
    driver.execute_script("arguments[0].click();", delete_button)

    try:
        final_delete_button = driver.find_element(
            By.CSS_SELECTOR,
            "button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.nCP5yc.AjY5Oe.DuMIQc.LQeN7.e6p9Rc",
        )
        final_delete_button.click()
    except NoSuchElementException:
        no_activity_text = driver.find_element(By.CLASS_NAME, "oDnphc").get_attribute("innerHTML")
        if "You have no selected activity" in no_activity_text:
            print("No activity to delete")
            return
        
    time.sleep(1)
    try:
        got_it_button = driver.find_element("xpath", '//span[text()="Got it"]')
        got_it_button.click()
    except NoSuchElementException:
        pass

    print("Activity is deleted")



