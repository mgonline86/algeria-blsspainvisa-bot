import os
import time
from datetime import datetime
import re
import logging

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

from helpers import find_new_message, extract_otp, extract_confirm_link, extract_otp_from_html, DatePicker
from h2captcha import solve_hcaptcha

# Logging Configurations
logging.basicConfig(
    filename='logs.log', 
    encoding='utf-8', 
    level=logging.INFO,
    format='[%(asctime)s](%(levelname)s): %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
)

# Prevent undetected_chromedriver from auto-close browser
class MyUDC(uc.Chrome):
    def __del__(self):
        pass



## TEMP VARIABLES
EMAIL= os.getenv("EMAIL")
PASSWORD= os.getenv("PASSWORD")

def check_for_wait_time_page(driver):
    try:
        logging.info("Looking for waiting time...")
        waitTime = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#waitTime")))
        
        regx = r"wait time is (\d+) min"
        matches = re.search(regx, waitTime.text)
        
        if matches:
            found = matches.group(1)
            logging.info(f"Waiting for {str(found)} min due to high volume of traffic...")
            time.sleep(float(found)*60)
        else:
            logging.info(f"Couldn't Detect Exact Waiting Time")
            logging.warning(f"Waiting for 10 min due to high volume of traffic Just in case...")
            time.sleep(10*60)
    except:
        logging.log("Couldn't find any waiting time!")


