"""
URL configuration for lssite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import (home_view, doctor_results_view, patient_history_view, upload_view)
from liverscan.views import (login_view, signup_view, doctor_login_view, results_view)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', home_view, name='home'),
    path('results/', results_view, name='results'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('doctor/results', doctor_results_view, name='doctor-results'),
    path('doctor/history', patient_history_view, name='patient-history'),
    path('doctor/upload', upload_view, name='upload'),
    path('doctor/login', doctor_login_view, name='doctor_login'),
    path('accounts/', include('allauth.urls')),
]
