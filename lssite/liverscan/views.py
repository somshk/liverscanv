from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.core.exceptions import ValidationError
from datetime import date, datetime
from liverscan.models import Diagnosis
from .forms import SignUpForm
import requests

# Create your views here.
def signup_view(request):
    context = {}

    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
        context['form'] = form
    
    return render(request, 'signup.html', context=context)

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
        initials = request.POST['initials']
        birthday = request.POST['birthday']
        diagnosis_date = request.POST['diagnosis-date']

        try:
            diagnosis = Diagnosis.objects.get(patient_initials=initials,
                                   birthday=birthday,
                                     diagnosis_date=diagnosis_date)
            context['curr_page'] = 'results'
            context['diagnosis'] = diagnosis
            return render(request, 'results.html', context=context)
        except:
            context['error'] = 'Invalid login credentials.'
            return render(request, 'login.html', context=context)
    return render(request, 'login.html', context=context)

def doctor_login_view(request):
    context = {}

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(role_based_redirect(user))
        else:
            context['error'] = 'Invalid login credentials.'
            return render(request, 'doctor_login.html', context=context)
    return render(request, 'doctor_login.html', context=context)