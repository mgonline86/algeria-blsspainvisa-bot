import os
import time
from datetime import datetime
import re
from logger import logger as logging

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import By
import selenium.webdriver.support.expected_conditions as EC  # noqa
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service

import undetected_chromedriver as uc

from webdriver_manager.chrome import ChromeDriverManager

from helpers import find_new_message, extract_otp, extract_confirm_link, extract_otp_from_html, DatePicker, runner, log_to_csv
from h2captcha import solve_hcaptcha


# Prevent undetected_chromedriver from auto-close browser
class MyUDC(uc.Chrome):
    def __del__(self):
        pass


## TEMP VARIABLES
EMAIL= os.getenv("EMAIL")
PASSWORD= os.getenv("PASSWORD")

def check_for_wait_time_page(driver):
    try:
        logging.critical("Looking for waiting time...")
        waitTime = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#waitTime")))
        
        regx = r"wait time is (\d+) min"
        matches = re.search(regx, waitTime.text)
        
        if matches:
            found = matches.group(1)
            logging.critical(f"Waiting for {str(found)} min due to high volume of traffic...")
            time.sleep(float(found)*60)
        else:
            logging.critical(f"Couldn't Detect Exact Waiting Time")
            logging.warning(f"Waiting for 10 min due to high volume of traffic Just in case...")
            time.sleep(10*60)
    except:
        logging.critical("Couldn't find any waiting time!")


