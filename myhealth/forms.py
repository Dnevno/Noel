from django import forms
from django.contrib.auth.models import User
from myhealth.utils.validators import validate_blood_pressure

class LoginForm(forms.Form):
    email = forms.CharField(label="", max_length=255, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Email'}))
    password = forms.CharField(label="", widget=forms.PasswordInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Password'}))

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Username'}))
    email = forms.CharField(max_length="255", widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Email'}))
    phone = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Phone number'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Confirm Password'}))
    accept_privacy_policy = forms.BooleanField(label="I agree to the privacy policy", required=True,
                                               widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    class Meta:
        model = User
        fields = ['username', 'email']

class PersonalForm(forms.Form):
    displayed_name = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Displayed Name'}))
    phone = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Phone number'}))
    address = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Address'}))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={
            'class': 'form-control mb-2',
            'type': 'date',
        }))
    
class DoctorForm(forms.Form):
    qualification = forms.CharField(max_length="255", widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Qualification'}))
    institution = forms.CharField(max_length="255", widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Institution'}))
    graduation_year = forms.DateField(widget=forms.DateInput(attrs={
            'class': 'form-control mb-2',
            'type': 'date',
        }))

class ShareForm(forms.Form):
    phone = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Phone number'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Password'}))

class HealthForm(forms.Form):
    hospital = forms.CharField(max_length="255", widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Hospital'}))
    weight = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        min_value=1,
        max_value=300, 
        widget=forms.NumberInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Weight'}))
    height = forms.DecimalField(
        max_digits=5, 
        decimal_places=2,
        min_value=50,
        max_value=250,
        widget=forms.NumberInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Height'}))
    blood_pressure = forms.CharField(
        max_length=255,
        validators=[validate_blood_pressure],
        widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Blood Pressure'}))
    blood_sugar = forms.DecimalField(
        max_digits=5, 
        decimal_places=2,
         min_value=50,
        max_value=500, 
        widget=forms.NumberInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Blood Sugar'}))
    cholesterol = forms.DecimalField(
        max_digits=5, 
        decimal_places=2,
        min_value=0,
        max_value=500,
        widget=forms.NumberInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Cholesterol'}))
    notes = forms.CharField(max_length=255, widget=forms.Textarea(attrs={'class': 'form-control mb-2', 'placeholder': 'Notes'}))