from bs4 import BeautifulSoup
import requests
import time
import re
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait  # Import this
from selenium.webdriver.support import expected_conditions as EC  # Import this
from selenium.webdriver.chrome.options import Options
import json
from datetime import datetime, timedelta
from datetime import datetime
import Booker
username = None
password = None

First_name = None
Last_name = None

days_in_week = {
    1: False,
    2: True,
    3: False,
    4: False,
    5: True

}
def get_day_of_week(date_string):
    original_datetime = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    adjusted_datetime = original_datetime + timedelta(hours=15)

    date = datetime.strptime(str(adjusted_datetime), '%Y-%m-%d %H:%M:%S')
    return date.strftime('%A')
   
def extract_day(datetime_str):
    return int(datetime_str.split(" ")[0].split("-")[2])
#input credentials
def extract_nums(String):
    pattern = r"\d+"   # \d+ matches one or more digits

    matches = re.findall(pattern, String)
    return matches[0]

def increment_date_in_url(url):

    days_in_months = {
    1: 31,  
    2: 28,  
    3: 31,  
    4: 30,  
    5: 31,  
    6: 30,
    7: 31, 
    8: 31, 
    9: 30, 
    10: 31,  
    11: 30,  
    12: 31   
    }
    base_url, date_part = url.rsplit("targetDate=", 1)

    current_date = datetime.strptime(date_part.strip(), "%Y%m%d")

    new_date = current_date + timedelta(days=1)

    new_month = new_date.month
    new_year = new_date.year


    if new_date.day > days_in_months[new_month]:

        if new_month == 12:
            new_month = 1
            new_year += 1
        else:
            new_month += 1
        new_date = datetime(new_year, new_month, 1)  
    new_date_str = new_date.strftime("%Y%m%d")

    new_url = base_url + "targetDate=" + new_date_str

    return new_url


class block_attributes():
    def __init__(self):
        self.sTime = None
        self.eTime = None
        self.day = None
        self.blocks = None
        self.month = None

class communityTimes():
    def __init__(self):
        self.sTime = None
        self.eTime = None
    # def periods(self,marker):
    #     if marker:
    #         self.blocks = []
    #         for x in range(4):
    #             self.blocks.append(block_attributes(False))

def hoursconversionrate(sdate):
    if " " in sdate:
        start_datetime_str = sdate.split(" ")[1]
        # Proceed with further logic
        start_datetime = datetime.strptime(start_datetime_str, "%H:%M:%S")
        adjusted_datetime = start_datetime + timedelta(hours=9)
        return adjusted_datetime.strftime("%H:%M:%S")
    else:
        print(f"Error: Invalid input string '{sdate}', missing space.")
        return None  # Or handle as appropriate
def add_hours_to_datetime(date_str, hours_to_add):
    # Convert the input string into a datetime object
    current_datetime = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    
    # Add the specified hours using timedelta
    new_datetime = current_datetime + timedelta(hours=hours_to_add)
    
    # Format the new datetime back into the desired string format
    new_date_str = new_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    return new_date_str
    
def timeDifference(stime, etime):
    etime_obj = datetime.strptime(etime, "%H:%M:%S")
    stime_obj = datetime.strptime(stime, "%H:%M:%S")
    
    # Calculate time difference in minutes
    time_difference = (stime_obj - etime_obj).total_seconds() / 60
    if time_difference > 70:
        return True
    return False
def get_month(date_string):
    # Parse the string into a datetime object
    dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    
    # Return the month name
    return dt.strftime("%B")



def print_schedule(json_file,commtime,instance,day):
    if commtime:
        print(f"Start of community time for day {day+1} is: {commtime.sTime}")
        print(f"End of community time for day {day+1} is: {commtime.eTime}")
        
    if instance.sTime is None and instance.eTime is None:
        print(f"\nNo avaiblable frees for day {day+1}.\n")
    else:
        print(f"\nThe start of free time for day {day+1} is: {instance.sTime}\n")
        print(f"\nThe end of free time for day {day+1} is: {instance.eTime}\n")
    if commtime.sTime is None and commtime.eTime is None:
        print(f"\nNo avaiblable community times  for day {day+1}.\n")

