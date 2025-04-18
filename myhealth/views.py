from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from datetime import timedelta
from django.utils.timezone import now
from django.core.mail import send_mail
from django.urls import reverse
from .models import MedicalHistory, Userdata, Qualification, Share
from .forms import LoginForm, RegisterForm, PersonalForm, DoctorForm, HealthForm, ShareForm
import hashlib

def hash_phone(phone):
    return hashlib.sha256(phone.encode()).hexdigest()

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard', user_id=request.user.id)

    else:
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']

                try:
                    user_obj = User.objects.get(username=email)
                except User.DoesNotExist:
                    user_obj = None

                if user_obj:
                    if not user_obj.is_active:
                        messages.error(request, 'Account is not activated. Please check your email for the activation link.')
                    else:
                        user = authenticate(request, username=email, password=password)
                        if user:
                            login(request, user)
                            return redirect('dashboard', user_id=user.id)
                        else:
                            messages.error(request, 'Invalid email or password')
                else:
                    messages.error(request, 'Invalid email or password')
        else:
            form = LoginForm()

        return render(request, 'home.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            if User.objects.filter(username=email).exists():
                messages.error(request, 'This email is already taken. Please choose a different one.')
            elif password != confirm_password:
                messages.error(request, 'Passwords do not match.')
            else:
                try:
                    with transaction.atomic():
                        user = User.objects.create_user(
                            username=email, 
                            password=password,
                            email=email,
                        )
                        user.is_active = False
                        user.save()

                        userdata = Userdata(
                            user=user,
                            displayed_name=form.cleaned_data['username'],
                        )
                        userdata.phone = form.cleaned_data['phone']
                        userdata.save()

                    # Send activation email
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    verify_url = request.build_absolute_uri(
                        reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
                    )

                    send_mail(
                        subject="Verify your email",
                        message=f"Click the link to verify your email: {verify_url}",
                        from_email="no-reply@myhealth.com",
                        recipient_list=[email],
                    )                    

                    messages.success(request, 'A verification email has been sent to your email address. Please check your inbox and click the link to verify your account.')
                    return redirect('index')
                except Exception as e:
                    messages.error(request, f'An error occurred. Please try again later.  {e}')
    else:
        form = RegisterForm()

    return render(request, 'register.html', { 'form': form })

def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None:
        if default_token_generator.check_token(user, token):
            if is_token_expired(user, allowed_minutes=60):
                return render(request, 'verify_email.html', {'expired': True, 'email': user.email})
            else:
                user.is_active = True
                user.save()
                return render(request, 'verify_email.html', {'verified': True})
        else:
            return render(request, 'verify_email.html', {'expired': True, 'email': user.email})
    return render(request, 'verify_email.html')

def resend_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(username=email)
            if user.is_active:
                messages.info(request, "Account is already verified.")
                return redirect('')
            
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verify_url = request.build_absolute_uri(
                reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
            )

            send_mail(
                subject='Verify your email',
                message=f'Click this link to verify your email: {verify_url}',
                from_email='no-reply@yourdomain.com',
                recipient_list=[email],
            )
            messages.success(request, "Verification email resent.")
            return redirect('')
        except User.DoesNotExist:
            messages.error(request, "Email not found.")
    return redirect('register')

def is_token_expired(user, allowed_minutes=60):
    timestamp = user.date_joined or user.last_login
    if timestamp is None:
        return True  # no reference time available
    return now() > timestamp + timedelta(minutes=allowed_minutes)

@login_required
def register_doctor(request):
    context = {}
    try:
        context['userdata'] = Userdata.objects.get(user=request.user)
    except Userdata.DoesNotExist:
        messages.error(request, "User not found.")
        return render(request, 'not_allow.html')

    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            qualification = form.cleaned_data['qualification']
            institution = form.cleaned_data['institution']
            year = form.cleaned_data['graduation_year']

            qualification = Qualification(
                user=Userdata.objects.get(user=request.user),
                qualification=qualification,
                institution=institution,
                year=year
            )
            qualification.save()
            messages.success(request, 'We have received your qualification. Please wait for approval within 24 hours.')
            return redirect('dashboard', user_id=request.user.id)
        else:
            messages.error(request, 'Qualification denied')
    
    else:
        form = DoctorForm()

    context['form'] = form
    return render(request, 'application.html', context)

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

@login_required
def dashboard(request, user_id):
    #check if user is authenticated
    context = {}
    try:
        login_user = Userdata.objects.get(user=request.user)
    except Userdata.DoesNotExist:
        messages.error(request, "User not found.")
        return render(request, 'not_allow.html')
    
    try:
        target_user = User.objects.get(id=user_id)
        target_userdata = Userdata.objects.get(user=target_user)
        context['userdata'] = target_userdata
        print(f"User phone in dashboard: {target_userdata.phone}")
        context['records'] = MedicalHistory.objects.filter(patient=target_userdata)
    except User.DoesNotExist:
        messages.error(request, "Userdata not found.")
        return render(request, 'not_allow.html')
    except Userdata.DoesNotExist:
        messages.error(request, "Userdata not found.")
        return render(request, 'not_allow.html')
    
    is_doctor = login_user.is_doctor
    
    if str(request.user.id) == str(user_id):
        context['self_control'] = True
        
        if is_doctor:
            context['doctor'] = True
            context['patients'] = Share.objects.filter(shared_with=request.user.id)

        profile_form = PersonalForm()
        share_form = ShareForm()

        if request.method == 'POST':
            form_type = request.POST.get('form_type')

            if form_type == 'profile_form':
                profile_form = PersonalForm(request.POST)
                if profile_form.is_valid():
                    displayed_name = profile_form.cleaned_data['displayed_name']
                    phone = profile_form.cleaned_data['phone']
                    address = profile_form.cleaned_data['address']
                    date_of_birth = profile_form.cleaned_data['date_of_birth']

                    login_user.displayed_name = displayed_name
                    login_user.phone = phone
                    login_user.address = address
                    login_user.date_of_birth = date_of_birth
                    login_user.save()

                    messages.success(request, "Profile updated successfully")
                else:
                    messages.error(request, profile_form.errors)

            elif form_type == 'share_form':
                share_form = ShareForm(request.POST)
                if share_form.is_valid():
                    phone = share_form.cleaned_data['phone']
                    password = share_form.cleaned_data['password']

                    try:
                        hashed = hash_phone(phone)
                        target_doctor = Userdata.objects.get(phone_hash=hashed)
                        if not target_doctor.is_doctor:
                            messages.error(request, "User is not a doctor")
                        elif request.user.check_password(password):
                            share = Share(
                                patient=login_user,
                                shared_with=target_doctor.user.id,
                            )
                            share.save()
                            messages.success(request, "Shared successfully")
                        else:
                            messages.error(request, "Invalid password")
                    except Userdata.DoesNotExist:
                        messages.error(request, "User not found")

        context['profile_form'] = profile_form
        context['share_form'] = share_form

    elif is_doctor:
        shared_patient = Share.objects.filter(shared_with=request.user.id).exists()
        if shared_patient:
            context['doctor'] = True

            if request.method == 'POST':
                health_form = HealthForm(request.POST)
                if health_form.is_valid():
                    try:
                        patient = Userdata.objects.get(user__id=user_id)
                    except Userdata.DoesNotExist:
                        messages.error(request, "Patient not found.")
                        return redirect('some_safe_page')

                    medical_history = MedicalHistory(
                        patient=patient,  # Patient's data
                        doctor=login_user,  # Logged-in doctor
                        hospital=health_form.cleaned_data['hospital'],
                        weight=health_form.cleaned_data['weight'],
                        height=health_form.cleaned_data['height'],
                        blood_pressure=health_form.cleaned_data['blood_pressure'],
                        blood_sugar=health_form.cleaned_data['blood_sugar'],
                        cholesterol=health_form.cleaned_data['cholesterol'],
                        notes=health_form.cleaned_data['notes'],
                    )

                    medical_history.save()
                    messages.success(request, "Health record added successfully")
                else:
                    messages.error(request, health_form.errors)
            else:
                health_form = HealthForm()

            context['health_form'] = health_form
        else:
            return render(request, 'not_allow.html')

    else:
        return render(request, 'not_allow.html')
    
    context['referer'] = request.META.get('HTTP_REFERER', '')
    return render(request, 'dashboard.html', context)

def testing(request):
    context = {}
    context['test'] = request.user.id
    return render(request, 'testing.html', context)

    