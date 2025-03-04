from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Diagnosis
from django.core.exceptions import ValidationError
from datetime import date
import os
import requests
from google.cloud import storage
from lssite.config import env
from api.views import get_signed_url

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']


def upload_triphasic_images(buckets, ct_scans, patient_initials, birthday, current_date):
    storage_client = storage.Client()
    image_names = ['unenhanced', 'arterial', 'portal_venous']

    for _bucket in buckets:

        bucket = storage_client.bucket(_bucket)
        
        image_urls = []
        for scan, suffix in zip(ct_scans, image_names):
            scan.seek(0)
            file_name = f'{patient_initials}-{birthday}-{current_date}-{suffix}.png'
            blob = bucket.blob(file_name)
            blob.upload_from_file(scan, content_type='image/png')
            image_urls.append(file_name)

    return image_urls

def get_diagnosis_from_response(signed_url):
    response = requests.get(signed_url)

    if response.status_code == 200:
        json_data = response.json()  # Automatically parses JSON
        if json_data:
            return json_data['predictions'][0]['class']
    else:
        print(f"Failed to fetch JSON: {response.status_code} - {response.text}")


def multitemporal_fusion(diagnosis: Diagnosis, image_urls, patient_initials, birthday, current_date):

    preprocessed_filename = f'{patient_initials}-{birthday}-{current_date}-preprocessed.png'
    result_json = f'{patient_initials}-{birthday}-{current_date}-result.json'
    result_stacked_image = f'{patient_initials}-{birthday}-{current_date}-result.png'
    result_unenhanced_image = f'{patient_initials}-{birthday}-{current_date}-unenhanced-result.png'
    result_arterial_image = f'{patient_initials}-{birthday}-{current_date}-arterial-result.png'
    result_portal_venous_image = f'{patient_initials}-{birthday}-{current_date}-portal-venous-result.png'

    try:
        requests.post(
                env("MTF_FUNCTION_ENDPOINT"),
                json={"input_bucket": env('INPUT_BUCKET'),
                    "output_bucket": env('OUTPUT_BUCKET'),
                    "unenhanced_path": image_urls[0],
                    "arterial_path": image_urls[1],
                    "portal_venous_path": image_urls[2],
                    "preprocessed_filename": preprocessed_filename,
                    "result_json": result_json,
                    "result_stacked_image": result_stacked_image,
                    "result_unenhanced_image": result_unenhanced_image,
                    "result_arterial_image": result_arterial_image,
                    "result_portal_venous_image": result_portal_venous_image,
                    }
            )
        
        
        diagnosis.transformed_ct = preprocessed_filename
        diagnosis.result_json = result_json
        diagnosis.result_stacked_image = result_stacked_image
        diagnosis.result_unenhanced_image = result_unenhanced_image
        diagnosis.result_arterial_image = result_arterial_image
        diagnosis.result_portal_venous_image = result_portal_venous_image
        diagnosis.status = 2
        diagnosis.initial_diagnosis = get_diagnosis_from_response(get_signed_url(result_json))
        diagnosis.save()

    except:
        return (False, ['Validation errors occurred.'])

    
def run_inference():
    pass

def create_request_diagnosis(request):
    """  Creates a Diagnosis instance given form data. """
    # required fields for all sources
    patient_initials = request.POST.get('initials').upper()
    birthday = request.POST.get('birthday')
    doctor_assigned = request.user

    ct_scans = request.FILES.getlist('images')

    if len(ct_scans) != 3:
        return (False, ['Please upload exactly three CT scan images.'])
    
    current_date = date.today().strftime("%Y-%m-%d")
    
    input_buckets = [env('INPUT_BUCKET')]
    image_urls = upload_triphasic_images(input_buckets, ct_scans, patient_initials, birthday, current_date)

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
        multitemporal_fusion(diagnosis, image_urls, patient_initials, birthday, diagnosis.diagnosis_date)

    
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
    