from django.urls import path
from django.contrib import admin
from django.http import HttpResponse

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("hello", views.hello_world,),
    path("healthz", views.healthz_view,),

]