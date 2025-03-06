from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.core.exceptions import ValidationError
from datetime import date, datetime
from django.contrib.auth import get_backends
from liverscan.models import Diagnosis
from .forms import CustomUserCreationForm
from django.contrib import messages
import requests
from liverscan.models import CustomUser
from api.views import get_gcs_credentials, get_signed_url

# Create your views here.
def signup_view(request):
    context = {}

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")

            if username == '' or username == None:
                messages.error(request, "The username cannot be empty.")
            elif CustomUser.objects.filter(username=username).exists():
                messages.error(request, "This username is already taken.")
            elif CustomUser.objects.filter(email=email).exists():
                messages.error(request, "This email is already registered.")
            else:
                user = form.save()

                backend = get_backends()[0]
                user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
                login(request, user)

                return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = CustomUserCreationForm()
        context['form'] = form
    
    return render(request, 'signup.html', context=context)

def doctor_login_view(request):
    context = {}

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username,  password=password)

        if user is not None:
            login(request, user)
            return redirect(role_based_redirect(user))
        else:
            context['error'] = 'Invalid login credentials.'
            return render(request, 'doctor_login.html', context=context)
    return render(request, 'doctor_login.html', context=context)

def role_based_redirect(user):
    if user.role == 'doctor':
        return 'doctor-results'
    if user.role == 'patient':
        return 'results'
    
def results_view(request):
    context = {}
    context['curr_page'] = 'results'
    return render(request, 'results.html', context=context)

def login_view(request):
    context = {}

    if request.method == "POST":
        initials = request.POST['initials'].upper()
        birthday = request.POST['birthday']
        diagnosis_date = request.POST['diagnosis-date']

        try:
            diagnosis = Diagnosis.objects.get(patient_initials=initials,
                                   birthday=birthday,
                                     diagnosis_date=diagnosis_date)
            
            diagnosis.proxy_result_unenhanced_image = get_signed_url(diagnosis.result_unenhanced_image)
            diagnosis.proxy_result_arterial_image = get_signed_url(diagnosis.result_arterial_image)
            diagnosis.proxy_result_portal_venous_image = get_signed_url(diagnosis.result_portal_venous_image)
            diagnosis.save()

            context['curr_page'] = 'results'
            context['diagnosis'] = diagnosis
            return render(request, 'results.html', context=context)
        except:
            context['error'] = 'Invalid login credentials.'
            return render(request, 'login.html', context=context)
    return render(request, 'login.html', context=context)

