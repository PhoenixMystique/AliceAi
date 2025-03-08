#!/usr/bin/env python3
"""
JobSailor - Automated job application tool
Main entry point for the application
"""

import os
import json
import time
from selenium import webdriver

from selenium_utils import setup_browser, close_browser, handle_privacy_agreement
from job_processor import extract_job_links, process_job
from logger import setup_log_directories, log_summary

def load_configuration(config_file="customization.json"):
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return {}

def main():
    """Main entry point for JobSailor application"""
    # Load configuration
    config = load_configuration()
    
    # Setup logging directories
    setup_log_directories(config.get("log_directory", "logs"))
    
    # Set up browser
    driver = setup_browser(
        config.get("browser_settings", {})
    )
    
    # Navigate to the job search page
    search_url = config.get("job_search_url", "https://www.naukri.com/python-developer-jobs")
    print(f"Navigating to: {search_url}")
    driver.get(search_url)
    
    # Wait for page to load
    time.sleep(config.get("page_load_wait_time", 5))
    
    # Extract job links
    job_links = extract_job_links(driver, config)
    
    # Process jobs
    max_applications = config.get("max_applications", 500)
    successful_applications = 0
    failed_applications = 0
    
    # Process each job link
    for job_url in job_links:
        if successful_applications >= max_applications:
            break
            
        print(f"\nProcessing job: {job_url}")
        driver.get(job_url)
        time.sleep(3)
        
        # Handle privacy agreements or consent popups
        attempts = 0
        while attempts < 3 and handle_privacy_agreement(driver):
            print("Privacy/consent popup handled, checking if there are more...")
            time.sleep(2)
            attempts += 1
        
        # Process this job
        success = process_job(driver, job_url, config)
        
        if success:
            successful_applications += 1
        else:
            failed_applications += 1
    
    # Log summary
    log_summary(successful_applications, failed_applications, config)
    
    # Close browser
    close_browser(driver)

if __name__ == "__main__":
    main()
