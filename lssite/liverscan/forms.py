from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Diagnosis
from django.core.exceptions import ValidationError
from .utils import upload_triphasic_images, multitemporal_fusion
from datetime import date

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

def create_request_diagnosis(request):
    """  Creates a Diagnosis instance given form data. """
    # required fields for all sources
    patient_initials = request.POST.get('initials').upper()
    birthday = request.POST.get('birthday')
    doctor_assigned = request.user

    ct_scans = request.FILES.getlist('images')

    for ct_scan in ct_scans:
        print(f"Received file: {ct_scan.name}")

    if len(ct_scans) != 3:
        return (False, ['Please upload exactly three CT scan images.'])
    
    current_date = date.today().strftime("%Y-%m-%d")
    
    image_urls = upload_triphasic_images(ct_scans, patient_initials, birthday, current_date)
    
    unenhanced_ct, arterial_ct, portal_venous_ct = image_urls

    try:
        # create the report instance
        diagnosis = Diagnosis(
            unenhanced_ct=unenhanced_ct,
            arterial_ct=arterial_ct,
            portal_venous_ct=portal_venous_ct,
            patient_initials=patient_initials,
            birthday = birthday,
            doctor_assigned=doctor_assigned
        )

        diagnosis.save()

        # Call Cloud Function to process images
        multitemporal_fusion(image_urls, patient_initials, birthday, diagnosis.diagnosis_date)

    
    except ValidationError as e:
        return (False, ['Validation errors occurred.'])
    return (True, None)

def validate_diagnosis(request):
    """  Creates a Diagnosis instance given form data. """
    # required fields for all sources

    patient_id = request.POST.get('patient_id')
    final_diagnosis = request.POST.get('final_diagnosis')
    remarks = request.POST.get('remarks')

    diagnosis = Diagnosis.objects.filter(patient_id=patient_id)
    
    try:
        diagnosis = Diagnosis.objects.get(patient_id=patient_id)

        if diagnosis.final_diagnosis is None:
            diagnosis.final_diagnosis = final_diagnosis
        if diagnosis.remarks is None:
            diagnosis.remarks = remarks
        diagnosis.status = 3

        diagnosis.save()

        return True, None

    except Diagnosis.DoesNotExist:
        return False, [f"No Diagnosis found for the provided patient ID."]
    except ValidationError as e:
        return False, ['Validation errors occurred.']