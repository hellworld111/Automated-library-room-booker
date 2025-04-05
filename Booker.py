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
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import json
from datetime import datetime, timedelta
from datetime import datetime
import pyautogui
from flask import Flask, request, render_template
import time

driver = None
def convert_time(time_str):
    hours, minutes, _ = time_str.split(":")  # Split into hours, minutes, and seconds
    hours = str(int(hours))  # Convert to integer to remove leading zeros, then back to string
    return f"{hours}:{minutes}"

#set service
def openwindow():
    global driver
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    # chrome_driver_path = ChromeDriverManager().install() 
    # chrome_driver_path = ChromeDriverManager(version="134.0.0").install() 
    # service = Service(chrome_driver_path)
    driver = uc.Chrome(options=chrome_options)

    driver.get("https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ0dV0DAP_sP6kN23pnQPBN-PE3WUhee4J1-KhTiCWD65UMZn4bkXaJXe0PgKZup8vgNZC1XrFmp")
    driver.maximize_window()

def verify_aria_label(aria_label, block):
    # Regular expression to capture the month, day, and year from the aria-label
    match = re.match(r"(\w+), (\w+ \d{1,2}), \d{4}", aria_label)
    
    if match:
        # Extract month and day from the matched groups
        month_day = match.group(2)  # group(2) is the "Month Day" part
        month, day = month_day.split(' ')  # Split into month and day
        
        # Check if the extracted month and day match the month and day of the BlockAttributes instance
        print("Expected month and day\n")
        print(month + " " + day)
        print("THE MONTH AND DAY:")
        print(block.month)
        print(block.day)
        if block.month == month and block.day == int(day):  # Compare month and day
            return True  # Match found
        else:
            return False  # No match found
    else:
        return False  # Invalid aria_label format

def clean_time_string(time_str):
    cleaned = re.sub(r'[^0-9:]', '', time_str)
    
    match = re.match(r'(\d{1,2}:\d{2})', cleaned)
    
    return match.group(1) if match else cleaned

class block_attributes():
    def __init__(self):
        self.sTime = None
        self.eTime = None
        self.day = None
        self.month = None

# blocks = []
# instance = block_attributes()
# instance.sTime = "8:00:00"
# instance.eTime = "9:25:00"
# instance.day = 7
# instance.month = "April"
# blocks.append(instance)



First_name = "yugo"
Last_name = "Igarashi"
Email = "27igarashiy@asij.ac.jp"


def generate_time_slots(start_time, end_time):
    slots = []
    current_time = datetime.strptime(start_time, "%H:%M")
    end_time = datetime.strptime(end_time, "%H:%M")

    while current_time <= end_time:
        # Use %-I for Unix (Mac/Linux) and %#I for Windows
        formatted_time = current_time.strftime("%-I:%M") if current_time.strftime("%p") else current_time.strftime("%#I:%M")
        slots.append(formatted_time)
        current_time += timedelta(minutes=30)

    return slots

#MAIN PROBLEM: THE SLOTS ARE ALREADY BOOKED!
def bookrooms(block,child_div,First_name,Last_name,Email):
    # Re-find elements in each loop iteration to avoid stale element issues
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "xYUUDc"))
        )

        time_slots = generate_time_slots(block.sTime, block.eTime)
        for slot in time_slots:
            print(slot)
        MAX_ATTEMPTS = 10
        attempt = 0
        while time_slots and attempt<2: 
            attempt+=1
            child_div_2 = child_div.find_elements(By.CLASS_NAME, "W89NWb") 
            for child in child_div_2:
                try:
                    key_name = child.find_element(By.CLASS_NAME, "AeBiU-LgbsSe")
                    print(key_name)
                    aria_label = key_name.get_attribute('aria-label')
                    print(aria_label)
                    cleaned_time = clean_time_string(aria_label)
                    print(cleaned_time)
                    if cleaned_time in time_slots:
                        print(f"Booking slot: {cleaned_time}")
                        # input_credentials(key_name,First_name,Last_name,Email)
                        time_slots.remove(cleaned_time)

                    if not time_slots:  # Stop if all required slots are booked
                        return
                except Exception as e:
                    print(f"Error processing child: {e}")
                    continue  # Skip to the next element if there's an issue
        print("No slots available!")
        return
    except Exception as e:
        print(f"Error in bookrooms: {e}")

