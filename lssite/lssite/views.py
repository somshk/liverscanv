from django.shortcuts import render, redirect
from liverscan.models import (Diagnosis)
from liverscan.forms import create_request_diagnosis, validate_diagnosis
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth import logout

# Create your views here.
def logout_view(request):
    if request.method == "POST":
        if 'logout' in request.POST:
            logout(request)

            return redirect('home')
        
def doctor_required(user):
    return user.role == 'doctor'

def home_view(request):
    logout_view(request)

    context = {}
    context['curr_page'] = 'home'
    context['diagnosed'] = len(Diagnosis.objects.all())
    return render(request, 'index.html', context=context)

@user_passes_test(doctor_required)
def doctor_results_view(request):
    logout_view(request)

    context = {}
    context['curr_page'] = 'doctor-results'
    context['diagnoses'] = Diagnosis.objects.filter(status__lt = 3)

    if request.method == 'POST':
        validate_diagnosis(request=request)

    return render(request, 'doctor_results.html', context=context)

@user_passes_test(doctor_required)
def patient_history_view(request):
    logout_view(request)

    context = {}
    context['curr_page'] = 'patient-history'
    context['diagnoses'] = Diagnosis.objects.filter(status=3)
    return render(request, 'patient_history.html', context=context)

@user_passes_test(doctor_required)
def upload_view(request):
    logout_view(request)
    
    context = {}
    context['curr_page'] = 'upload'

    if request.method == "POST":
        create_request_diagnosis(request=request)
    
    return render(request, 'upload.html', context=context)