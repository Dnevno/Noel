from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from .models import MedicalHistory, Userdata, Qualification, Share
from .forms import LoginForm, RegisterForm, DoctorForm, HealthForm, ShareForm

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard', username=request.user.id)

    else:
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']

                user = authenticate(request, username=email, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('dashboard', username=user.id)
                else:
                    messages.error(request, 'Invalid phone number or password')
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
                        user.is_active = True
                        user.save()

                        userdata = Userdata.objects.create(
                            user=user,
                            displayed_name=form.cleaned_data['username'],
                            phone=form.cleaned_data['phone'],
                        )
                    
                    messages.success(request, 'Account created successfully.')
                    
                    login(request, user)
                    return redirect('dashboard', username=user.id)
                except Exception as e:
                    messages.error(request, f'An error occurred. Please try again later.  {e}')
    else:
        form = RegisterForm()

    return render(request, 'register.html', { 'form': form })

@login_required
def register_doctor(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            qualification = form.cleaned_data['qualification']
            institution = form.cleaned_data['institution']
            year = form.cleaned_data['graduation_year']

            qualification = Qualification(
                user=Userdata.objects.get(uid=request.user.id),
                qualification=qualification,
                institution=institution,
                year=year
            )
            qualification.save()
            messages.success(request, 'We have received your qualification. Please wait for approval within 24 hours.')
        else:
            messages.error(request, 'Qualification denied')
    
    else:
        form = DoctorForm()

    return render(request, 'application.html', {'form': form})

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

@login_required
def dashboard(request, username):
    #check if user is authenticated
    context = {}
    login_user = Userdata.objects.get(user=request.user)
    is_doctor = login_user.is_doctor
    
    if str(login_user.user.id) == str(username):
        context['self_control'] = True
        if is_doctor:
            context['doctor'] = True
            context['patients'] = Share.objects.filter(shared_with=login_user.user.id)

        if request.method == 'POST':
            share_form = ShareForm(request.POST)
            if share_form.is_valid():
                phone = share_form.cleaned_data['phone']
                password = share_form.cleaned_data['password']

                try:
                    target_user = Userdata.objects.get(phone=phone)
                    if not target_user.is_doctor:
                        messages.error(request, "User is not a doctor")
                    elif request.user.check_password(password):
                        share = Share(
                            patient=login_user,
                            shared_with=target_user.user.id,
                        )
                        share.save()
                        messages.success(request, "Shared successfully")
                    else:
                        messages.error(request, "Invalid password")
                except Userdata.DoesNotExist:
                    messages.error(request, "User not found")

        else:
            share_form = ShareForm()

        context['share_form'] = share_form

    elif is_doctor:
        shared_patient = Share.objects.filter(shared_with=login_user.user.id).exists()
        if shared_patient:
            context['doctor'] = True

            if request.method == 'POST':
                health_form = HealthForm(request.POST)
                if health_form.is_valid():
                    medical_history = MedicalHistory(
                        patient=Userdata.objects.get(uid=username),  # Patient's data
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
                health_form = HealthForm()

            context['health_form'] = health_form
        else:
            return render(request, 'not_allow.html')

    else:
        return render(request, 'not_allow.html')

    context['userdata'] = Userdata.objects.get(user=User.objects.get(id=username))
    context['records'] = MedicalHistory.objects.filter(patient=Userdata.objects.get(user=User.objects.get(id=username)))
    return render(request, 'dashboard.html', context)

def testing(request):
    context = {}
    context['test'] = request.user.id
    return render(request, 'testing.html', context)

    