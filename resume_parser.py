"""
Resume Parser Module
Handles PDF resume parsing and data extraction
"""

import os
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('resume_parser')

def get_resume_data(config):
    """
    Get resume data from PDF or fallback to default data
    Returns a dictionary of resume information
    """
    logger.info("Attempting to load resume data")
    
    # Check if resume settings are configured
    if not config.get("resume_settings"):
        logger.warning("No resume settings found in config")
        return create_fallback_resume(config)
    
    resume_settings = config.get("resume_settings", {})
    use_pdf = resume_settings.get("use_pdf_resume", True)
    
    if use_pdf:
        # Try to parse PDF resume
        try:
            resume_folder = resume_settings.get("resume_folder", "./resume")
            filename = resume_settings.get("default_resume_filename", "resume.pdf")
            resume_path = os.path.join(resume_folder, filename)
            
            # Check if file exists
            if not os.path.exists(resume_path):
                logger.error(f"Resume file not found: {resume_path}")
                return create_fallback_resume(config)
                
            # Try to parse PDF
            resume_data = parse_pdf_resume(resume_path)
            
            if resume_data:
                logger.info(f"Successfully parsed resume for {resume_data.get('name', 'Unknown')}")
                return resume_data
            else:
                logger.warning("PDF parsing returned no data")
                return create_fallback_resume(config)
                
        except Exception as e:
            logger.exception(f"Error parsing PDF resume: {e}")
            
            # Fallback to JSON data if configured
            if resume_settings.get("fallback_to_json_data", True):
                logger.info("Attempting to fall back to JSON resume data")
                return load_json_resume(config)
            else:
                return create_fallback_resume(config)
    else:
        # Use JSON data directly
        return load_json_resume(config)

def parse_pdf_resume(resume_path):
    """Parse PDF resume file and extract relevant information"""
    try:
        # First try with PyPDF2 if available
        try:
            import PyPDF2
            logger.info("Using PyPDF2 to parse resume")
            
            with open(resume_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                # Basic parsing - in a real implementation this would be more sophisticated
                return {
                    "name": extract_name_from_text(text),
                    "email": extract_email_from_text(text),
                    "phone": extract_phone_from_text(text),
                    "raw_text": text,
                    "parsed_with": "PyPDF2"
                }
        except ImportError:
            logger.warning("PyPDF2 not available")
            
        # Try with pdfplumber if available
        try:
            import pdfplumber
            logger.info("Using pdfplumber to parse resume")
            
            with pdfplumber.open(resume_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
                
                return {
                    "name": extract_name_from_text(text),
                    "email": extract_email_from_text(text),
                    "phone": extract_phone_from_text(text),
                    "raw_text": text,
                    "parsed_with": "pdfplumber"
                }
        except ImportError:
            logger.warning("pdfplumber not available")
        
        logger.error("No PDF parsing library available")
        return None
        
    except Exception as e:
        logger.exception(f"Error in PDF parsing: {e}")
        return None

def load_json_resume(config):
    """Load resume data from JSON file"""
    try:
        resume_settings = config.get("resume_settings", {})
        resume_folder = resume_settings.get("resume_folder", "./resume")
        json_filename = resume_settings.get("resume_json_filename", "resume.json")
        json_path = os.path.join(resume_folder, json_filename)
        
        if not os.path.exists(json_path):
            logger.error(f"JSON resume file not found: {json_path}")
            return create_fallback_resume(config)
            
        with open(json_path, 'r') as file:
            resume_data = json.load(file)
            logger.info(f"Successfully loaded resume data from JSON for {resume_data.get('name', 'Unknown')}")
            return resume_data
            
    except Exception as e:
        logger.exception(f"Error loading JSON resume: {e}")
        return create_fallback_resume(config)

def create_fallback_resume(config):
    """Create fallback resume data from configuration"""
    default_answers = config.get("default_answers", {})
    
    fallback_resume = {
        "name": "Job Applicant",
        "email": default_answers.get("email", "applicant@example.com"),
        "phone": default_answers.get("phone", "Not specified"),
        "current_location": default_answers.get("current_location", "Not specified"),
        "experience": default_answers.get("experience", "3 years"),
        "current_salary": default_answers.get("current_salary", "Not specified"),
        "expected_salary": default_answers.get("expected_salary", "Not specified"),
        "notice_period": default_answers.get("notice_period", "Immediate"),
        "skills": ["Not specified"],
        "education": ["Not specified"],
        "is_fallback": True
    }
    
    logger.info("Created fallback resume data")
    return fallback_resume

def extract_name_from_text(text):
    """Extract name from resume text - simplified version"""
    # This is a placeholder for more sophisticated name extraction
    lines = text.split('\n')
    if lines and lines[0].strip():
        return lines[0].strip()
    return "Unknown"

def extract_email_from_text(text):
    """Extract email from resume text - simplified version"""
    import re
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)
    if matches:
        return matches[0]
    return "Not found"

def extract_phone_from_text(text):
    """Extract phone from resume text - simplified version"""
    import re
    phone_pattern = r'(\+\d{1,3}[-.\s]?)?(\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\d{10}|\d{3}[-.\s]?\d{4}[-.\s]?\d{4})'
    matches = re.findall(phone_pattern, text)
    if matches:
        # Return the first complete match
        for match in matches:
            complete = ''.join(match).strip()
            if complete:
                return complete
    return "Not found"