def main():
    # instance of Options class allows
    # us to configure Headless Chrome
    options = Options()

    # this parameter tells Chrome that
    # it should be run without UI (Headless)
    # options.add_argument('--headless')  # Uncomment this line If you want to run headless driver
    options.add_argument('--window-size=1366,768')

    # initializing webdriver for Chrome with our options
    driver = MyUDC(service=Service(ChromeDriverManager().install()), options=options)
    
    logging.info("Opening Browser!")
    driver.get('https://algeria.blsspainvisa.com')

    logging.info("Waiting for 20 sec to pass security checks...")
    time.sleep(20)
    try:

        check_for_wait_time_page(driver)

        try:
            logging.info("Searching for Login Link...")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='login.php']")))
            logging.info("Login Link Found!")
        except:        
            raise ValueError("Couldn't Find Login Link!")
        
        try:
            driver.execute_script('''document.querySelector("a[href='login.php']").click()''')
            logging.info("Login Link Clicked!")
        except:        
            raise ValueError("Couldn't Click Login Link!")

        check_for_wait_time_page(driver)

        f1_submit_time = None

        try:
            logging.info("Searching for Enter Email Form...")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#al_login")))
            logging.info("Enter Email Form Found!")
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
            logging.info(f'Entering Email "{f1_user_email_value}"...')
            f1_user_email_input.send_keys(f1_user_email_value)
            logging.info(f'Entered Email "{f1_user_email_value}"')
        except:
            raise ValueError("Couldn't Enter Email!")
            
        try:
            f1_submit_time = datetime.now()
            logging.info("Pressing Continue Button...")
            f1_submit_input.click()
            logging.info("Pressed Continue Button!")
        except:
            raise ValueError("Couldn't Press Continue Button!")

        check_for_wait_time_page(driver)

        try:
            print("Checking if we need to switch account...")
            otp_was_sent = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div > div > div > div > div > p")))

            if otp_was_sent:
                logging.info("We need to switch account!")
                #   ::TODO::  Handle Switch Account
                raise ValueError("Current Account Expired, Try after 30 min!")
        except:
            logging.info("No need to switch account.")

        try:
            logging.info("Waiting for OTP Email...")
            otp_email = find_new_message(f1_submit_time)
            logging.info("Retriving OTP Code from Email...")
            otp_code = extract_otp(otp_email)
            logging.info(f"OTP Code is {otp_code}")
        except:
            raise ValueError("Couldn't Retrive OTP Code from Email!")
        
        try:            
            logging.info("Searching for Enter OTP & Password Form...")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#al_login")))
            logging.info("Enter OTP & Password Form Found!")
        except:
            raise ValueError("Couldn't Find OTP & Password Form!")

        try:
            # Filling Inputs with Values
            f2_otp_input = driver.find_element(By.CSS_SELECTOR, "#al_login input[name='otp']")
            logging.info(f'Entering OTP "{otp_code}"...')
            f2_otp_input.send_keys(otp_code)
            logging.info(f'Entered OTP "{otp_code}"!')
        except:
            raise ValueError("Couldn't Enter OTP Code!")            
            
        try:
            f2_password_input = driver.find_element(By.CSS_SELECTOR, "#al_login input[name='user_password']")
            f2_password_value = PASSWORD
            logging.info(f'Entering Password "{"*" * len(f2_password_value)}"...')
            f2_password_input.send_keys(f2_password_value)
            logging.info(f'Entered Password "{"*" * len(f2_password_value)}"!')
        except:
            raise ValueError("Couldn't Enter Password!")            
            
        try:
            f2_submit_input = driver.find_element(By.CSS_SELECTOR, "#al_login input[type='submit']")
            logging.info("Pressing Login Button...")
            f2_submit_input.click()
            logging.info("Pressed Login Button!")
        except:
            raise ValueError("Couldn't Press Login Button!")

        check_for_wait_time_page(driver)

        try:
            f3_submit_time = None
            print("Searching for Appointment Booking Form...")
            form_03 = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#alg_app_first")))
            if form_03:
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


                print("Appointment Booking Form Found :-)")
                
                # Form Inputs
                f3_app_type1_radio = driver.find_element(By.CSS_SELECTOR, "#app_type1")
                f3_app_type2_radio = driver.find_element(By.CSS_SELECTOR, "#app_type2")
                f3_visa_question_input = driver.find_element(By.CSS_SELECTOR, "#visa_question")
                f3_visa_no_input = driver.find_element(By.CSS_SELECTOR, "#visa_no")
                f3_visa_valid_from_input = driver.find_element(By.CSS_SELECTOR, "#visa_valid_from")
                f3_visa_valid_to_input = driver.find_element(By.CSS_SELECTOR, "#visa_valid_to")
                f3_rejected2_input = driver.find_element(By.CSS_SELECTOR, "#rejected2")
                f3_rejected_input = driver.find_element(By.CSS_SELECTOR, "#rejected")
                f3_refusal_date_input = driver.find_element(By.CSS_SELECTOR, "#refusal_date")
                f3_phone_code_input = driver.find_element(By.CSS_SELECTOR, "#phone_code")
                f3_phone_input = driver.find_element(By.CSS_SELECTOR, "#phone")
                f3_email_input = driver.find_element(By.CSS_SELECTOR, "#email")
                f3_csrftokenvalue_input = driver.find_element(By.CSS_SELECTOR, "#csrftokenvalue")
                
                f3_member_select = Select(driver.find_element(By.CSS_SELECTOR, "#member"))
                f3_juridiction_select = Select(driver.find_element(By.CSS_SELECTOR, "#juridiction"))
                

                # if application type is family
                if app_type_u_input == "Family":
                    app_type = "Family"
                    members_count = members_count_u_input
                    f3_app_type2_radio.click()
                    print("Family Appliction Type is Selected!")
                
                    print("Waiting for 1 sec...")
                    time.sleep(1)
                    f3_member_select.select_by_value(members_count)
                else:
                    print("Individual Appliction Type is Selected!")


                print("Waiting for 1 sec...")
                time.sleep(1)

                print("Closing Popup")
                # close_popup = driver.find_element(By.CSS_SELECTOR, ".popup-appCloseIcon")
                # if close_popup:
                #     close_popup.click()
                driver.execute_script('''document.querySelector(".popup-appCloseIcon").click()''')
                print("Waiting for 1 sec...")
                time.sleep(1)

                # Filling Inputs with Values
                print(f'Selecting Juridiction...')
                f3_juridiction_select.select_by_visible_text(juridiction_u_input)
                print(f'Selected Juridiction is "{juridiction_u_input}"')

                print("Waiting for 5 sec...")
                time.sleep(5)

                print(f'Selecting Appointment Category...')
                f3_category_select = Select(driver.find_element(By.CSS_SELECTOR, "#category"))
                f3_category_select.select_by_visible_text(app_cat_u_input)
                print(f'Selected Appointment Category is "{app_cat_u_input}"')
                
                print("Waiting for 3 sec...")
                time.sleep(3)

                # f3_email_input.send_keys(f3_email_input)
                # print(f'Entered Email is "{f3_email_input}"')
                
                # print("Waiting for 1 sec...")
                # time.sleep(1)

                f3_submit_time = datetime.now()
                driver.execute_script('''document.querySelector("#verification_code").click()''')
                print(f'Requested Verification Token Button Clicked')


                print("Waiting for Verification Token Email...")
                verify_email = find_new_message(f3_submit_time)

                print("Retriving Confirm URL from Email...")
                verify_url = extract_confirm_link(verify_email)
                print(f"Verify URL is ({verify_url})")

                if not verify_url:
                    raise ValueError("Couldn't Retrive Verify URL!")
                
                print("Opening Verify URL in a New Browser")
                sub_options = Options()
                # sub_options.add_argument('--headless')  # Uncomment this line If you want to run headless driver
                sub_options.add_argument('--window-size=1366,768')
                sub_driver = MyUDC(service=Service(ChromeDriverManager().install()), options=sub_options)
                sub_driver.get(verify_url)
                
                print("Waiting for 3 sec...")
                time.sleep(3)

                check_for_wait_time_page(sub_driver)


                verify_otp = None

                try:
                    print("Searching for Email Input...")
                    sub_email_input = WebDriverWait(sub_driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[name=email]")))
                    if sub_email_input:
                        print("Email Input Found!")
                        # sub_email_input.send_keys(email_u_input)
                        sub_driver.execute_script(f'''document.querySelector("[name=email]").value = `{email_u_input}`''')
                        print(f'Entered Email is "{email_u_input}"')
        
                        print("Waiting for 1 sec...")
                        time.sleep(1)

                        print("Pressing Submit Button...")
                        # sub_submit_btn = sub_driver.find_element(By.CSS_SELECTOR, "form input[type='submit']")
                        # sub_submit_btn.click()
                        sub_driver.execute_script('''document.querySelector("[type=submit]").click()''')
                        print("Pressed Submit Button!")

                        print("Searching for OTP div...")
                        verify_otp_div = WebDriverWait(sub_driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".blurry-text")))


                        if verify_otp_div:
                            verify_otp = extract_otp_from_html(verify_otp_div.text)
                except Exception as err:        
                    print("Error at Email Input:\n")
                    print(err)
                    quit()
                finally:
                    sub_driver.quit()

                if verify_otp:
                    print("Waiting for 2 sec...")
                    time.sleep(2)
                    f3_otpvr_input = driver.find_element(By.CSS_SELECTOR, "#otpvr")
                    print("Entering Verify Token...")
                    f3_otpvr_input.send_keys(verify_otp)
                    print(f"Entered Verify Token is {verify_otp}")
                else:
                    raise ValueError("Couldn't Optain Verify Token!")

                print("Waiting for 4 sec...")
                time.sleep(4)
                print("Waiting for 1 sec...")
                time.sleep(1)

                print("Closing Popup")
                driver.execute_script('''document.querySelector(".popup-appCloseIcon").click()''')
                print("Waiting for 1 sec...")
                time.sleep(1)

                print(f'Selecting Juridiction Again...')
                f3_juridiction_select_2 = Select(driver.find_element(By.CSS_SELECTOR, "#juridiction"))
                f3_juridiction_select_2.select_by_visible_text(juridiction_u_input)
                print(f'Selected Juridiction is "{juridiction_u_input}"')

                print("Waiting for 5 sec...")
                time.sleep(5)

                print(f'Selecting Appointment Category Again...')
                f3_category_select_2 = Select(driver.find_element(By.CSS_SELECTOR, "#category"))
                f3_category_select_2.select_by_visible_text(app_cat_u_input)
                print(f'Selected Appointment Category is "{app_cat_u_input}"')

                print("Waiting for 4 sec...")
                time.sleep(4)

                challenge_div = driver.find_element(By.CSS_SELECTOR, "[data-sitekey]")
                print("Started Solver...")
                hc_sitekey = challenge_div.get_attribute('data-sitekey')
                print("sitekey:", hc_sitekey)
                hc_page_url = driver.current_url
                print("page_url:", hc_page_url)
                print("Solving hcaptcha...")
                captcha_token = solve_hcaptcha(hc_sitekey, hc_page_url)
                print("captcha_solution:", captcha_token)
                driver.execute_script(
                    """
                    document.getElementsByName('h-captcha-response')[0].innerHTML = arguments[0]
                    """,
                    captcha_token,
                )
                print("waiting 2 sec")
                time.sleep(2)
                # f3_submit_btn = driver.find_element(By.CSS_SELECTOR, "input[name='save']")
                print("Pressing Submit Button...")
                # f3_submit_btn.click()
                driver.execute_script('''document.querySelector("[name=save]").click()''')
                print("Pressed Submit Button!")
                print("waiting 2 sec")
                time.sleep(2)



                # f3_password_input.send_keys(f3_password_value)
                # print(f'Entered Password "{f3_password_value}"')
                
                # print("Waiting for 2 sec...")
                # time.sleep(2)

                # f3_submit_input.click()
                # print("Pressed Login Button")

        except Exception as err:
            print("Error:\n")
            print(err)
            print("Appointment Booking Form not Found!")
            print("Try again tomorrow :-(")

        check_for_wait_time_page(driver)
        
        # Terms Agreement Page
        try:

            print("Finding Agree Button...")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[name=agree]")))
            print("Agree Button Found!")
            
            print("Closing Popup")
            driver.execute_script('''document.querySelector(".popup-appCloseIcon").click()''')
            print("Waiting for 1 sec...")
            time.sleep(1)


            print("Pressing Agree Button...")
            driver.execute_script('''document.querySelector("[name=agree]").click()''')
            print("Pressed Agree Button!")

        except:
            print("Agree Button not Found!")
            print("Try again tomorrow :-(")

        check_for_wait_time_page(driver)

        # Date Picker Page
        try:
            print("Closing Popup")
            driver.execute_script('''document.querySelector(".popup-appCloseIcon").click()''')
            print("Waiting for 1 sec...")
            time.sleep(1)


            print("Finding Date Picker Input...")
            app_data = WebDriverWait(driver, 5).until(lambda x: x.find_element(By.ID, "app_date"))
            print("Date Picker Input Found!")
            # create action chain object
            action = ActionChains(driver)
            action.click(app_data).perform()
            print("Finding Date Picker Table...")
            date_picker = WebDriverWait(driver, 2).until(lambda x: x.find_element(By.CLASS_NAME, "datepicker"))
            if date_picker:
                print("Date Picker Table Found!")
                curr_month_date = driver.find_element(By.CSS_SELECTOR, '.datepicker-days th.datepicker-switch').text
                tds = driver.find_elements(By.CSS_SELECTOR, '.datepicker td[title]:not([title="Not Allowed"],[title="Off Day"])')
                datePicker = DatePicker(curr_month_date)
                for td in tds:
                    td_title = td.get_attribute("title")
                    td_date = datePicker.get_element_date(td).date()
                    td_classes = td.get_attribute("class")
                    print(f"[{td_date}]:\ttitle: '{td_title}'\tclasses: '{td_classes}'")

            
            print("Waiting for 60 min...")
            time.sleep(1*60*60)
        except:
            print("Agree Button not Found!")
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
    logging.info("=====================")
    logging.info("====== NEW RUN ======")
    logging.info("=====================")
    main()