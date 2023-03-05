import os
import time
from datetime import datetime
import re

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import By
import selenium.webdriver.support.expected_conditions as EC  # noqa
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

from helpers import find_new_message, extract_otp, extract_confirm_link, extract_otp_from_html

import undetected_chromedriver as uc

# Prevent undetected_chromedriver from auto-close browser
class MyUDC(uc.Chrome):
    def __del__(self):
        try:
            self.service.process.kill()
        except:  # noqa
            pass
        # self.quit()



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
        driver = MyUDC(options=options)
        
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

        f1_submit_time = None

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

                f1_submit_time = datetime.now()
                f1_submit_input.click()
                print("Pressed Continue Button")

        except:
            print("Enter Email Form not Found!")
            print("Try again tomorrow :-(")

        check_for_wait_time_page(driver)

        try:
            try:
                print("Checking if we need to switch account...")
                otp_was_sent = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div > div > div > div > div > p")))

                if otp_was_sent:
                    print("We need to switch account!")
                    quit()
            except:
                print("No need to switch account.")
                pass

            print("Waiting for OTP Email...")
            otp_email = find_new_message(f1_submit_time)
            print("Retriving OTP Code from Email...")
            otp_code = extract_otp(otp_email)

            print(f"OTP Code is {otp_code}")
            print("Searching for Enter OTP & Password Form...")
            form_02 = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#al_login")))
            if form_02:

                print("Enter OTP & Password Form Found :-)")
                f2_otp_input = driver.find_element(By.CSS_SELECTOR, "#al_login input[name='otp']")
                f2_password_input = driver.find_element(By.CSS_SELECTOR, "#al_login input[name='user_password']")
                f2_submit_input = driver.find_element(By.CSS_SELECTOR, "#al_login input[type='submit']")

                print("Waiting for 2 sec...")
                time.sleep(2)

                # Inputs Values
                f2_password_value = PASSWORD

                # Filling Inputs with Values
                f2_otp_input.send_keys(otp_code)
                print(f'Entered OTP "{otp_code}"')
                
                print("Waiting for 2 sec...")
                time.sleep(2)

                f2_password_input.send_keys(f2_password_value)
                print(f'Entered Password "{f2_password_value}"')
                
                print("Waiting for 2 sec...")
                time.sleep(2)

                f2_submit_input.click()
                print("Pressed Login Button")

        except:
            print("Enter OTP & Password Form not Found!")
            print("Try again tomorrow :-(")

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
                f3_otpvr_input = driver.find_element(By.CSS_SELECTOR, "#otpvr")
                f3_csrftokenvalue_input = driver.find_element(By.CSS_SELECTOR, "#csrftokenvalue")
                
                f3_member_select = Select(driver.find_element(By.CSS_SELECTOR, "#member"))
                f3_juridiction_select = Select(driver.find_element(By.CSS_SELECTOR, "#juridiction"))
                

                f3_submit_btn = driver.find_element(By.CSS_SELECTOR, "input[name='save']")

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

                # # Filling Inputs with Values
                print(f'Selecting Juridiction...')
                f3_juridiction_select.select_by_visible_text(juridiction_u_input)
                print(f'Selected Juridiction is "{juridiction_u_input}"')

                print("Waiting for 3 sec...")
                time.sleep(3)

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
                sub_driver = MyUDC(options=sub_options)
                sub_driver.get(verify_email)

                check_for_wait_time_page(sub_driver)

                verify_otp = None

                try:
                    print("Searching for Email Input...")
                    sub_email_input = WebDriverWait(sub_driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "form input[name='email']")))
                    if sub_email_input:
                        print("Email Input Found!")

                        sub_submit_btn = sub_driver.find_element(By.CSS_SELECTOR, "form input[type='submit']")

                        sub_email_input.send_keys(f3_email_input)
                        print(f'Entered Email is "{f3_email_input}"')
        
                        print("Waiting for 1 sec...")
                        time.sleep(1)

                        sub_submit_btn.click()
                        print("Pressed Submit Button!")

                        print("Searching for OTP div...")
                        verify_otp_div = WebDriverWait(sub_driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".blurry-text")))


                        if verify_otp_div:
                            verify_otp = extract_otp_from_html(verify_otp_div.text)
                except:        
                    print("Email Input not Found!")
                    print("Try again tomorrow :-(")
                    quit()
                finally:
                    sub_driver.close()

                if verify_otp:
                    f3_otpvr_input.send_keys(verify_otp)
                else:
                    raise ValueError("Couldn't Optain Verify Token!")
                
                    

                # f3_password_input.send_keys(f3_password_value)
                # print(f'Entered Password "{f3_password_value}"')
                
                # print("Waiting for 2 sec...")
                # time.sleep(2)

                # f3_submit_input.click()
                # print("Pressed Login Button")

            print("Waiting for 60 min...")
            time.sleep(1*60*60)
        except Exception as err:
            print("Error:\n")
            print(err)
            print("Appointment Booking Form not Found!")
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