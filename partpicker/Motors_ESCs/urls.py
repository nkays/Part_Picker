from django.urls import path
from django.contrib import admin
from django.http import HttpResponse

from . import views

urlpatterns = [
    path("", views.index, name="index"),
]