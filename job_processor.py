"""
JobSailor - Job Processing Module
Handles job extraction, matching, and application
"""

import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium_utils import is_html_response
from logger import (save_job_log, save_question_log, save_preference_match_log)
from gemini_api import bard_flash_response

def extract_job_links(driver, config):
    """Extract job links from the search results page"""
    print("Extracting job links...")
    job_links = []
    wait = WebDriverWait(driver, 10)
    
    try:
        # Wait for job cards to load
        job_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.jobTuple")))
        
        # Extract links from job cards
        for card in job_cards:
            try:
                link_element = card.find_element(By.CSS_SELECTOR, "a.title")
                job_url = link_element.get_attribute("href")
                job_links.append(job_url)
                print(f"Found job link: {job_url}")
            except Exception as e:
                print(f"Error extracting job link from card: {e}")
                continue
    except Exception as e:
        print(f"Error waiting for job cards: {e}")
        
        # Fallback method if the above selector doesn't work
        try:
            link_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/job-listings']")
            for link in link_elements:
                job_url = link.get_attribute("href")
                if job_url and "/job-listings" in job_url and job_url not in job_links:
                    job_links.append(job_url)
                    print(f"Found job link (fallback): {job_url}")
        except Exception as e:
            print(f"Error with fallback link extraction: {e}")
    
    # Limit number of links based on configuration
    max_jobs_to_process = config.get("max_jobs_to_process", len(job_links))
    job_links = job_links[:max_jobs_to_process]
    
    print(f"Total job links found: {len(job_links)}")
    return job_links

def extract_job_details(driver):
    """Extract basic job details from the job page"""
    job_details = {
        "job_url": driver.current_url,
        "application_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": "",
        "company": "",
    }
    
    # Check if the page is an HTML error page
    page_source = driver.page_source
    if is_html_response(page_source) and "splashscreen-container" in page_source:
        print("Detected HTML error page instead of job details")
        job_details["status"] = "failed"
        job_details["error_reason"] = "html_response"
        job_details["error_details"] = "Received HTML error page instead of job data"
        
        # Try to extract title from URL if available
        try:
            url_parts = driver.current_url.split('?')
            if len(url_parts) > 0 and "jobTitle=" in url_parts[0]:
                title_param = [p for p in url_parts[0].split('&') if p.startswith("jobTitle=")]
                if title_param:
                    job_details["title"] = title_param[0].replace("jobTitle=", "").replace("+", " ")
        except Exception as e:
            print(f"Error extracting title from URL: {e}")
        
        return job_details
    
    try:
        # Try to get job title
        title_elements = driver.find_elements(By.CSS_SELECTOR, "h1.jd-header-title")
        if title_elements:
            job_details["title"] = title_elements[0].text
    except Exception as e:
        print(f"Error extracting job title: {e}")
    
    try:
        # Try to get company name
        company_elements = driver.find_elements(By.CSS_SELECTOR, "div.jd-header-comp-name a")
        if company_elements:
            job_details["company"] = company_elements[0].text
    except Exception as e:
        print(f"Error extracting company name: {e}")
    
    return job_details

def extract_detailed_job_info(driver):
    """Extract detailed job information for preference matching"""
    job_info = extract_job_details(driver)
    
    # If already identified as an HTML error response, return early
    if job_info.get("status") == "failed" and job_info.get("error_reason") == "html_response":
        return job_info
    
    # Add job description
    try:
        job_description_elements = driver.find_elements(By.CSS_SELECTOR, "div.job-desc")
        if job_description_elements:
            job_info["description"] = job_description_elements[0].text
        else:
            # Try alternative selector
            job_description_elements = driver.find_elements(By.XPATH, "//section[contains(@class, 'job-desc')]")
            if job_description_elements:
                job_info["description"] = job_description_elements[0].text
            else:
                job_info["description"] = ""
    except Exception as e:
        print(f"Error extracting job description: {e}")
        job_info["description"] = ""
    
    # Add job requirements
    try:
        requirements_elements = driver.find_elements(By.CSS_SELECTOR, "div.key-skill")
        if requirements_elements:
            job_info["requirements"] = requirements_elements[0].text
        else:
            # Try alternative selector
            requirements_elements = driver.find_elements(By.XPATH, "//section[contains(@class, 'requirements')]")
            if requirements_elements:
                job_info["requirements"] = requirements_elements[0].text
            else:
                job_info["requirements"] = ""
    except Exception as e:
        print(f"Error extracting job requirements: {e}")
        job_info["requirements"] = ""
    
    # Add experience required
    try:
        exp_elements = driver.find_elements(By.CSS_SELECTOR, "span.exp")
        if exp_elements:
            job_info["experience"] = exp_elements[0].text
    except Exception as e:
        print(f"Error extracting experience requirement: {e}")
    
    # Add location
    try:
        location_elements = driver.find_elements(By.CSS_SELECTOR, "span.loc")
        if location_elements:
            job_info["location"] = location_elements[0].text
    except Exception as e:
        print(f"Error extracting job location: {e}")
    
    return job_info