def scraper(json_file,session_ID,url):
    #iterate 7 times, look for free block and community time and log it under the DAYS class
    #everything within the json file is 3 hours ahead of time
    #if time between class is more than 45 mins, there is a free block from->
    #the end of the last class to the start of next class
    #inside slices->itemdata->r1
    cookies = {
        'session_id_edsby': session_ID  # Use the session_id you retrieved
    }
    class_array, comm_array = [], []
    for day in range(14):
        count = 1
        instance, commtime = block_attributes(), communityTimes()
        class_array.append(instance)
        comm_array.append(commtime)
        while "itemdata" not in json_file["slices"][0]["data"]:
            response = requests.get(url, cookies=cookies)
            if response.status_code == 200:
                json_file = response.json()
                if "itemdata" in json_file["slices"][0]["data"]:
                    break
                else:
                    print("succesful retrival of json page")
                    url = increment_date_in_url(url)
                    print(url)
            else:
                print("failed to fetch page")
        #json file as it is, dissect url
        #make basic conditions, so first class has to equal 8:00, last class has to start at 13:45
        Day_of_week_str  = json_file["slices"][0]["data"]["itemdata"]["r-1"]["sdate"]
        Day_of_week_str = add_hours_to_datetime(Day_of_week_str,9)
        instance.day = extract_day(Day_of_week_str)
        Day_of_week = get_day_of_week(Day_of_week_str)
        if Day_of_week != "Tuesday" and Day_of_week != "Thursday":
            commtime.sTime = "11:00:00"
            commtime.eTime = "11:40:00"
        if  "r-4" in json_file["slices"][0]["data"]["itemdata"]:
            instance.sTime = None
            instance.eTime = None
            st_time = json_file["slices"][0]["data"]["itemdata"]["r-1"]["sdate"]
            instance.month = get_month(st_time)
            
        else:
            #if r1 sdate does not start at 8:00, MARK THE FREE BLOCKS START TIME FROM 8:00 to 9:25
            start_time_str = json_file["slices"][0]["data"]["itemdata"]["r-1"]["sdate"]

            if start_time_str:
                # Split the datetime string by space, then take the time part
                start_time = hoursconversionrate(start_time_str)
                instance.month = get_month(start_time_str)
                if start_time != "08:00:00" and start_time != "08:10:00":
                    instance.sTime = "8:00:00"
                    instance.eTime = "9:40:00"
                    
                else:
                    # ALL COMPILING PROBLEMS START FROM HERE
                    end_time_str = json_file["slices"][0]["data"]["itemdata"]["r-1"]["edate"]
                    end_time = hoursconversionrate(end_time_str)
                    break_reason = "None"
                    while True:
                        count+=1
                        key = f"r-{count}"
                        if key not in json_file["slices"][0]["data"]["itemdata"]:
                            break 
                        start_time_str = json_file["slices"][0]["data"]["itemdata"][key]["sdate"]
                        if start_time_str:
                            start_time = hoursconversionrate(start_time_str)
                        #add conditional here
                        if timeDifference(start_time,end_time):
                            instance.sTime = end_time
                            instance.eTime = start_time
                            break_reason = "Found"
                            break
                        end_time_str = json_file["slices"][0]["data"]["itemdata"][key]["edate"]
                        if end_time_str:
                            end_time = hoursconversionrate(end_time_str)
                    if timeDifference("15:00:00",start_time) and break_reason!= "Found": 
                        instance.sTime = end_time
                        instance.eTime = "15:00:00"
        # print_schedule(json_file,commtime,instance,day)
        url = increment_date_in_url(url)

        response = requests.get(url, cookies=cookies)
        if response.status_code == 200:
            json_file = response.json()
        else:
            print("failure to  retrive json page")
    for cls in class_array:
        print("\n")
        print(cls.month)
        print(cls.day)
        print(cls.sTime)
        print(cls.eTime)
        print("\n")
    #Make sure the day variable is a numeric
    Booker.openwindow()
    Booker.checkrooms(class_array,First_name,Last_name,username)

        # get_day_of_week(json_file,url,cookies,commtime,instance)

#CLEAN UP THE DISPLAY, THE REST IS OK
#MOVE TO PHASE 2, CREATE SEPERATE CODE FOR GOOGLE CALENDAR
    


