#https://color.method.ac 
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
#firefox binary
path = r'/Applications/Firefox.app/Contents/MacOS/firefox'
geckodriver = r'/Users/grahamzemel/Downloads/geckodriver'
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pyautogui
import time

def get_rgb_values(style_attribute):
    rgb = style_attribute.split(": ")[1].replace("rgb", "").replace("(", "").replace(")", "").replace(";", "")
    return tuple(map(int, rgb.split(", ")))

def colorChecker(driver):
    # time.sleep(1)
    wheel = driver.find_element(By.ID, "wheel")
    wheel_location = wheel.location
    wheel_size = wheel.size
    
    # Calculate the center of the wheel
    center_x = wheel_location['x'] + wheel_size['width'] // 2
    center_y = wheel_location['y'] + wheel_size['height'] // 2
    
    # Move the mouse to the center of the wheel
    pyautogui.moveTo(center_x, center_y)
    
    target_color = get_rgb_values(driver.find_element(By.ID, "clockcolor").get_attribute("style"))
    current_color = get_rgb_values(driver.find_element(By.ID, "matchcolor").get_attribute("style"))
    
    # While loop to find the matching color
    while not current_color == target_color:
        # Get the current pixel color at the center
        target_color = get_rgb_values(driver.find_element(By.ID, "clockcolor").get_attribute("style"))
        current_color = get_rgb_values(driver.find_element(By.ID, "matchcolor").get_attribute("style"))

        print(target_color)
        print(current_color)

        # custom tolerance function by 1px
        if target_color[0] - 1 <= current_color[0] <= target_color[0] + 1 and target_color[1] - 1 <= current_color[1] <= target_color[1] + 1 and target_color[2] - 1 <= current_color[2] <= target_color[2] + 1:
            break
        
        # Logic to move the mouse closer or further away
        # pyautogui.moveRel(10, 0)  # Move mouse 10 pixels to the right
        
        # Add a sleep to prevent too fast movements
        time.sleep(1)
    
    # When the color matches, perform the desired action (like a mouse click)
    pyautogui.click()

def main():
    options = Options()
    options.binary = path
    driver = webdriver.Firefox(options=options, executable_path=geckodriver)
    # go to website
    driver.get("https://color.method.ac")
    time.sleep(1)
    driver.find_element(By.ID, "start").click()
    time.sleep(6)
    while True:
        colorChecker(driver)
main()