def job_matches_preferences(driver, job_info, config):
    """Check if a job matches the user's preferences"""
    print("Evaluating job against your preferences...")
    
    # Get job preferences from config
    job_preferences = config.get("job_preferences", "")
    
    # Prepare prompt for AI
    prompt = f"""
    My job preferences:
    {job_preferences}
    
    Job details:
    Title: {job_info.get('title', 'Not specified')}
    Company: {job_info.get('company', 'Not specified')}
    Location: {job_info.get('location', 'Not specified')}
    Experience required: {job_info.get('experience', 'Not specified')}
    
    Description:
    {job_info.get('description', 'Not specified')}
    
    Requirements:
    {job_info.get('requirements', 'Not specified')}
    
    Based on the above information, does this job match my preferences?
    Please respond with 'yes' if it's a good match, or 'no' if it's not a good match.
    Also provide a brief reason in one sentence.
    """
    
    # Get response from AI
    response = bard_flash_response(prompt)
    print(f"AI response: {response}")
    
    # Parse the response
    match_decision = False
    match_reason = "No clear reason provided"
    
    if response.lower().startswith("yes"):
        match_decision = True
        match_reason = response
    elif " yes " in response.lower():
        match_decision = True
        match_reason = response
    else:
        match_reason = response
    
    # Log the decision
    match_data = {
        "job_url": job_info["job_url"],
        "job_title": job_info.get("title", "Not specified"),
        "company": job_info.get("company", "Not specified"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "matches_preferences": match_decision,
        "ai_response": response
    }
    save_preference_match_log(match_data, config)
    
    return match_decision, match_reason

def handle_radio_buttons(driver, job_info, config):
    """Handle radio button questions during application"""
    wait = WebDriverWait(driver, 10)
    try:
        radio_buttons = WebDriverWait(driver, 1).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ssrc__radio-btn-container"))
        )

        question = driver.find_element(By.XPATH, "//li[contains(@class, 'botItem')]/div/div/span").text
        print(question)

        options = []
        for index, button in enumerate(radio_buttons, start=1):
            label = button.find_element(By.CSS_SELECTOR, "label")
            value = button.find_element(By.CSS_SELECTOR, "input").get_attribute("value")
            options.append(f"{index}. {label.text} (Value: {value})")
            print(options[-1])

        options_str = "\n".join(options)
        user_input_message = f"{question}\n{options_str}"

        # Log the question and options
        question_data = {
            "job_url": driver.current_url,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question_type": "multiple_choice",
            "question": question,
            "options": options,
            "job_title": job_info.get("title", ""),
            "company": job_info.get("company", "")
        }

        save_question_log(question_data, config)

        selected_option = int(bard_flash_response(user_input_message))

        selected_button = radio_buttons[selected_option - 1].find_element(By.CSS_SELECTOR, "input")
        driver.execute_script("arguments[0].click();", selected_button)

        save_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div[1]/div[3]/div/div")))
        save_button.click()

        success_message = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH,
                                           "//span[contains(@class, 'apply-message') and contains(text(), 'successfully applied')]")))
        if success_message:
            # Log successful application
            job_data = extract_job_details(driver)
            job_data["status"] = "success"
            job_data["application_method"] = "radio_buttons"
            save_job_log(job_data, config)
            return True

        return False
    except Exception as e:
        print(f"Error handling radio buttons: {e}")
        return False

def handle_text_input(driver, job_info, config):
    """Handle text input questions during application"""
    wait = WebDriverWait(driver, 10)
    try:
        chat_list = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, "//ul[contains(@id, 'chatList_')]"))
        )

        li_elements = chat_list.find_elements(By.TAG_NAME, "li")
        last_question_text = None

        if li_elements:
            last_li_element = li_elements[-1]
            last_question_text = last_li_element.text
            print("Last question text:", last_question_text)

            # Log the text question
            question_data = {
                "job_url": driver.current_url,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "question_type": "text_input",
                "question": last_question_text,
                "job_title": job_info.get("title", ""),
                "company": job_info.get("company", "")
            }
            save_question_log(question_data, config)
        else:
            print("No <li> elements found.")
            return False

        response = bard_flash_response(last_question_text)
        input_field = driver.find_element(By.XPATH, "//div[@class='textArea']")

        if last_question_text == "Date of Birth":
            dob = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//ul[contains(@id, 'dob__input-container')]"))
            )
            dob.send_keys("68767868")

        if response:
            input_field.send_keys(response)
        else:
            input_field.send_keys("None")
            print("No response from bard_flash_response.")
        time.sleep(1)

        save_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div[1]/div[3]/div/div")))
        save_button.click()

        success_message = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH,
                                           "//span[contains(@class, 'apply-message') and contains(text(), 'successfully applied')]")))
        if success_message:
            # Log successful application
            job_data = extract_job_details(driver)
            job_data["status"] = "success"
            job_data["application_method"] = "text_input"
            save_job_log(job_data, config)
            return True

        return False
    except Exception as e:
        print(f"Error handling text input: {e}")
        return False

