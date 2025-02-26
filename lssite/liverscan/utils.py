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

def multitemporal_fusion(image_urls, patient_initials, birthday, current_date):
    requests.post(
            "https://multi-temporal-fusion-346213469712.asia-east1.run.app",
            json={"input_bucket": 'lvscan_input',
                   "output_bucket": 'lvscan_output',
                   "unenhanced_path": image_urls[0],
                   "arterial_path": image_urls[1],
                   "portal_venous_path": image_urls[2],
                   "output_filename": f'{patient_initials}-{birthday}-preprocessed-{current_date}.png'}
        )