def main():
    # instance of Options class allows
    # us to configure Headless Chrome
    options = Options()

    # this parameter tells Chrome that
    # it should be run without UI (Headless)
    options.add_argument('--headless')  # Uncomment this line If you want to run headless driver
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1366,768')

    # initializing webdriver for Chrome with our options
    driver = MyUDC(service=Service(ChromeDriverManager().install()), options=options)
    
    logging.critical("Opening Browser!")
    driver.get('https://algeria.blsspainvisa.com')

    logging.critical("Waiting for 20 sec to pass security checks...")
    time.sleep(20)
    try:

        check_for_wait_time_page(driver)

        try:
            logging.critical("Searching for Login Link...")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='login.php']")))
            logging.critical("Login Link Found!")
        except:        
            raise ValueError("Couldn't Find Login Link!")
        
        try:
            driver.execute_script('''document.querySelector("a[href='login.php']").click()''')
            logging.critical("Login Link Clicked!")
        except:        
            raise ValueError("Couldn't Click Login Link!")

        check_for_wait_time_page(driver)

        f1_submit_time = None

        try:
            logging.critical("Searching for Enter Email Form...")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#al_login")))
            logging.critical("Enter Email Form Found!")
        except:
            raise ValueError("Enter Email Form not Found!")

        try:
            f1_user_email_input = driver.find_element(By.CSS_SELECTOR, "#al_login input[name='user_email']")
        except:
            raise ValueError("Email input not Found!")
        
        try:
            f1_submit_input = driver.find_element(By.CSS_SELECTOR, "#al_login input[type='submit']")
        except:
            raise ValueError("Submit button not Found!")

        try:
            # Inputs Values
            f1_user_email_value = EMAIL
            # Filling Inputs with Values
            logging.critical(f'Entering Email "{f1_user_email_value}"...')
            f1_user_email_input.send_keys(f1_user_email_value)
            logging.critical(f'Entered Email "{f1_user_email_value}"')
        except:
            raise ValueError("Couldn't Enter Email!")
            
        try:
            f1_submit_time = datetime.now()
            logging.critical("Pressing Continue Button...")
            f1_submit_input.click()
            logging.critical("Pressed Continue Button!")
        except:
            raise ValueError("Couldn't Press Continue Button!")

        check_for_wait_time_page(driver)

        otp_was_sent = None

        try:
            logging.critical("Checking if we need to switch account...")
            otp_was_sent = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div > div > div > div > div > p")))

            logging.critical("We need to switch account!")
            #   ::TODO::  Handle Switch Account
            logging.critical("Waiting for 30 min...")
            time.sleep(30 * 60)
        except:
            logging.critical("No need to switch account.")

        if otp_was_sent:
            raise ValueError("Restarting App after 30 min!")
        
        try:
            logging.critical("Waiting for OTP Email...")
            otp_email = find_new_message(f1_submit_time)
            logging.critical("Retriving OTP Code from Email...")
            otp_code = extract_otp(otp_email)
            logging.critical(f"OTP Code is {otp_code}")
        except:
            raise ValueError("Couldn't Retrive OTP Code from Email!")
        
        try:            
            logging.critical("Searching for Enter OTP & Password Form...")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#al_login")))
            logging.critical("Enter OTP & Password Form Found!")
        except:
            raise ValueError("Couldn't Find OTP & Password Form!")

        try:
            # Filling Inputs with Values
            f2_otp_input = driver.find_element(By.CSS_SELECTOR, "#al_login input[name='otp']")
            logging.critical(f'Entering OTP "{otp_code}"...')
            f2_otp_input.send_keys(otp_code)
            logging.critical(f'Entered OTP "{otp_code}"!')
        except:
            raise ValueError("Couldn't Enter OTP Code!")            
            
        try:
            f2_password_input = driver.find_element(By.CSS_SELECTOR, "#al_login input[name='user_password']")
            f2_password_value = PASSWORD
            logging.critical(f'Entering Password "{"*" * len(f2_password_value)}"...')
            f2_password_input.send_keys(f2_password_value)
            logging.critical(f'Entered Password "{"*" * len(f2_password_value)}"!')
        except:
            raise ValueError("Couldn't Enter Password!")            
            
        try:
            f2_submit_input = driver.find_element(By.CSS_SELECTOR, "#al_login input[type='submit']")
            logging.critical("Pressing Login Button...")
            f2_submit_input.click()
            logging.critical("Pressed Login Button!")
        except:
            raise ValueError("Couldn't Press Login Button!")

        check_for_wait_time_page(driver)

        f3_submit_time = None
        try:
            logging.critical("Searching for Appointment Booking Form...")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#alg_app_first")))
            logging.critical("Appointment Booking Form Found :-)")
        except:
            raise ValueError("Couldn't Find Appointment Booking Form!")
        
        try:
            logging.critical("Closing Popup Box...")
            driver.execute_script('''document.querySelector(".popup-appCloseIcon").click()''')
            logging.critical("Popup Box Closed!")
            logging.critical("Waiting for 1 sec...")
            time.sleep(1)
        except:
            raise ValueError("Couldn't Close Popup Box!")

        # Default Values
        app_type = "Individual"
        members_count = None
        f3_juridiction_select_opts = {
            "Select Juridiction": "",
            "Adrar": "14#Adrar#9",
            "Aïn Temouchent Y Relizane": "14#A�n Temouchent Y Relizane#9",
            "Ain-Defla": "15#Ain-Defla#10",
            "Algiers": "15#Algiers#10",
            "Annaba": "15#Annaba#10",
            "Batna": "15#Batna#10",
            "Béchar": "14#B�char#9",
            "Béjaia": "15#B�jaia#10",
            "Biskra": "15#Biskra#10",
            "Blida": "15#Blida#10",
            "Bordj-Bou-Arréridj": "15#Bordj-Bou-Arr�ridj#10",
            "Bouira": "15#Bouira#10",
            "Boumerdés": "15#Boumerd�s#10",
            "Chlef": "14#Chlef#9",
            "Constantine": "15#Constantine#10",
            "Djelfa": "15#Djelfa#10",
            "El Bayadh": "14#El Bayadh#9",
            "El Oued, El Tarf": "15#El Oued, El Tarf#10",
            "Ghardaïa": "15#Gharda�a#10",
            "Guelma": "15#Guelma#10",
            "Illizi": "15#Illizi#10",
            "Jijel": "15#Jijel#10",
            "Khenchela": "15#Khenchela#10",
            "Laghouart": "15#Laghouart#10",
            "M'sila": "15#M'sila#10",
            "Mascara": "14#Mascara#9",
            "Médéa": "15#M�d�a#10",
            "Mila": "15#Mila#10",
            "Mostaganem": "14#Mostaganem#9",
            "Naâma": "14#Na�ma#9",
            "Oran": "14#Oran#9",
            "Ouargla": "15#Ouargla#10",
            "Oum El Bouaghi": "15#Oum El Bouaghi#10",
            "Saïda": "14#Sa�da#9",
            "Sétif": "15#S�tif#10",
            "Sidi Bel-Abbes": "14#Sidi Bel-Abbes#9",
            "Skikda": "15#Skikda#10",
            "Souk Ahras": "15#Souk Ahras#10",
            "Tamanrasset": "15#Tamanrasset#10",
            "Tebessa": "15#Tebessa#10",
            "Tiaret": "14#Tiaret#9",
            "Tindouf": "15#Tindouf#10",
            "Tipaza": "15#Tipaza#10",
            "Tissemsilt": "14#Tissemsilt#9",
            "Tizi-Ouzou": "15#Tizi-Ouzou#10",
            "Tlemcen": "14#Tlemcen#9"
        }
        f3_category_select_opts = {
            "Appointment Category" : "",
            "Normal" : "Normal",
            "Premium" : "Premium",
        }

        # User Inputs
        app_type_u_input = "Individual"
        members_count_u_input = "2"
        juridiction_u_input = "Sétif"
        app_cat_u_input = "Normal"
        email_u_input = EMAIL

        # try:
        #     logging.critical("Searching for Appointment Booking Form Input Fields...")
        #     # Form Inputs
        #     f3_app_type1_radio = driver.find_element(By.CSS_SELECTOR, "#app_type1")
        #     f3_visa_question_input = driver.find_element(By.CSS_SELECTOR, "#visa_question")
        #     f3_visa_no_input = driver.find_element(By.CSS_SELECTOR, "#visa_no")
        #     f3_visa_valid_from_input = driver.find_element(By.CSS_SELECTOR, "#visa_valid_from")
        #     f3_visa_valid_to_input = driver.find_element(By.CSS_SELECTOR, "#visa_valid_to")
        #     f3_rejected2_input = driver.find_element(By.CSS_SELECTOR, "#rejected2")
        #     f3_rejected_input = driver.find_element(By.CSS_SELECTOR, "#rejected")
        #     f3_refusal_date_input = driver.find_element(By.CSS_SELECTOR, "#refusal_date")
        #     f3_phone_code_input = driver.find_element(By.CSS_SELECTOR, "#phone_code")
        #     f3_phone_input = driver.find_element(By.CSS_SELECTOR, "#phone")
        #     f3_email_input = driver.find_element(By.CSS_SELECTOR, "#email")
        #     f3_csrftokenvalue_input = driver.find_element(By.CSS_SELECTOR, "#csrftokenvalue")
            
        #     logging.critical("Found Appointment Booking Form Input Fields!")
        # except:
        #     raise ValueError("Couldn't Find Appointment Booking Form Input Fields!!")
            
        try:
            # if application type is family
            if app_type_u_input == "Family":
                logging.critical("Selecting Family Appliction Type...")
                app_type = "Family"
                members_count = members_count_u_input
                f3_app_type2_radio = driver.find_element(By.CSS_SELECTOR, "#app_type2")
                f3_app_type2_radio.click()
                logging.critical("Family Appliction Type is Selected!")
                logging.critical("Waiting for 1 sec...")
                time.sleep(1)
                try:
                    logging.critical(f"Setting Number of Members as {members_count}...")
                    f3_member_select = Select(driver.find_element(By.CSS_SELECTOR, "#member"))
                    f3_member_select.select_by_value(members_count)
                    logging.critical(f"Number of Members is Set to {members_count}!")
                except:
                    raise ValueError("Couldn't Set Number of Members!")
            else:
                logging.critical("Individual Appliction Type is Selected by default!")

            logging.critical("Waiting for 1 sec...")
            time.sleep(1)
        except:
            raise ValueError("Couldn't Select Application Type!")
            
        try:
            # Filling Inputs with Values
            logging.critical(f'Selecting Juridiction as "{juridiction_u_input}"...')
            f3_juridiction_select = Select(driver.find_element(By.CSS_SELECTOR, "#juridiction"))
            f3_juridiction_select.select_by_visible_text(juridiction_u_input)
            logging.critical(f'Selected Juridiction as "{juridiction_u_input}"')
            logging.critical("Waiting for 5 sec...")
            time.sleep(5)
        except:
            raise ValueError("Couldn't Select Juridiction!")
            
        try:
            logging.critical(f'Selecting Appointment Category as "{app_cat_u_input}"...')
            f3_category_select = Select(driver.find_element(By.CSS_SELECTOR, "#category"))
            f3_category_select.select_by_visible_text(app_cat_u_input)
            logging.critical(f'Selected Appointment Category as "{app_cat_u_input}"')            
            logging.critical("Waiting for 3 sec...")
            time.sleep(3)
        except:
            raise ValueError("Couldn't Select Appointment Category!")
            
        f3_submit_time = datetime.now()
        
        try:
            logging.critical('Clicking Request Verification Token Button...')
            driver.execute_script('''document.querySelector("#verification_code").click()''')
            logging.critical(f'Clicked Request Verification Token Button!')
        except:
            raise ValueError("Couldn't Click Request Verification Token Button!")
            
        try:
            logging.critical("Retriving Verification Token...")
            logging.critical("Finding Last Verification Token Email...")
            verify_email = find_new_message(f3_submit_time)
            if not verify_email:
                raise ValueError("Couldn't Find Last Verification Token Email!")
            
            logging.critical("Extracting Confirm URL from Email...")
            verify_url = extract_confirm_link(verify_email)
            if not verify_url:
                raise ValueError("Couldn't Retrive Verify URL!")
            logging.critical(f"Verify URL is ({verify_url})")
            
            logging.critical("Opening Verify URL in a New Browser")
            sub_options = Options()
            sub_options.add_argument('--headless')  # Uncomment this line If you want to run headless driver
            sub_options.options.add_argument('--disable-gpu')
            sub_options.add_argument('--window-size=1366,768')
            sub_driver = MyUDC(service=Service(ChromeDriverManager().install()), options=sub_options)
            sub_driver.get(verify_url)
            logging.critical("Waiting for 3 sec...")
            time.sleep(3)

            check_for_wait_time_page(sub_driver)

            verify_otp = None
            try:
                logging.critical("Started Verifying Process...")
                try:
                    logging.critical("Searching for Email Input...")
                    WebDriverWait(sub_driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[name=email]")))
                    logging.critical("Email Input Found!")
                except:
                    raise ValueError("Couldn't Find Email Input!")
                    
                try:
                    logging.critical(f'Entering Email as "{email_u_input}"...')
                    sub_driver.execute_script(f'''document.querySelector("[name=email]").value = `{email_u_input}`''')
                    logging.critical(f'Entered Email as "{email_u_input}"!')
                    logging.critical("Waiting for 1 sec...")
                    time.sleep(1)
                except:
                    raise ValueError("Couldn't Enter Email!")
                    
                try:
                    logging.critical("Pressing Submit Button...")
                    sub_driver.execute_script('''document.querySelector("[type=submit]").click()''')
                    logging.critical("Pressed Submit Button!")
                except:
                    raise ValueError("Couldn't Press Submit Button!")
                    
                try:
                    logging.critical("Searching for OTP div...")
                    verify_otp_div = WebDriverWait(sub_driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".blurry-text")))
                    logging.critical("OTP div Found!")
                except:
                    raise ValueError("Couldn't Find OTP div!")
                    
                try:
                    logging.critical("Extracting Verify OTP...")
                    verify_otp = extract_otp_from_html(verify_otp_div.text)
                    logging.critical(f'Extracted Verify OTP is "{verify_otp}"!')
                except:
                    raise ValueError("Couldn't Extracting Verify OTP!")
            except Exception as err:        
                logging.error("Couldn't Complete Verifying Process!")
                logging.error(err)
            finally:
                sub_driver.quit()

            if verify_otp:
                try:
                    logging.critical("Waiting for 2 sec...")
                    time.sleep(2)
                    logging.critical("Entering Verify Token...")
                    f3_otpvr_input = driver.find_element(By.CSS_SELECTOR, "#otpvr")
                    f3_otpvr_input.send_keys(verify_otp)
                    logging.critical(f"Entered Verify Token is {verify_otp}")
                except:
                    raise ValueError("Couldn't Enter Verify Token!")
            else:
                raise ValueError("Couldn't Optain Verify Token!")

            logging.critical("Waiting for 2 sec...")
            time.sleep(2)

            try:    
                logging.critical(f'Selecting Juridiction Again...')
                f3_juridiction_select_2 = Select(driver.find_element(By.CSS_SELECTOR, "#juridiction"))
                f3_juridiction_select_2.select_by_visible_text(juridiction_u_input)
                logging.critical(f'Selected Juridiction is "{juridiction_u_input}"')
                logging.critical("Waiting for 5 sec...")
                time.sleep(5)
            except:
                raise ValueError("Couldn't Select Juridiction Again!")

            try:
                logging.critical(f'Selecting Appointment Category Again...')
                f3_category_select_2 = Select(driver.find_element(By.CSS_SELECTOR, "#category"))
                f3_category_select_2.select_by_visible_text(app_cat_u_input)
                logging.critical(f'Selected Appointment Category is "{app_cat_u_input}"')

                logging.critical("Waiting for 4 sec...")
                time.sleep(4)
            except:
                raise ValueError("Couldn't Select Appointment Category Again!")

            try:
                logging.critical("Started Solving hcaptcha...")
                challenge_div = driver.find_element(By.CSS_SELECTOR, "[data-sitekey]")
                logging.critical("Started Solver...")
                hc_sitekey = challenge_div.get_attribute('data-sitekey')
                logging.critical("sitekey:", hc_sitekey)
                hc_page_url = driver.current_url
                logging.critical("page_url:", hc_page_url)
                logging.critical("Solving hcaptcha...")
                captcha_token = solve_hcaptcha(hc_sitekey, hc_page_url)
                logging.critical("captcha_solution:", captcha_token)
                driver.execute_script(
                    """
                    document.getElementsByName('h-captcha-response')[0].innerHTML = arguments[0]
                    """,
                    captcha_token,
                )
                logging.critical("waiting 2 sec")
                time.sleep(2)
            except:
                raise ValueError("Couldn't Solve hcaptcha!")

            try:
                logging.critical("Pressing Submit Button...")
                driver.execute_script('''document.querySelector("[name=save]").click()''')
                logging.critical("Pressed Submit Button!")
                logging.critical("waiting 2 sec")
                time.sleep(2)
            except:
                raise ValueError("Couldn't Select Appointment Category Again!")
        except:
            raise ValueError("Couldn't Retrive Verification Token!")
            
        check_for_wait_time_page(driver)
        
        # Terms Agreement Page
        try:
            logging.critical("Finding Agree Button...")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[name=agree]")))
            logging.critical("Agree Button Found!")
        except:
            raise ValueError("Couldn't Find Agree Button!")
            
        try:
            logging.critical("Closing Popup Box...")
            driver.execute_script('''document.querySelector(".popup-appCloseIcon").click()''')
            logging.critical("Closed Popup Box!")
            logging.critical("Waiting for 1 sec...")
            time.sleep(1)
        except:
            raise ValueError("Couldn't Close Popup Box!")
            
        try:
            logging.critical("Pressing Agree Button...")
            driver.execute_script('''document.querySelector("[name=agree]").click()''')
            logging.critical("Pressed Agree Button!")
        except:
            raise ValueError("Couldn't Press Agree Button!")

        check_for_wait_time_page(driver)

        # Date Picker Page
        try:
            logging.critical("Finding Date Picker Input...")
            app_data = WebDriverWait(driver, 5).until(lambda x: x.find_element(By.ID, "app_date"))
            logging.critical("Date Picker Input Found!")
        except:
            raise ValueError("Couldn't Find Date Picker!")

        try:
            # Create action chain object
            action = ActionChains(driver)
            action.click(app_data).perform()
            logging.critical("Finding Date Picker Table...")
            WebDriverWait(driver, 2).until(lambda x: x.find_element(By.CLASS_NAME, "datepicker"))
            logging.critical("Date Picker Table Found!")
        except:
            raise ValueError("Couldn't Find Date Picker Table!")

        try:
            logging.critical("Finding Current Table Month...")
            curr_month_date = driver.find_element(By.CSS_SELECTOR, '.datepicker-days th.datepicker-switch').text
            logging.critical("Found Current Table Month!")
        except:
            raise ValueError("Couldn't Find Current Table Month!")

        try:
            logging.critical("Finding Table Data Cells Tags...")
            tds = driver.find_elements(By.CSS_SELECTOR, '.datepicker td[title]:not([title="Not Allowed"],[title="Off Day"])')
            logging.critical("Found Table Data Cells Tags!")
        except:
            raise ValueError("Couldn't Find Table Data Cells Tags!")

        try:
            logging.critical("Extracting Available Days Data...")
            datePicker = DatePicker(curr_month_date)
            csv_header = ['Cell Date', 'Cell Title Attribute', 'Cell Classes']
            csv_rows = []
            for td in tds:
                td_title = td.get_attribute("title")
                td_date = datePicker.get_element_date(td).date()
                td_classes = td.get_attribute("class")
                logging.critical(f"[{td_date}]:\ttitle: '{td_title}'\tclasses: '{td_classes}'")
                csv_rows.append([td_date, td_title, td_classes])
            logging.critical("Extracted Available Days Data!")
            log_to_csv('logs.csv', csv_rows, csv_header)
        except:
            raise ValueError("Couldn't Extract Available Days Data!")
  
    except Exception as err:
        logging.error(err)
    
    finally:
        logging.critical("Saving Last_View.png Screenshot Image...")
        driver.save_screenshot("Last_View.png")
        logging.critical("Waiting for 2 sec...")
        time.sleep(2)
        logging.critical("Closing Browser!")
        driver.quit()  

if __name__ == "__main__":
    logging.critical("=====================")
    logging.critical("====== NEW RUN ======")
    logging.critical("=====================")
    runner(main)