def round_to_nearest_30(time_str):
    # Convert the input string to a datetime object
    time_obj = datetime.strptime(time_str, "%H:%M")
    
    # Special case: If it's 1:45, round to 1:30
    if time_obj.hour == 1 and time_obj.minute == 45:
        return "1:30"
    
    minutes = time_obj.minute
    
    if minutes < 15:
        time_obj = time_obj.replace(minute=0)
    elif minutes < 45:
        time_obj = time_obj.replace(minute=30)
    else:
        time_obj = time_obj.replace(minute=0) + timedelta(hours=1)
    return time_obj.strftime("%-H:%M")

def input_credentials(div,First_name,Last_name,Email):
    time.sleep(0.5)
    div.click()
    #Works until here in the second trial
    def send_keys_if_exists():
        input_values = {
            0: First_name,
            1: Last_name,
            2: Email
        }
        inputs = driver.find_elements(By.CLASS_NAME,"qdOxv-fmcmS-wGMbrd")
        for index, input_element in enumerate(inputs):
            if index in input_values:
                input_element.send_keys(input_values[index])

    send_keys_if_exists()
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "YUhpIc-LgbsSe"))
    )
    element.click()

    WebDriverWait(driver, 10).until(
        lambda driver: driver.execute_script('return document.readyState') == 'complete'
    )
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "fVXLmf"))
    )
    close_button = driver.find_element(By.XPATH, '//*[@jsname="plIjzf"]')
    close_button.click()

class BreakLoopException(Exception):
    pass
def is_later(time1, time2):
    t1 = datetime.strptime(time1, "%H:%M")
    t2 = datetime.strptime(time2, "%H:%M")
    
    return t1 > t2

def checkrooms(blocks,First_name,Last_name,Email):
    time.sleep(5)
    for block in blocks[:4]:# CONVERT ALL OFF BLOCK ETIME AND STIME TO THE STANDARDIZED TIME, 1:00 or 2:00, not 9:25:00 or 11:00:00
        MAX_ATTEMPTS = 10
        attempt = 0
        if block.sTime == None and block.eTime == None:
            continue
        block.sTime = convert_time(block.sTime)
        block.eTime = convert_time(block.eTime)
        block.sTime = round_to_nearest_30(block.sTime)
        base_condition = False
        while not base_condition and attempt < MAX_ATTEMPTS:  # Keep repeating until the base_condition is True
            # while len(driver.find_elements(By.CLASS_NAME, "BCRc3d")) == 0:
            #     print("Page might be stuck. Refreshing...")
            #     driver.refresh()
            #     WebDriverWait(driver, 5).until(
            #         EC.presence_of_element_located((By.CLASS_NAME, "BCRc3d"))
            # )
            while True:
                try:
                    rooms = WebDriverWait(driver, 2).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "AeBiU-LgbsSe"))
                    )
                    if rooms:
                        print("✅ Found rooms!")
                        break  
                except:
                    driver.refresh()  
                    time.sleep(2)

            divs = driver.find_elements(By.CLASS_NAME, "BCRc3d")
            print(block.sTime)
            print(block.eTime)
            print(block.day)
            print(block.month)
            for div in divs:
                print(" DIVS!")
                if base_condition:
                    break
                child_div = div.find_elements(By.CLASS_NAME, "xYUUDc")
                for child in child_div:
                    print(" DIVS!")
                    aria_label = child.get_attribute('aria-label')
                    if verify_aria_label(aria_label, block) == True:
                        print("PROBLEM IN HERE")
                        print(aria_label)
                        print("about to book")
                        bookrooms(block, child,First_name,Last_name,Email)
                        print("\n"+ block.sTime+"\n")#PROBLEM: The child variable that is passed in bookrooms is empty
                        base_condition = True
                        break
            if not base_condition:
                # If base_condition is still False, click the last button and repeat the loop
                click_bt = driver.find_elements(By.CLASS_NAME, "pYTkkf-Bz112c-RLmnJb")
                click_bt[3].click()
                print("clicked")

    # After the base_condition is met, the outer loop will move to the next block

#Func that checks if clickable