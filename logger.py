"""
JobSailor - Logging Module
Handles all file-based logging operations
"""

import os
import json
from datetime import datetime

def setup_log_directories(log_directory="logs"):
    """Create necessary directory for logs"""
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
        print(f"Created logs directory: {log_directory}")
    
    return log_directory

def save_job_log(job_data, config):
    """Save job application log to JSON file"""
    log_directory = config.get("log_directory", "logs")
    log_file = os.path.join(log_directory, "application_logs.json")
    
    # Load existing data if the file exists
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            # File exists but is not valid JSON
            logs = {
                "preferences": config.get("preferences", {}),
                "applications": [],
                "preference_matches": [],
                "errors": []
            }
    else:
        logs = {
            "preferences": config.get("preferences", {}),
            "applications": [],
            "preference_matches": [],
            "errors": []
        }
    
    # Add new job application data
    logs["applications"].append(job_data)
    
    # If this is an error, also add to errors list
    if job_data.get("status") == "failed":
        error_log = {
            "timestamp": job_data["application_time"],
            "url": job_data["job_url"],
            "error_type": job_data.get("error_reason", "unknown"),
            "details": job_data.get("error_details", "No details provided")
        }
        logs["errors"].append(error_log)
    
    # Save updated logs
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)
    
    print(f"Job application logged to {log_file}")

def save_question_log(question_data, config):
    """Save application question log to JSON file"""
    log_directory = config.get("log_directory", "logs")
    log_file = os.path.join(log_directory, "qa_logs.json")
    
    # Load existing data if the file exists
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            # File exists but is not valid JSON
            logs = {"questions": []}
    else:
        logs = {"questions": []}
    
    # Add new question data
    logs["questions"].append(question_data)
    
    # Save updated logs
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)
    
    print(f"Question logged to {log_file}")

def save_preference_match_log(match_data, config):
    """Save preference match decision to application logs file"""
    log_directory = config.get("log_directory", "logs")
    log_file = os.path.join(log_directory, "application_logs.json")
    
    # Load existing data if the file exists
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            # File exists but is not valid JSON
            logs = {
                "preferences": config.get("preferences", {}),
                "applications": [],
                "preference_matches": [],
                "errors": []
            }
    else:
        logs = {
            "preferences": config.get("preferences", {}),
            "applications": [],
            "preference_matches": [],
            "errors": []
        }
    
    # Add new match data
    logs["preference_matches"].append(match_data)
    
    # Save updated logs
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)
    
    print(f"Preference match decision logged to {log_file}")

def log_summary(successful_applications, failed_applications, config):
    """Log summary of application session to the application logs file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary_data = {
        "timestamp": timestamp,
        "successful_applications": successful_applications,
        "failed_applications": failed_applications,
        "total_processed": successful_applications + failed_applications
    }
    
    # Save to application logs
    log_directory = config.get("log_directory", "logs")
    log_file = os.path.join(log_directory, "application_logs.json")
    
    # Load existing data if the file exists
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            # File exists but is not valid JSON
            logs = {
                "preferences": config.get("preferences", {}),
                "applications": [],
                "preference_matches": [],
                "errors": [],
                "sessions": []
            }
    else:
        logs = {
            "preferences": config.get("preferences", {}),
            "applications": [],
            "preference_matches": [],
            "errors": [],
            "sessions": []
        }
    
    # Add new session data
    if "sessions" not in logs:
        logs["sessions"] = []
        
    logs["sessions"].append(summary_data)
    
    # Save updated logs
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)
    
    print(f"\nApplication process completed. Applied to {successful_applications} jobs. Failed: {failed_applications}")
    print(f"Total processed: {successful_applications + failed_applications}")
    print(f"Session summary and all application logs saved to {log_file}")
    print(f"Q&A logs saved to {os.path.join(log_directory, 'qa_logs.json')}")