def process_job(driver, job_url, config):
    """Process a single job - check match, apply, handle questions"""
    # Add error counter for this job
    job_error_count = 0
    status = True
    
    # Extract detailed job information
    job_info = extract_detailed_job_info(driver)
    
    # Check if we got an HTML error response
    if job_info.get("status") == "failed" and job_info.get("error_reason") == "html_response":
        print(f"Failed to load job details: {job_info.get('error_details')}")
        save_job_log(job_info, config)
        return False
    
    # Check if job matches preferences
    try:
        matches_preferences, match_reason = job_matches_preferences(driver, job_info, config)
        
        if not matches_preferences:
            print(f"Job doesn't match your preferences. Reason: {match_reason}")
            print("Skipping this job.")
            return False
        
        print(f"Job matches your preferences! Reason: {match_reason}")
        print("Proceeding with application...")
    except Exception as e:
        print(f"Error during preference matching: {e}")
        job_error_count += 1
        if job_error_count > 2:
            print(f"Too many errors for this job (error count: {job_error_count}). Skipping.")
            
            # Log the error but don't mark it as a successful application
            error_data = {
                "job_url": job_url,
                "application_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "title": job_info.get("title", ""),
                "company": job_info.get("company", ""),
                "status": "failed",
                "error_reason": "multiple_errors",
                "error_details": f"Encountered {job_error_count} errors while processing job"
            }
            save_job_log(error_data, config)
            return False
    
    try:
        already_applied_elements = driver.find_elements(By.ID, "already-applied")
        if already_applied_elements:
            print("Already applied to this job. Skipping.")
            return False

        alert_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'styles_alert-message-text__')]")
        if alert_elements:
            print("Alert message found. Skipping job.")
            return False

        company_site_buttons = driver.find_elements(By.ID, "company-site-button")
        jd_container_elements = driver.find_elements(By.CLASS_NAME, "jdContainer")

        if company_site_buttons:
            print("External application required. Skipping.")
            return False
        elif jd_container_elements:
            print("Special JD container found. Skipping.")
            return False

    except Exception as e:
        print(f"Error checking job status: {e}")
        job_error_count += 1
        if job_error_count > 2:
            print(f"Too many errors for this job (error count: {job_error_count}). Skipping.")
            return False
            
        try:
            alert_message = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'styles_alert-message-text')]"))
            )
            if alert_message.text:
                print(f"Alert message: {alert_message.text}. Skipping.")
                return False
        except:
            pass

    try:
        if already_applied_elements:
            return False
            
        driver.find_element(By.XPATH, "//*[text()='Apply']").click()

        success_message = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH,"//span[contains(@class, 'apply-message') and contains(text(), 'successfully applied')]")))
        print("Successfully applied.")
        
        # Log successful application
        job_data = extract_job_details(driver)
        job_data["status"] = "success"
        save_job_log(job_data, config)
        
        time.sleep(3)
        if success_message:
            return True

    except Exception as e:
        print(f"Error during initial apply attempt: {e}")
        job_error_count += 1
        if job_error_count > 2:
            print(f"Too many errors for this job (error count: {job_error_count}). Skipping.")
            
            # Log the error but don't mark as success
            error_data = {
                "job_url": job_url,
                "application_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "title": job_info.get("title", ""),
                "company": job_info.get("company", ""),
                "status": "failed",
                "error_reason": "multiple_errors",
                "error_details": f"Encountered {job_error_count} errors during application process"
            }
            save_job_log(error_data, config)
            return False
        
    # Handle additional application steps
    while status:
        # Try radio buttons first
        try:
            if handle_radio_buttons(driver, job_info, config):
                return True
        except Exception as e:
            print(f"Error during radio button handling: {e}")
            job_error_count += 1
            
        # Try text input if radio buttons didn't work
        try:
            if handle_text_input(driver, job_info, config):
                return True
        except Exception as e:
            print(f"Error during text input handling: {e}")
            job_error_count += 1
            
        # Check for success messages as fallback
        try:
            apply_status_header = driver.find_elements(By.XPATH,"//div[contains(@class, 'apply-status-header') and contains(@class, 'green')]")
            if apply_status_header:
                # Log successful application
                job_data = extract_job_details(driver)
                job_data["status"] = "success"
                job_data["application_method"] = "green_header"
                save_job_log(job_data, config)
                return True
                
            success_message_elements = driver.find_elements(By.XPATH,
                                                          "//span[contains(@class, 'apply-message') and contains(text(), 'You have successfully applied')]")
            if success_message_elements:
                # Log successful application if not already logged
                job_data = extract_job_details(driver)
                job_data["status"] = "success"
                job_data["application_method"] = "final_check"
                save_job_log(job_data, config)
                return True
        except Exception as e:
            print(f"Error during success check: {e}")
            
        # Check if we've hit the error limit
        job_error_count += 1
        if job_error_count > 2:
            print(f"Too many errors for this job (error count: {job_error_count}). Skipping.")
            
            # Log the error
            error_data = {
                "job_url": job_url,
                "application_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "title": job_info.get("title", ""),
                "company": job_info.get("company", ""),
                "status": "failed",
                "error_reason": "multiple_errors_chat_list",
                "error_details": f"Encountered {job_error_count} errors processing chat interactions"
            }
            save_job_log(error_data, config)
            return False
            
    return False
