from django.urls import path

from lexnetic_school import views

urlpatterns = [
	path('', views.redirect_docs, name='docs'),
]

