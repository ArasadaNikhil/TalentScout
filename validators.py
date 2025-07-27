import re
import phonenumbers
from phonenumbers import NumberParseException
import hashlib
import json
import pandas as pd
from datetime import datetime

class EmailValidator:
    """Validates and extracts email addresses"""
    
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    def is_valid_email(self, email):
        """Check if email format is valid"""
        if not email:
            return False
        return bool(re.match(self.email_pattern, email))
    
    def extract_email(self, text):
        """Extract email from text"""
        if not text:
            return None
        
        match = re.search(self.email_pattern, text)
        if match:
            return match.group()
        return None
    
    def normalize_email(self, email):
        """Normalize email address"""
        if not email:
            return None
        return email.lower().strip()

class PhoneValidator:
    """Validates and extracts phone numbers"""
    
    def __init__(self):
        self.phone_pattern = r'[\+]?[1-9]?[0-9]{7,14}'
    
    def is_valid_phone(self, phone_str, region='US'):
        """Check if phone number is valid using phonenumbers library"""
        if not phone_str:
            return False
        
        try:
            # Parse the phone number
            phone_number = phonenumbers.parse(phone_str, region)
            # Check if it's valid
            return phonenumbers.is_valid_number(phone_number)
        except NumberParseException:
            return False
    
    def extract_phone(self, text):
        """Extract phone number from text"""
        if not text:
            return None
        
        # Clean the text for phone extraction
        cleaned_text = text.replace('-', '').replace(' ', '')
        match = re.search(self.phone_pattern, cleaned_text)
        
        if match:
            return match.group()
        return None
    
    def format_phone(self, phone_str, region='US'):
        """Format phone number in a standard format"""
        if not phone_str:
            return None
        
        try:
            phone_number = phonenumbers.parse(phone_str, region)
            if phonenumbers.is_valid_number(phone_number):
                return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        except NumberParseException:
            pass
        
        return phone_str  # Return original if formatting fails

class ExperienceValidator:
    """Validates years of experience"""
    
    def __init__(self):
        self.experience_pattern = r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)'
    
    def extract_experience(self, text):
        """Extract years of experience from text"""
        if not text:
            return None
        
        text_lower = text.lower()
        match = re.search(self.experience_pattern, text_lower)
        
        if match:
            years = float(match.group(1))
            return f"{years} years" if years != 1 else "1 year"
        
        return None
    
    def is_valid_experience(self, years):
        """Check if experience years are reasonable (0-50 years)"""
        try:
            years_float = float(years.replace(' years', '').replace(' year', ''))
            return 0 <= years_float <= 50
        except (ValueError, AttributeError):
            return False

class DataValidator:
    """General data validation utilities"""
    
    @staticmethod
    def hash_data(data):
        """Create a hash of the data for security/privacy"""
        if not data:
            return None
        
        data_str = json.dumps(data, sort_keys=True) if isinstance(data, dict) else str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    @staticmethod
    def sanitize_input(text):
        """Sanitize user input"""
        if not text:
            return ""
        
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>"\';]', '', text)
        return sanitized.strip()
    
    @staticmethod
    def validate_name(name):
        """Validate full name format"""
        if not name:
            return False
        
        # Check if name contains at least 2 words and only contains letters, spaces, hyphens, apostrophes
        name_pattern = r"^[a-zA-Z\s\-'\.]+$"
        words = name.strip().split()
        
        return len(words) >= 1 and bool(re.match(name_pattern, name)) and len(name) <= 100
    
    @staticmethod
    def validate_position(position):
        """Validate job position/title"""
        if not position:
            return False
        
        # Check reasonable length and characters
        position_pattern = r"^[a-zA-Z0-9\s\-/\+\.\(\)]+$"
        return bool(re.match(position_pattern, position)) and 2 <= len(position) <= 100
    
    @staticmethod
    def validate_location(location):
        """Validate location format"""
        if not location:
            return False
        
        # Allow letters, spaces, commas, periods, hyphens
        location_pattern = r"^[a-zA-Z\s,\.\-]+$"
        return bool(re.match(location_pattern, location)) and 2 <= len(location) <= 100

class CandidateDataManager:
    """Manages candidate data storage and retrieval"""
    
    def __init__(self):
        self.email_validator = EmailValidator()
        self.phone_validator = PhoneValidator()
        self.experience_validator = ExperienceValidator()
        self.data_validator = DataValidator()
    
    def validate_candidate_data(self, candidate_info):
        """Validate all candidate information"""
        validation_results = {
            'valid': True,
            'errors': []
        }
        
        # Validate email
        if 'email' in candidate_info:
            if not self.email_validator.is_valid_email(candidate_info['email']):
                validation_results['valid'] = False
                validation_results['errors'].append('Invalid email format')
        
        # Validate phone
        if 'phone' in candidate_info:
            if not self.phone_validator.is_valid_phone(candidate_info['phone']):
                validation_results['valid'] = False
                validation_results['errors'].append('Invalid phone number')
        
        # Validate experience
        if 'experience' in candidate_info:
            if not self.experience_validator.is_valid_experience(candidate_info['experience']):
                validation_results['valid'] = False
                validation_results['errors'].append('Invalid experience format')
        
        # Validate name
        if 'name' in candidate_info:
            if not self.data_validator.validate_name(candidate_info['name']):
                validation_results['valid'] = False
                validation_results['errors'].append('Invalid name format')
        
        return validation_results
    
    def sanitize_candidate_data(self, candidate_info):
        """Sanitize all candidate data"""
        sanitized_data = {}
        
        for key, value in candidate_info.items():
            if isinstance(value, str):
                sanitized_data[key] = self.data_validator.sanitize_input(value)
            else:
                sanitized_data[key] = value
        
        return sanitized_data
    
    def export_to_dataframe(self, candidate_info):
        """Export candidate info to pandas DataFrame"""
        # Add timestamp
        candidate_info['timestamp'] = datetime.now().isoformat()
        
        # Create DataFrame
        df = pd.DataFrame([candidate_info])
        return df
    
    def save_to_csv(self, candidate_info, filename='candidates.csv'):
        """Save candidate data to CSV file"""
        df = self.export_to_dataframe(candidate_info)
        
        try:
            # Try to append to existing file
            existing_df = pd.read_csv(filename)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.to_csv(filename, index=False)
        except FileNotFoundError:
            # Create new file if it doesn't exist
            df.to_csv(filename, index=False)
        
        return filename