def credentials() -> None:
    global username,password
    username = input("Enter username:")
    password = input("Enter password:")

def retrieveID(driver):
    time.sleep(5)
    session_id = driver.get_cookie("session_id_edsby")["value"]

    return session_id

def retrieveStudentID(driver):
    current_url = str(driver.current_url)
    student_ID = extract_nums(current_url)

    return student_ID

def update_date_in_url(url):
    # Get today's date in YYYYMMDD format
    today_str = datetime.today().strftime("%Y%m%d")
    
    # Replace the last 8-digit date pattern in the URL
    updated_url = re.sub(r"\d{8}(?=$)", today_str, url)
    print(updated_url +"THE DATE OF TODAY")
    return updated_url
def split_full_name(full_name):
    parts = full_name.strip().split()
    if len(parts) >= 2:
        first_name = parts[0]
        last_name = ' '.join(parts[1:])
    else:
        first_name = parts[0]
        last_name = ''
    return first_name, last_name
def fetch_json(driver):
    session_ID = retrieveID(driver)
    student_ID = retrieveStudentID(driver)
    global First_name,Last_name
    cookies = {
            'session_id_edsby': session_ID  # Use the session_id you retrieved
        }
    url = f"https://asij.edsby.com/core/node.json/{student_ID}?xds=CalendarPanelNav_Student&targetDate=20250320"
    url = update_date_in_url(url)
    response = requests.get(url, cookies=cookies)
    if response.status_code == 200:
        print("succesful retrival of json page")
        print(response.json())
    else:
        print("failed to fetch page")
    data = response.json()
    name = data["slices"][0]["data"]["sidebar"]["wrap"]["controls"]["user"]["content"]["who"]["name"]
    First_name, Last_name = split_full_name(name)
    scraper(response.json(),session_ID,url)#use resppnse 
    


def automated_google_login()->None:
    credentials()
    chrome_options = Options()
    # chrome_options.add_argument("--headless") FIX FOR HEADLESS -> ERROR:An element was not found or took too long to be clickable.
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    # chrome_options.add_argument('--headless=new')
    service = Service(executable_path="/Users/yugoigarashi/dev/hackathon_project/chromedriver") 
    driver = uc.Chrome(service=service, options=chrome_options)

    driver.get("https://asij.edsby.com/p/BasePublic/")
    driver.maximize_window()

    try:
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "2loginform-integrations-google-0-text"))
        )
        login_button.click()
        time.sleep(1)
        
        driver.find_element(By.ID,"identifierId").send_keys(username)
        driver.find_element(By.ID,"identifierNext").click()

        password_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "Passwd"))
        )
        password_field.send_keys(password)

        driver.find_element(By.ID,"passwordNext").click()
        print(driver.current_url)
    except TimeoutException:
        print("An element was not found or took too long to be clickable.")
    fetch_json(driver)

def form_id(driver):
    class_name = "xdl-xdo xds-has-click xds-CalendarPanel-types-day_date CalendarPanel-banner-left-da"
    xpath = f"//div[contains(@class, '{class_name}')]"
    element = driver.find_element(By.XPATH,xpath)
    div_id_num = element.get_attribute("id")
    idnum = extract_nums(div_id_num)

    div_id = f"{idnum}CalendarPanelNav_Student-dayheader-schedule"
    return div_id

def get_html(url,path):
    response = requests.get(url)
    with open(path,'w',encoding='utf-8') as f:
        f.write(response.text)
        #will open up file at the path we have specified, 'w' stand for writing to this file

    # classes_for_today = block_attributes()
    # classes_for_today.blocks[0].startTime = data["slices"]["itemdata"]["r-1"]["sdate"]


automated_google_login()
time.sleep(1000000)

#To do until class:
#Make a month variable and make it accesible DONE
#add new feature of Booking.py that incorporates e.Time in it DONE
#add commtime feature for Booking.py -> LATER
#combine the two for results -> LATER
#make this all headless -> LATER


#Create UI: CLASS TIME2(THURSDAY, FRIDAY)


#TODO:
#Adjust everything so that the date of the url is contingent on today's 
#Make it headless selenium by the end of the project