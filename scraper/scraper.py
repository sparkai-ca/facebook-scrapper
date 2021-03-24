import calendar
import os
import platform
import sys
import urllib.request
import yaml
import traceback
import time
import numpy as np
import pandas as pd
import json

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

# from langdetect import detect, detect_langs


# -------------------------------------------------------------
# -------------------------------------------------------------

# Global Variables


options = webdriver.ChromeOptions()

#  Code to disable notifications pop up of Chrome Browser
options.add_argument("--disable-notifications")
options.add_argument("--disable-infobars")
options.add_argument("--mute-audio")
options.add_argument("--no-sandbox")
options.add_argument("--headless")


total_scrolls = 99999999999
current_scrolls = 0
scroll_time = 10

old_height = 0

facebook_path = "https://www.facebook.com/"

CHROMEDRIVER_BINARIES_FOLDER = "bin"

data = []



# -------------------------------------------------------------
# -------------------------------------------------------------


def scrap_posts(tag, driver):
    try:
        main_window, next_window = None, None
        main_window = driver.window_handles[0]

        main_div = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div')
        divs = main_div.find_elements_by_xpath('./*')

        print(len(divs))
        for c,div in enumerate(divs):
            try:
                print('\n---\n',c,'\n---\n')
                href = div.find_element_by_xpath('./div/div/div/div/div/div[3]/a').get_attribute('href')
                print(href)
                driver.execute_script("window.open('"+href+"');")
                next_window = driver.window_handles[1]
                driver.switch_to.window(next_window)
                time.sleep(np.random.randint(8, 10))

                
                

                params = {
                    "latitude": 52.520008,
                    "longitude": 13.404954,
                    "accuracy": 99
                    }
                driver.execute_cdp_cmd("Page.setGeolocationOverride", params)
                driver.execute_cdp_cmd("Emulation.clearGeolocationOverride", params)
                
                txt = ''
                try:
                    _text = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div[1]/div/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div[3]')
                    txt = str(_text.text)
                    print(1,'\n',txt)
                except Exception as ex1:
                    print(ex1)
                    try:
                        _text = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[3]')
                        txt = str(_text.text)
                        print(2,'\n',txt)
                    except Exception as ex2:
                        print(ex2)

                if txt!='':
                    # print(detect(txt))
                    # print(detect_langs(txt))
                    data.append((tag, txt))
                

                driver.close()
                driver.switch_to.window(main_window)
                time.sleep(np.random.randint(2, 4))

            except Exception as ex:
                print(ex)
                pass

    except Exception as ex:
        pass
        #print(ex)



# -------------------------------------------------------------
# -------------------------------------------------------------


def search_tag(tag, driver):
    try:
        tag = '#'+str(tag)
        time.sleep(np.random.randint(3, 6))
        search_field = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div[1]/div/div/label')
        search_field.find_element_by_tag_name('input')
        search_field.send_keys(tag)
        time.sleep(np.random.randint(3, 6))
        search_button = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/ul')
        search_button = search_button.find_elements_by_xpath('./*')[-1]
        search_button = search_button.find_element_by_xpath('./div/a')
        print(search_button.text)
        search_button.click()
        time.sleep(np.random.randint(3, 6))
        scroll(driver)
        time.sleep(np.random.randint(3, 6))
        posts_button = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[2]/div/div/div[2]/div[2]/a')
        posts_button.click()
        time.sleep(np.random.randint(5, 9))
        return True
    except Exception as ex:
        pass
        #print(ex)
    return False

# -------------------------------------------------------------
# -------------------------------------------------------------


def check_height(driver):
    new_height = driver.execute_script("return document.body.scrollHeight")
    return new_height != old_height


# helper function: used to scroll the page
def scroll(driver):
    global old_height
    current_scrolls = 0

    while True:
        try:
            if current_scrolls == total_scrolls:
                print(current_scrolls)
                return


            old_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, scroll_time, 0.05).until(
                lambda driver: check_height(driver)
            )
            current_scrolls += 1
        except TimeoutException:
            #print(traceback.format_exc())
            break
    return



# -------------------------------------------------------------
# -------------------------------------------------------------



