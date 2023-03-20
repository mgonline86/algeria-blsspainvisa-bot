import os
import time
import json
import re
import base64
from g_api import GOOGLE
from datetime import datetime

def find_new_message(submit_time):
    try:
        g = GOOGLE()
        delta_time = 0
        retries = 0
        last_message = None

        while delta_time <= 0:
            if retries >= 60:
                print("Exceeded Max Retries(5 min), Couldn't Find New OTP Message! Aborting!")
                return
            retries += 1
            print("Waiting for 5 sec...")
            time.sleep(5)
            last_message_id = g.list_messages()[0].get("id")

            last_message = g.get_message_by_id(last_message_id)

            msg_time = last_message.get("internalDate")
            msg_datetime = float(msg_time)/1000
            submit_datetime = submit_time.timestamp() - 3720  # ALG 1-hr diff & Extra 2 min
            print("submit_datetime:", submit_time)
            print("msg_time:", datetime.fromtimestamp(msg_datetime))
            delta_time = msg_datetime - submit_datetime
            print(delta_time)

        return last_message
    except Exception as err:
        print("Error at  'find_new_message()':\n")
        print(err)
        return

def decode_email_body(body_data):
    try:
        """Take encoded body data string, return decoded string."""
        # The Body of the message is in Encrypted format. So, we have to decode it.
        # Get the data and decode it with base 64 decoder.
        data = body_data.replace("-","+").replace("_","/")
        decoded_data = base64.b64decode(data)
        return decoded_data
    except Exception as err:
        print("Error in decode_email_body():\n")
        print(err)
        return

def extract_otp(message):
    try:
        # Get value of 'payload' from dictionary 'message'
        payload = message['payload']
        headers = payload['headers']

        # Look for Subject and Sender Email in the headers
        for d in headers:
            if d['name'] == 'Subject':
                subject = d['value']
            if d['name'] == 'From':
                sender = d['value']

        # Printing the subject, sender's email and message
        print("Subject: ", subject)
        print("From: ", sender)

        if not ("info@blshelpline.com" in sender):
            return None

        # The Body of the message is in Encrypted format. So, we have to decode it.
        # Get the data and decode it with base 64 decoder.
        data = payload['body']['data']
        decoded_data = decode_email_body(data)
        
        OTP_regx = r">OTP - (\d+)"
        OTP_matches = re.search(OTP_regx, str(decoded_data))

        if OTP_matches:
            OTP = OTP_matches.group(1)
            return OTP.strip()
        else:
            return

    except Exception as err:
        print("Error in extract_otp():\n")
        print(err)
        return
    
def runner(func):
    """Take a Function and Run it to Infinity with restarting it on error."""
    while True:
        try:
            func()
        except Exception as err:
            print("[!] An Error Occured:")
            print(err)
            print(f"[!] Restarting '{func.__name__}() Function' ...")
            continue

def run_func_on_interval(func, interval_time):
    """Take a Function & Interval Time in seconds.

    It runs the passed Function only on two conditions:
     1- No updated_at timestamp is saved.
     2- Interval Time has exceeded when comparing the saved
        updated_at timestamp.
    """
    notify_file_exist = False
    now_timestamp = datetime.now().timestamp()
    do_update = True

    if os.path.isfile("notified.json") and os.access("notified.json", os.R_OK):
        # checks if notified.json exists
        notify_file_exist = True

    if notify_file_exist:
        with open("notified.json", "r") as jsonFile:
            old_data = json.load(jsonFile)
            last_timestamp = old_data.get("updated_at")
            time_diff = now_timestamp - last_timestamp
            if time_diff < interval_time:
                do_update = False
    if do_update:
        # Run the function
        func()
        # Save update time
        with open("notified.json", "w") as jsonFile:
            data = { "updated_at" : now_timestamp}
            json.dump(data, jsonFile)

def extract_confirm_link(message):
    try:
        # Get value of 'payload' from dictionary 'message'
        payload = message['payload']
        headers = payload['headers']

        # Look for Subject and Sender Email in the headers
        for d in headers:
            if d['name'] == 'Subject':
                subject = d['value']
            if d['name'] == 'From':
                sender = d['value']

        # Printing the subject, sender's email and message
        print("Subject: ", subject)
        print("From: ", sender)

        if not ("info.spain@blshelpline.com" in sender):
            return None

        # The Body of the message is in Encrypted format. So, we have to decode it.
        # Get the data and decode it with base 64 decoder.
        data = payload['body']['data']
        decoded_str = decode_email_body(data)
        
        url_regx = r'<a href="(.+?)">Click here.+?<\/a>'
        url_matches = re.search(url_regx, str(decoded_str))
        if url_matches:
            url = url_matches.group(1)
            return str(url.strip())
        else:
            return

    except Exception as err:
        print("Error in extract_confirm_link():\n")
        print(err)
        return

def extract_otp_from_html(html_str:str) -> str:
    try:
        OTP_regx = r"Your OTP is (\d+)"
        OTP_matches = re.search(OTP_regx, str(html_str))

        if OTP_matches:
            OTP = OTP_matches.group(1)
            return OTP.strip()
        else:
            return

    except Exception as err:
        print("Error in extract_otp():\n")
        print(err)
        return

class DatePicker:
    def __init__(self, month_year_str) -> None:
        self.month_str, self.year_str = month_year_str.split(" ")
        self.year_int = int(self.year_str)
        self.monthes = {
            "January" : 1,
            "February" : 2,
            "March" : 3,
            "April" : 4,
            "May" : 5,
            "June" : 6,
            "July" : 7,
            "August" : 8,
            "September" : 9,
            "October" : 10,
            "November" : 11,
            "December" : 12,
        }

    def get_element_date(self,ele):
        ele_classes = ele.get_attribute("class").split(' ')
        day = int(ele.text)
        month = self.monthes[self.month_str]
        year = self.year_int
        if "old" in ele_classes:
            if month == 1:
                month = 12
                year -= 1
            else:
                month -= 1
                
        if "new" in ele_classes:
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1

        return datetime(year, month, day)