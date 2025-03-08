"""
JobSailor - Selenium Utilities Module
Handles browser setup and common Selenium operations
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_browser(browser_settings=None):
    """Set up and configure the browser"""
    if browser_settings is None:
        browser_settings = {}
        
    # Setup Chrome options
    options = Options()
    options.add_argument("--start-maximized")
    
    # Add any additional options from settings
    for option in browser_settings.get("chrome_options", []):
        options.add_argument(option)
    
    # Create a profile directory
    profile_dir = browser_settings.get("profile_directory", os.path.join(os.getcwd(), "profile"))
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)
        print(f"Created Chrome profile directory: {profile_dir}")
    else:
        print(f"Using existing Chrome profile directory: {profile_dir}")

    options.add_argument(f"--user-data-dir={profile_dir}")

    # Auto-download and setup ChromeDriver
    print("Downloading/setting up ChromeDriver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver

def close_browser(driver):
    """Safely close the browser"""
    if driver:
        driver.quit()
    print("Browser closed.")

def is_html_response(content):
    """Check if content is HTML"""
    if isinstance(content, str):
        return content.strip().startswith("<!DOCTYPE html>") or "<html" in content.lower()[:500]
    return False

def handle_privacy_agreement(driver):
    """Detect and handle privacy agreement popups by clicking 'Yes' or 'Agree' buttons."""
    try:
        # Check for splashscreen container which often contains privacy dialogs
        splash_screens = driver.find_elements(By.CLASS_NAME, "styles_splashscreen-container__jxBax")
        if splash_screens:
            print("Splash screen detected, waiting for content to load...")
            time.sleep(2)
            
        # Check for chatbot-style Yes buttons (chips)
        chip_buttons = driver.find_elements(By.XPATH, "//div[contains(@class, 'chatbot_Chip') and contains(@class, 'chipInRow')]/span[text()='Yes']")
        if not chip_buttons:
            chip_buttons = driver.find_elements(By.XPATH, "//div[contains(@class, 'chatbot_Chip')]/span[text()='Yes']")
        if not chip_buttons:
            chip_buttons = driver.find_elements(By.XPATH, "//div[@class='chips']//span[text()='Yes']/..")
        
        if chip_buttons:
            print("Chatbot chip 'Yes' button detected, attempting to click...")
            for button in chip_buttons:
                try:
                    # Try different click methods
                    try:
                        button.click()
                        print("Clicked chatbot 'Yes' chip button with direct click")
                    except Exception:
                        driver.execute_script("arguments[0].click();", button)
                        print("Clicked chatbot 'Yes' chip button with JavaScript")
                    time.sleep(2)
                    return True
                except Exception as e:
                    print(f"Failed to click chatbot chip button: {e}")
                    try:
                        id_buttons = driver.find_elements(By.XPATH, "//div[starts-with(@id, '_u') and contains(@class, 'chatbot_Chip')]")
                        if id_buttons:
                            driver.execute_script("arguments[0].click();", id_buttons[0])
                            print("Clicked chip button by ID pattern")
                            time.sleep(2)
                            return True
                    except Exception as e2:
                        print(f"Failed to click by ID pattern: {e2}")
            
        # Look for common privacy agreement buttons by text
        privacy_buttons = driver.find_elements(By.XPATH, 
            "//button[contains(text(), 'Yes') or contains(text(), 'Agree') or contains(text(), 'Accept') or contains(text(), 'Allow')]")
        
        if privacy_buttons:
            print("Privacy agreement popup detected, clicking accept button...")
            for button in privacy_buttons:
                try:
                    driver.execute_script("arguments[0].click();", button)
                    print("Clicked privacy button with text: " + button.text)
                    time.sleep(1)
                    return True
                except Exception as e:
                    print(f"Failed to click button: {e}")
                    continue
        
        # Look for cookie consent buttons
        cookie_buttons = driver.find_elements(By.XPATH, 
            "//*[contains(@class, 'cookie') and (contains(@class, 'btn') or contains(@class, 'button'))]")
        
        if cookie_buttons:
            print("Cookie consent buttons found, attempting to click...")
            for button in cookie_buttons:
                try:
                    driver.execute_script("arguments[0].click();", button)
                    print("Clicked cookie button")
                    time.sleep(1)
                    return True
                except Exception as e:
                    print(f"Failed to click cookie button: {e}")
            
        # Check if we're still on a splash screen
        if "styles_splashscreen-container__jxBax" in driver.page_source:
            # Try clicking any visible button as a last resort
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if button.is_displayed():
                    try:
                        driver.execute_script("arguments[0].click();", button)
                        print("Clicked button as fallback")
                        time.sleep(1)
                        return True
                    except:
                        continue
        
        # Comprehensive fallback for chatbot chips
        if "chipsContainer" in driver.page_source:
            print("Found chipsContainer, attempting to click any visible Yes/Accept button...")
            try:
                chip_spans = driver.find_elements(By.XPATH, 
                    "//div[contains(@class, 'chip')]//span[contains(text(), 'Yes') or contains(text(), 'Accept')]")
                
                for span in chip_spans:
                    try:
                        parent = span.find_element(By.XPATH, "./..")
                        driver.execute_script("arguments[0].click();", parent)
                        print(f"Clicked chip parent containing: {span.text}")
                        time.sleep(2)
                        return True
                    except Exception as e:
                        print(f"Failed to click chip parent: {e}")
                        try:
                            driver.execute_script("arguments[0].click();", span)
                            print(f"Clicked chip span directly: {span.text}")
                            time.sleep(2)
                            return True
                        except Exception as e2:
                            print(f"Failed to click span directly: {e2}")
            except Exception as e:
                print(f"Error with comprehensive chip fallback: {e}")
        
        return False
    except Exception as e:
        print(f"Error handling privacy agreement: {e}")
        return False

def capture_screenshot(driver, filename):
    """Capture a screenshot of the current browser state"""
    try:
        driver.save_screenshot(filename)
        print(f"Screenshot saved: {filename}")
        return True
    except Exception as e:
        print(f"Failed to capture screenshot: {e}")
        return False

def wait_for_element(driver, selector, by=By.CSS_SELECTOR, timeout=10):
    """Wait for an element to become available"""
    try:
        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.presence_of_element_located((by, selector)))
        return element
    except Exception as e:
        print(f"Timeout waiting for element '{selector}': {e}")
        return None

def scroll_to_element(driver, element):
    """Scroll to make an element visible"""
    try:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"Failed to scroll to element: {e}")
        return False
