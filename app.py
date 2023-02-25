import os
import time
import re

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import By
import selenium.webdriver.support.expected_conditions as EC  # noqa
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

import undetected_chromedriver as uc


## TEMP VARIABLES
EMAIL= os.getenv("EMAIL")
PASSWORD= os.getenv("PASSWORD")

def check_for_wait_time_page(driver):
    try:
        print("Looking for waiting time!")
        waitTime = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#waitTime")))
        
        if waitTime:

            regx = r"wait time is (\d+) min"
            matches = re.search(regx, waitTime.text)
            
            if matches:
                found = matches.group(1)
                print(f"Waiting for {str(found)} min due to high volume of traffic...")
                time.sleep(float(found)*60)
            else:
                print(f"Couldn't Detect Exact Waiting Time")
                print(f"Waiting for 10 min due to high volume of traffic Just in case...")
                time.sleep(10*60)
    except:
        print("No Waiting Time Found!")
    finally:
        print("Waiting For Extra 5 sec...")
        time.sleep(5)


def main():
    try:
        # instance of Options class allows
        # us to configure Headless Chrome
        options = Options()

        # this parameter tells Chrome that
        # it should be run without UI (Headless)
        # options.add_argument('--headless')  # Uncomment this line If you want to run headless driver

        # initializing webdriver for Chrome with our options
        driver = uc.Chrome(options=options)
        
        print("Opening Browser!")
        driver.get('https://algeria.blsspainvisa.com')


        print("Waiting for 20 sec to pass security checks...")
        time.sleep(20)

        check_for_wait_time_page(driver)

        try:
            print("Searching for Login Link...")
            login_anchor = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='login.php']")))
            if login_anchor:

                print("Login Link Found!")

                driver.execute_script('''document.querySelector("a[href='login.php']").click()''')
                print("Login Link Clicked!")

        except:        
            print("Login Link not Found!")
            print("Try again tomorrow :-(")
            quit()

        check_for_wait_time_page(driver)

        try:
            print("Searching for Enter Email Form...")
            form_01 = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#al_login")))
            if form_01:

                print("Enter Email Form Found :-)")
                f1_user_email_input = driver.find_element(By.CSS_SELECTOR, "#al_login input[name='user_email']")
                f1_submit_input = driver.find_element(By.CSS_SELECTOR, "#al_login input[type='submit']")

                print("Waiting for 2 sec...")
                time.sleep(2)

                # Inputs Values
                f1_user_email_value = EMAIL

                # Filling Inputs with Values
                f1_user_email_input.send_keys(f1_user_email_value)
                print(f'Entered Email "{f1_user_email_value}"')
                
                print("Waiting for 5 sec...")
                time.sleep(5)

                f1_submit_input.click()
                print("Pressed Continue Button")

                print("Waiting for 20 sec...")
                time.sleep(20)
        except:
            print("Enter Email Form not Found!")
            print("Try again tomorrow :-(")

        print("Saving Last_View.png Screenshot Image...")
        driver.save_screenshot("Last_View.png")

        print("Waiting for 2 sec...")
        time.sleep(2)
  
    except Exception as err:
        print("Something went Wrong!")
        print(err)
    finally:
        print("Closing Browser!")
        driver.quit()  

if __name__ == "__main__":
    main()