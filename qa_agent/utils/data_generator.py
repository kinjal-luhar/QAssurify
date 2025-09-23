"""
Data Generator utility for QA Agent
Uses Faker to generate realistic test data for various testing scenarios
"""

from faker import Faker
import random
import string
from typing import Dict, List, Any


class TestDataGenerator:
    """
    Generates realistic test data for QA testing
    - Valid data for positive testing
    - Invalid data for negative testing
    - Edge case data for boundary testing
    """
    
    def __init__(self, locale: str = 'en_US'):
        """
        Initialize the data generator
        
        Args:
            locale: Locale for Faker (e.g., 'en_US', 'en_GB', 'es_ES')
        """
        self.fake = Faker(locale)
        self.fake.seed_instance(42)  # For reproducible results
    
    def generate_user_data(self, valid: bool = True) -> Dict[str, str]:
        """
        Generate user registration data
        
        Args:
            valid: If True, generates valid data; if False, generates invalid data
            
        Returns:
            Dictionary with user data fields
        """
        if valid:
            return {
                'first_name': self.fake.first_name(),
                'last_name': self.fake.last_name(),
                'email': self.fake.email(),
                'username': self.fake.user_name(),
                'password': self._generate_strong_password(),
                'phone': self.fake.phone_number(),
                'address': self.fake.address(),
                'city': self.fake.city(),
                'state': self.fake.state(),
                'zip_code': self.fake.zipcode(),
                'country': self.fake.country(),
                'date_of_birth': self.fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%Y-%m-%d')
            }
        else:
            return {
                'first_name': '',  # Empty required field
                'last_name': self.fake.last_name(),
                'email': 'invalid-email',  # Invalid email format
                'username': '',  # Empty required field
                'password': '123',  # Weak password
                'phone': 'invalid-phone',
                'address': self.fake.address(),
                'city': self.fake.city(),
                'state': self.fake.state(),
                'zip_code': 'invalid-zip',
                'country': self.fake.country(),
                'date_of_birth': 'invalid-date'
            }
    
    def generate_login_data(self, valid: bool = True) -> Dict[str, str]:
        """
        Generate login credentials
        
        Args:
            valid: If True, generates valid credentials; if False, generates invalid
            
        Returns:
            Dictionary with login data
        """
        if valid:
            return {
                'username': self.fake.user_name(),
                'email': self.fake.email(),
                'password': self._generate_strong_password()
            }
        else:
            return {
                'username': 'nonexistent_user',
                'email': 'invalid@email',
                'password': 'wrong_password'
            }
    
    def generate_form_data(self, field_type: str, valid: bool = True) -> Dict[str, str]:
        """
        Generate form data based on field type
        
        Args:
            field_type: Type of form (contact, feedback, survey, etc.)
            valid: If True, generates valid data; if False, generates invalid
            
        Returns:
            Dictionary with form data
        """
        if field_type == 'contact':
            if valid:
                return {
                    'name': self.fake.name(),
                    'email': self.fake.email(),
                    'subject': self.fake.sentence(nb_words=3),
                    'message': self.fake.text(max_nb_chars=200),
                    'phone': self.fake.phone_number()
                }
            else:
                return {
                    'name': '',  # Empty required field
                    'email': 'invalid-email',
                    'subject': '',  # Empty required field
                    'message': '',  # Empty required field
                    'phone': 'invalid-phone'
                }
        
        elif field_type == 'feedback':
            if valid:
                return {
                    'rating': str(random.randint(1, 5)),
                    'comment': self.fake.text(max_nb_chars=500),
                    'category': random.choice(['Bug Report', 'Feature Request', 'General Feedback'])
                }
            else:
                return {
                    'rating': 'invalid-rating',
                    'comment': '',  # Empty required field
                    'category': 'Invalid Category'
                }
        
        return {}
    
    def generate_edge_case_data(self) -> Dict[str, str]:
        """
        Generate edge case data for boundary testing
        
        Returns:
            Dictionary with edge case data
        """
        return {
            'very_long_text': 'A' * 1000,  # Very long text
            'special_chars': '!@#$%^&*()_+-=[]{}|;:,.<>?',
            'unicode_text': '测试文本 🚀 ñáéíóú',
            'sql_injection': "'; DROP TABLE users; --",
            'xss_attempt': '<script>alert("XSS")</script>',
            'very_long_email': f"{'a' * 50}@{'b' * 50}.com",
            'empty_string': '',
            'whitespace_only': '   ',
            'numbers_only': '123456789',
            'symbols_only': '!@#$%^&*()'
        }
    
    def generate_api_test_data(self) -> Dict[str, Any]:
        """
        Generate data for API testing
        
        Returns:
            Dictionary with API test data
        """
        return {
            'valid_json': {
                'name': self.fake.name(),
                'email': self.fake.email(),
                'age': random.randint(18, 80),
                'active': True
            },
            'invalid_json': {
                'name': None,
                'email': 'invalid-email',
                'age': 'not-a-number',
                'active': 'not-boolean'
            },
            'malformed_json': '{"name": "test", "email": "test@example.com", "age": 25,}',  # Trailing comma
            'empty_json': {},
            'large_payload': {
                'data': [self.fake.text() for _ in range(1000)]  # Large array
            }
        }
    
    def _generate_strong_password(self) -> str:
        """
        Generate a strong password for testing
        
        Returns:
            Strong password string
        """
        # Generate password with mixed case, numbers, and special characters
        password = (
            self.fake.password(length=12, special_chars=True, digits=True, 
                             upper_case=True, lower_case=True)
        )
        return password
    
    def generate_boundary_values(self, field_type: str) -> List[str]:
        """
        Generate boundary values for testing
        
        Args:
            field_type: Type of field (email, password, text, number, etc.)
            
        Returns:
            List of boundary values
        """
        if field_type == 'email':
            return [
                'a@b.co',  # Minimum valid email
                'a' * 50 + '@' + 'b' * 50 + '.com',  # Very long email
                'test@example.com',  # Normal email
                'test+tag@example.com',  # Email with plus
                'test.name@example.co.uk'  # Email with dots and subdomain
            ]
        
        elif field_type == 'password':
            return [
                'a',  # Too short
                'a' * 7,  # Just under minimum
                'a' * 8,  # Minimum length
                'a' * 50,  # Very long
                '12345678',  # Numbers only
                'abcdefgh',  # Letters only
                'Abc123!',  # Mixed but short
                'Abc123!@#$%^&*()',  # Very strong
            ]
        
        elif field_type == 'text':
            return [
                '',  # Empty
                'a',  # Single character
                'a' * 255,  # Maximum typical length
                'a' * 1000,  # Very long
                '   ',  # Whitespace only
                'a' * 10 + ' ' + 'b' * 10,  # With spaces
            ]
        
        return []
    
    def generate_sql_injection_payloads(self) -> List[str]:
        """
        Generate SQL injection test payloads
        
        Returns:
            List of SQL injection strings
        """
        return [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' OR 1=1 --",
            "admin'--",
            "admin'/*",
            "' UNION SELECT * FROM users --",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            "' OR 'x'='x",
            "1' OR '1'='1",
            "admin' OR '1'='1' --"
        ]
    
    def generate_xss_payloads(self) -> List[str]:
        """
        Generate XSS test payloads
        
        Returns:
            List of XSS strings
        """
        return [
            '<script>alert("XSS")</script>',
            '<img src="x" onerror="alert(\'XSS\')">',
            '<svg onload="alert(\'XSS\')">',
            'javascript:alert("XSS")',
            '<iframe src="javascript:alert(\'XSS\')">',
            '<body onload="alert(\'XSS\')">',
            '<input onfocus="alert(\'XSS\')" autofocus>',
            '<select onfocus="alert(\'XSS\')" autofocus>',
            '<textarea onfocus="alert(\'XSS\')" autofocus>',
            '<keygen onfocus="alert(\'XSS\')" autofocus>'
        ]


# Global data generator instance
data_generator = TestDataGenerator()
