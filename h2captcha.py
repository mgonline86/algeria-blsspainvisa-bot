"""Solve hcaptcha by 2captcha."""

import os
import time

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

from selenium.webdriver.remote.webdriver import By
import selenium.webdriver.support.expected_conditions as EC  # noqa
from selenium.webdriver.support.wait import WebDriverWait

API_KEY = os.getenv("CAPTCHA_KEY")

def solve_hcaptcha(sitekey:str, url:str) -> str:
    """Send sitekey and pageurl to 2Captcha API.
    
    Return solver code (str) that you could use by 
    finding textarea with name='h-captcha-response',
    and put there received code. Then, click the Check button.
    """
    from twocaptcha import TwoCaptcha

    solver = TwoCaptcha(API_KEY)
    result = None
    
    try:
        result = solver.hcaptcha(sitekey, url)

    except Exception as e:
        print("Error at solve_hcaptcha():\n")
        print(e)

    print("result:\n", result)    
    return result.get("code")

def pass_form_captcha(driver, submit_btn):
    challenge_div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-sitekey]")))
    print("Started Solver...")
    hc_sitekey = challenge_div.get_attribute('data-sitekey')
    print("sitekey:", hc_sitekey)
    hc_page_url = driver.current_url
    print("page_url:", hc_page_url)
    captcha_token = solve_hcaptcha(hc_sitekey, hc_page_url)
    print("captcha_token:", captcha_token)
    driver.execute_script(
        """
        document.getElementsByName('h-captcha-response')[0].innerHTML = arguments[0]
        """,
        captcha_token,
    )
    print("waiting 2 sec")
    time.sleep(2)
    submit_btn.click()
    print("waiting 2 sec")
    time.sleep(2)