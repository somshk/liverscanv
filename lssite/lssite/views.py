from django.shortcuts import render, redirect
from liverscan.models import (Diagnosis)
from liverscan.forms import create_request_diagnosis, validate_diagnosis
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth import logout
from django.http import Http404, JsonResponse
from django.core.exceptions import PermissionDenied

# Create your views here.
def logout_view(request):
    if request.method == "POST" and request.POST.get("action") == 'logout':
        if 'logout' in request.POST:
            logout(request)

            print('WE LOGGED OUT ALREADY FUCKING REDIRECT!')

            context = {}
            context['curr_page'] = 'home'
            context['diagnosed'] = len(Diagnosis.objects.all())
            
            print(context)

            return True # render(request, 'index.html', context=context)
        
def doctor_required(user):
    is_doctor = user.is_authenticated and user.role == 'doctor'

    if not is_doctor:
        raise PermissionDenied
    return is_doctor

def home_view(request):
    if logout_view(request):
        return redirect('home')

    context = {}
    context['curr_page'] = 'home'
    context['diagnosed'] = len(Diagnosis.objects.all())
    return render(request, 'index.html', context=context)

@user_passes_test(doctor_required)
def doctor_results_view(request):
    if logout_view(request):
        return redirect('home')


    print("gagu ano ba mauuna")
    context = {}
    context['curr_page'] = 'doctor-results'
    context['diagnoses'] = Diagnosis.objects.filter(status__lt = 3, doctor_assigned=request.user)

    if request.method == 'POST' and request.POST.get("action") == 'validate_diagnosis':
        validate_diagnosis(request=request)

    return render(request, 'doctor_results.html', context=context)

@user_passes_test(doctor_required)
def patient_history_view(request):
    if logout_view(request):
        return redirect('home')

    context = {}
    context['curr_page'] = 'patient-history'
    context['diagnoses'] = Diagnosis.objects.filter(status=3, doctor_assigned=request.user)
    return render(request, 'patient_history.html', context=context)

@user_passes_test(doctor_required)
def upload_view(request):
    if logout_view(request):
        return redirect('home')
    
    context = {}
    context['curr_page'] = 'upload'

    if request.method == "POST" and request.POST.get("action") == 'create_request_diagnosis':
        success, error_messages = create_request_diagnosis(request=request)

        if not success:
            context['errors'] = error_messages
            return JsonResponse({'success': False, 'errors': error_messages}, status=400)
        
        if success:
            return JsonResponse({'success': True, 'message': 'Diagnosis request created successfully'})

    return render(request, 'upload.html', context=context)