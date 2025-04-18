import re
from django.core.exceptions import ValidationError

def validate_email_format(value):
    if '@' not in value or not value.lower().endswith('.com'):
        raise ValidationError("Enter a valid email address (must contain '@' and end with '.com').")
    
def validate_phone_number(value):
    if not re.fullmatch(r'0\d{9,10}', value):
        raise ValidationError("Enter a valid Malaysian phone number (starts with 0 and 10–11 digits).")

def validate_blood_pressure(value):
    # Define regex to match the blood pressure format "120/80"
    if not re.match(r'^\d{2,3}/\d{2,3}$', value):
        raise ValidationError("Blood pressure must be in the format '120/80'.")