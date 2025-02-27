from rest_framework import serializers
from liverscan.models import CustomUser, Diagnosis

# serializer for Audit Reports
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'role'
        ]

class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = [
            'id', 'patient_id', 'status', 'doctor_assigned', 'patient_initials',
            'birthday', 'diagnosis_date', 'initial_diagnosis', 'confidence', 'area',
            'remarks', 'final_diagnosis', 'unenhanced_ct',

            'proxy_unenhanced_ct', 'proxy_arterial_ct', 'proxy_portal_venous_ct', 'proxy_transformed_ct'
        ]