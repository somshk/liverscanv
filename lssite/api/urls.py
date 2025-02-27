from django.urls import path
from .views import DiagnosisList, DiagnosisDetail

urlpatterns = [
    path('diagnoses/', DiagnosisList.as_view(), name='diagnoses_list'),
    path('diagnoses/<int:pk>/', DiagnosisDetail.as_view(), name='diagnosis_detail'),
]