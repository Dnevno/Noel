import re
from django.core.exceptions import ValidationError

def validate_blood_pressure(value):
    # Define regex to match the blood pressure format "120/80"
    if not re.match(r'^\d{2,3}/\d{2,3}$', value):
        raise ValidationError("Blood pressure must be in the format '120/80'.")