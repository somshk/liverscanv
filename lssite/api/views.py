from rest_framework import generics
from .serializers import CustomUserSerializer, DiagnosisSerializer
from liverscan.models import CustomUser, Diagnosis
from google.cloud import storage
from datetime import timedelta
import json
from rest_framework.response import Response
from google.oauth2 import service_account
from liverscan.models import Diagnosis
from lssite.config import env

class DiagnosisList(generics.ListCreateAPIView):
    queryset = Diagnosis.objects.all()
    serializer_class = DiagnosisSerializer

    
def get_gcs_credentials():
    credentials_json = env("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if credentials_json:
        try:
            credentials_info = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(credentials_info)
            return credentials
        except Exception as e:
            print(f"Error loading credentials from JSON: {e}")
            return None
    else:
        print("GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable not set.")
        return None

def get_signed_url(blob_name, bucket_name=env("OUTPUT_BUCKET"), expiration=timedelta(minutes=15)):
    """Generates a signed URL for a Google Cloud Storage blob.

    Args:
        bucket_name (str): The name of the GCS bucket.
        blob_name (str): The name of the GCS blob.
        expiration (timedelta): The expiration time for the signed URL. Defaults to 15 minutes.

    Returns:
        str: The signed URL.
        None: If an error occurs.
    """
    credentials = get_gcs_credentials()
    if credentials:
        try:
            storage_client = storage.Client(credentials=credentials)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            url = blob.generate_signed_url(
                version="v4",
                # This URL is valid for 15 minutes
                expiration=expiration,
                # Allow GET requests using this URL.
                method="GET",
            )
            return url
        except Exception as e:
            print(f"Error generating signed URL: {e}")
            return None
    else:
        return None

class DiagnosisDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Diagnosis.objects.all()
    serializer_class = DiagnosisSerializer

    def retrieve(self, request, *args, **kwargs):
        instance: Diagnosis = self.get_object() #This is needed to get the object.

        instance.proxy_unenhanced_ct = get_signed_url(instance.result_unenhanced_image)
        instance.proxy_arterial_ct = get_signed_url(instance.result_arterial_image)
        instance.proxy_portal_venous_ct = get_signed_url(instance.result_portal_venous_image)

        instance.save()

        serializer = self.get_serializer(instance)

        return Response(serializer.data) #This returns the data.