def safe_find_element_by_id(driver, elem_id):
    try:
        return driver.find_element_by_id(elem_id)
    except NoSuchElementException:
        #print(traceback.format_exc())
        return None


def login(email, password, driver):
    """ Logging into our own profile """

    time.sleep(np.random.randint(4, 6))

    try:

        fb_path = facebook_path
        driver.get(fb_path)
        
        driver.maximize_window()

        try:
            driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div/div/div[3]/button[2]').click()
            time.sleep(np.random.randint(3, 5))
        except Exception as ex:
            try:
                driver.find_element_by_id('u_0_j_EX').click()
                time.sleep(np.random.randint(3, 5))
            except Exception as ex:
                print(ex)

        # filling the form
        driver.find_element_by_id("email").send_keys(email)
        driver.find_element_by_id("pass").send_keys(password)

        try:
            # clicking on login button
            driver.find_element_by_id("loginbutton").click()
        except NoSuchElementException:
            #print(traceback.format_exc())
            # Facebook new design
            driver.find_element_by_name("login").click()

        # if your account uses multi factor authentication
        mfa_code_input = safe_find_element_by_id(driver, "approvals_code")

        if mfa_code_input is None:
            return

        mfa_code_input.send_keys(input("Enter MFA code: "))
        driver.find_element_by_id("checkpointSubmitButton").click()

        # there are so many screens asking you to verify things. Just skip them all
        while safe_find_element_by_id(driver, "checkpointSubmitButton") is not None:
            dont_save_browser_radio = safe_find_element_by_id(driver, "u_0_3")
            if dont_save_browser_radio is not None:
                dont_save_browser_radio.click()

            driver.find_element_by_id("checkpointSubmitButton").click()

    except Exception as ex:
        print(ex,traceback.format_exc())
        print("There's some error in log in.")
        print(sys.exc_info()[0])
        exit(1)


def get_driver():
    try:
        platform_ = platform.system().lower()
        chromedriver_versions = {
            "linux": os.path.join(
                os.getcwd(), CHROMEDRIVER_BINARIES_FOLDER, "chromedriver_linux64",
            ),
            "darwin": os.path.join(
                os.getcwd(), CHROMEDRIVER_BINARIES_FOLDER, "chromedriver_mac64",
            ),
            "windows": os.path.join(
                os.getcwd(), CHROMEDRIVER_BINARIES_FOLDER, "chromedriver_win32.exe",
            ),
        }

        driver = webdriver.Chrome(
            executable_path=chromedriver_versions[platform_], options=options
        )

        return driver
    except Exception as ex:
        # print(ex,traceback.format_exc())
        print(
            "Kindly replace the Chrome Web Driver with the latest one from "
            "http://chromedriver.chromium.org/downloads "
            "and also make sure you have the latest Chrome Browser version."
            "\nYour OS: {}".format(platform_)
        )
        exit(1)


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


def scrapper(tags, **kwargs):


    with open("facebook_credentials.yaml", "r") as ymlfile:
        cfg = yaml.safe_load(stream=ymlfile)

    if ("password" not in cfg) or ("email" not in cfg):
        print("Your email or password is missing. Kindly write them in credentials.txt")
        exit(1)

    

    if tags:

        print("\nStarting Scraping...")

        with get_driver() as driver: 
            print(driver)

            login(cfg["email"], cfg["password"], driver)
            print('\nLogin Successfull\n')

            time.sleep(np.random.randint(3, 6))

            for key, values in tags.items():
                try:
                    os.mkdir("data/"+key)
                except Exception as ex:
                    print(ex)
                for tag in values:

                    if search_tag(tag, driver):
                        pass
                    else:                
                        search_tag(tag, driver)

                    print('\nSearched Successfull\n')

                    time.sleep(np.random.randint(2, 4))

                    scroll(driver)

                    time.sleep(np.random.randint(2, 4))

                    print('\nScrolled Successfull\n')

                    scrap_posts(tag, driver)

                    print('\nPosts Scraped Successfull\n')

                    print(len(data),data)

                    df = pd.DataFrame(data)
                    df.to_csv('data/'+key+'/'+tag+'.csv')

                    time.sleep(np.random.randint(1, 2))

                    driver.get(facebook_path)

            driver.close()
            driver.quit()
    else:
        print("No tag given")


# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------

