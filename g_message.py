import os
from pathlib import Path

# import nltk
# punkt_path = 'nltk_data/tokenizers/punkt' if os.name == 'posix' else 'AppData/Roaming/nltk_data/tokenizers/punkt'
# stopwords_path = 'nltk_data/corpora/stopwords' if os.name == 'posix' else 'AppData/Roaming/nltk_data/corpora/stopwords'
# if not os.path.exists(Path.home() / punkt_path):
#     nltk.download('punkt')
# if not os.path.exists(Path.home() / stopwords_path):
#     nltk.download('stopwords')
# from nltk.tokenize import word_tokenize, sent_tokenize
# from nltk.corpus import stopwords
# import pyderman
# import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# import undetected_chromedriver as uc

# from cpotp._version import __version__


GOOGLE_MESSAGES_URL = "https://messages.google.com/web"
if not ('CHROME_USER_DATA_DIR' in os.environ and os.path.exists(Path(os.environ['CHROME_USER_DATA_DIR']))):
    print('''
        Please set CHROME_USER_DATA_DIR environment variable.
        Run chrome://version in Chrome/Edge/Chromium browser new tab
        and set this environment variable to path given in "Profile Path"
        except the "/Default" part.
        Example: export CHROME_USER_DATA_DIR=/home/riteshp/.config/google-chrome
    ''')


class CpOTP:
    def __init__(self):
        # self._driver_path = pyderman.install(browser=pyderman.chrome, verbose=False)
        self._driver_path = ""

    def _init_driver(self, headless=True):
        options = Options()
        if headless:
            options.add_argument("--headless=new")
            if os.name == 'nt':
                options.add_argument("--disable-gpu")
        options.add_argument("--enable-javascript")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        clean_user_data_dir = os.environ['CHROME_USER_DATA_DIR'].replace('/Default', '').strip().rstrip('/')
        options.add_argument(
            f"--user-data-dir={str(Path(clean_user_data_dir) / 'cpotp')}"
        )
        driver = webdriver.Chrome(options=options)
        return driver

    def _login(self):
        driver = self._init_driver(headless=False)
        try:
            driver.get(GOOGLE_MESSAGES_URL)
            toggle = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox']")))
            driver.execute_script("arguments[0].click();", toggle)
            WebDriverWait(driver, 300).until(EC.url_contains('conversations'))
        except (TimeoutException, Exception) as e:
            print(str(e))
            print('It seems you are already logged in. Run cpotp instead.')
        finally:
            driver.quit()

    def _grab_last_sms(self):
        last_sms = ''
        print('Opening the browser')
        driver = self._init_driver()
        wait = WebDriverWait(driver, 10)
        try:
            print(f'Opening {GOOGLE_MESSAGES_URL}')
            driver.get(GOOGLE_MESSAGES_URL)

            print('Waiting for the conversations to load')
            elems = wait.until(
                EC.visibility_of_all_elements_located(
                    (By.XPATH, "//div[contains(@class,'conv-container')]/mws-conversation-list-item"))
            )
            if elems:
                msg_elem = elems[0].find_element(By.TAG_NAME, 'a')
                driver.execute_script("arguments[0].click();", msg_elem)
                print('Waiting for the messages to load in the latest conversation')
                txt_elems = wait.until(
                    EC.visibility_of_all_elements_located(
                        (By.XPATH, "//div[contains(@class,'text-msg')]"))
                )
                if txt_elems:
                    last_sms = txt_elems[-1].text
        except (TimeoutException, Exception) as e:
            print(str(e))
            print('It seems you are not already logged in. Run cpotp-setup instead.')
        finally:
            driver.quit()
        return last_sms

    # def _extract_otp(self, sms):
    #     stop = set(stopwords.words('english'))
    #     window_size = 3
    #     tokens = []
    #     for sent in sent_tokenize(sms):
    #         for word in word_tokenize(sent):
    #             word = word.lower().strip()
    #             if word not in stop:
    #                 tokens.append(word)
    #     for idx, word in enumerate(tokens):
    #         if word == 'otp' or word == 'code':
    #             context_tokens = tokens[idx+1:idx+window_size+1] + tokens[idx-window_size:idx]
    #             for context_token in context_tokens:
    #                 if context_token.isdigit() and len(context_token) >= 4 and len(context_token) <= 6:
    #                     return context_token
    #     return ''

    def get_otp(self):
        sms = self._grab_last_sms()
        if sms == '':
            return
        otp = self._extract_otp(sms)
        if otp == '':
            print('OTP not found in the last received sms.')
        else:
            # pyperclip.copy(otp)
            print(f'OTP has been copied to the clipboard: {otp}')
            return otp
