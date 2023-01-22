"""LexneticSchool URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from ninja import NinjaAPI
from ninja.security import django_auth

from lexnetic_school.api import router as base_router
from lexnetic_school.apis.school import router as school_router
from lexnetic_school.apis.class_ import router as class_router
from lexnetic_school.apis.student import router as student_router
from lexnetic_school.apis.teacher import router as teacher_router
from lexnetic_school.apis.headmaster import router as headmaster_router

api = NinjaAPI(title="Lexnetic School API", version="1.0.0", csrf=True)
api.add_router("v1", school_router)
api.add_router("v1", class_router)
api.add_router("v1", student_router)
api.add_router("v1", teacher_router)
api.add_router("v1", headmaster_router)
api.add_router("v1", base_router)

urlpatterns = [
	path("api/", api.urls),
	path("admin/", admin.site.urls),
	path("", include("lexnetic_school.urls")),
]
