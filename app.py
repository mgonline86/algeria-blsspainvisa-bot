import time

# from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import By
import selenium.webdriver.support.expected_conditions as EC  # noqa
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

import undetected_chromedriver as uc


def main():
    try:
        options = Options()

        # this parameter tells Chrome that
        # it should be run without UI (Headless)
        # options.add_argument('--headless')  # Uncomment this line If you want to run headless driver

        # initializing webdriver for Chrome with our options
        driver = uc.Chrome(options=options)
        
        print("Opening Browser!")
        driver.get('https://algeria.blsspainvisa.com/mobile-biometric.php')


        print("Waiting for 20 sec to pass security checks...")
        time.sleep(20)
        
        try:
            print("Searching for the Form...")
            app_form = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#form_mobile_biometric")))
            if app_form:
                print("Form Found :-)")
                firstname_input = driver.find_element(By.CSS_SELECTOR, "#firstname")
                lastname_input = driver.find_element(By.CSS_SELECTOR, "#lastname")
                useremail_input = driver.find_element(By.CSS_SELECTOR, "#useremail")
                phone_input = driver.find_element(By.CSS_SELECTOR, "#phone")
                city_input = driver.find_element(By.CSS_SELECTOR, "#city")
                terms_agree_input = driver.find_element(By.CSS_SELECTOR, "#user_consent")
                captcha_input = driver.find_element(By.CSS_SELECTOR, "#captcha")
                captcha_img = driver.find_element(By.CSS_SELECTOR, "#captcha-img")
                captcha_img_change_anchor = driver.find_element(By.CSS_SELECTOR, "#change-image")
        
                print("Waiting for 5 sec...")
                time.sleep(5)

                # Inputs Values
                firstname = "X_firstname"
                lastname = "X_lastname"
                useremail = "X_useremail"
                phone = "X_phone"
                city = "X_city"
                captcha = "X_captcha"

                # Filling Inputs with Values
                firstname_input.send_keys(firstname)
                lastname_input.send_keys(lastname)
                useremail_input.send_keys(useremail)
                phone_input.send_keys(phone)
                city_input.send_keys(city)
                captcha_input.send_keys(captcha)
                terms_agree_input.click()

                print("Waiting for 5 sec...")
                time.sleep(5)

                # app_form.submit()
        except:
            print("Form not Found!")
            print("Try again tomorrow :-(")

        print("Saving Last_View.png Screenshot Image...")
        driver.save_screenshot("Last_View.png")

        print("Waiting for 2 sec...")
        time.sleep(2)

        print("Closing Browser!")
        driver.quit()    
    except Exception as err:
        print("Something went Wrong!")
        print(err)
# instance of Options class allows
# us to configure Headless Chrome

if __name__ == "__main__":
    main()