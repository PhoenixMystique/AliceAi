"""
JobSailor - Logging Module
Handles all file-based logging operations
"""

import os
import json
from datetime import datetime

def setup_log_directories(log_directory="logs"):
    """Create necessary directories for logs"""
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
        print(f"Created logs directory: {log_directory}")
    
    # Create subdirectories for different log types
    subdirs = ["applications", "questions", "preferences", "errors"]
    for subdir in subdirs:
        path = os.path.join(log_directory, subdir)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created log subdirectory: {path}")
    
    return log_directory

def get_log_path(log_type, config):
    """Get the path for a specific log file"""
    log_directory = config.get("log_directory", "logs")
    
    # Map log type to subdirectory
    subdir_map = {
        "applications": "applications",
        "questions": "questions",
        "preferences": "preferences",
        "errors": "errors"
    }
    
    subdir = subdir_map.get(log_type, "")
    return os.path.join(log_directory, subdir)

def save_job_log(job_data, config):
    """Save job application log to JSON file"""
    log_file = os.path.join(get_log_path("applications", config), "job_applications_log.json")
    
    # Load existing data if the file exists
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            # File exists but is not valid JSON
            logs = {
                "preferences": config.get("preferences", {}),
                "applications": []
            }
    else:
        logs = {
            "preferences": config.get("preferences", {}),
            "applications": []
        }
    
    # Add new job application data
    logs["applications"].append(job_data)
    
    # Add error logs section if it doesn't exist and this is an error
    if "error_logs" not in logs:
        logs["error_logs"] = []
    
    # If this is an error, also add to error_logs
    if job_data.get("status") == "failed":
        error_log = {
            "timestamp": job_data["application_time"],
            "url": job_data["job_url"],
            "error_type": job_data.get("error_reason", "unknown"),
            "details": job_data.get("error_details", "No details provided")
        }
        logs["error_logs"].append(error_log)
        
        # Also save to separate error log
        save_error_log(error_log, config)
    
    # Save updated logs
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)
    
    print(f"Job application logged to {log_file}")

def save_question_log(question_data, config):
    """Save application question log to JSON file"""
    log_file = os.path.join(get_log_path("questions", config), "application_questions_log.json")
    
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
    """Save preference match decision to JSON file"""
    log_file = os.path.join(get_log_path("preferences", config), "job_preference_matches.json")
    
    # Load existing data if the file exists
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            # File exists but is not valid JSON
            logs = {"preference_matches": []}
    else:
        logs = {"preference_matches": []}
    
    # Add new match data
    logs["preference_matches"].append(match_data)
    
    # Save updated logs
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)
    
    print(f"Preference match decision logged to {log_file}")

def save_error_log(error_data, config):
    """Save error log to separate JSON file"""
    log_file = os.path.join(get_log_path("errors", config), "errors_log.json")
    
    # Load existing data if the file exists
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            # File exists but is not valid JSON
            logs = {"errors": []}
    else:
        logs = {"errors": []}
    
    # Add new error data
    logs["errors"].append(error_data)
    
    # Save updated logs
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)

def log_summary(successful_applications, failed_applications, config):
    """Log summary of application session"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary_data = {
        "timestamp": timestamp,
        "successful_applications": successful_applications,
        "failed_applications": failed_applications,
        "total_processed": successful_applications + failed_applications
    }
    
    # Save to summary log
    log_file = os.path.join(config.get("log_directory", "logs"), "summary_log.json")
    
    # Load existing data if the file exists
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            # File exists but is not valid JSON
            logs = {"sessions": []}
    else:
        logs = {"sessions": []}
    
    # Add new session data
    logs["sessions"].append(summary_data)
    
    # Save updated logs
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)
    
    print(f"\nApplication process completed. Applied to {successful_applications} jobs. Failed: {failed_applications}")
    print(f"Total processed: {successful_applications + failed_applications}")
    print(f"Summary logged to {log_file}")
    
    # Print paths to all log files
    log_directory = config.get("log_directory", "logs")
    print(f"Application logs saved to {os.path.join(log_directory, 'applications', 'job_applications_log.json')}")
    print(f"Question logs saved to {os.path.join(log_directory, 'questions', 'application_questions_log.json')}")
    print(f"Preference match logs saved to {os.path.join(log_directory, 'preferences', 'job_preference_matches.json')}")
