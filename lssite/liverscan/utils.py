import os
import requests
from google.cloud import storage

def upload_triphasic_images(ct_scans, patient_initials, birthday, current_date):
    storage_client = storage.Client()
    bucket = storage_client.bucket('lvscan_input')
    image_names = ['unenhanced', 'arterial', 'portal_venous']
    image_urls = []
    for scan, name in zip(ct_scans, image_names):
        file_name = f'{patient_initials}-{birthday}-{name}-{current_date}.png'
        blob = bucket.blob(file_name)
        blob.upload_from_file(scan)
        image_urls.append(file_name)
        print(image_urls)

    return image_urls

def run_inference(image_urls, patient_initials, birthday, current_date):
    requests.post(
            os.getenv("MTF_FUCNTION_ENDPOINT"),
            json={"input_bucket": 'lvscan_input',
                   "output_bucket": 'lvscan_input',
                   "unenhanced_path": image_urls[0],
                   "arterial_path": image_urls[1],
                   "portal_venous_path": image_urls[2],
                   "preprocessed_filename": f'{patient_initials}-{birthday}-preprocessed-{current_date}.png'}
        )