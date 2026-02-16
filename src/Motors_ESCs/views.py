from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse


PROJECT_NAME = getattr(settings, "PROJECT_NAME", "unset views")
# Create your views here.


# def index(request):
#     return render("Hello, world. Youre at the Motors index")

def index(request):
    return render(request, "Motors_ESCs/home.html")

def hello_world(request):
    return render(request, "hello-world.html", {
        "project_name": PROJECT_NAME
    })

def healthz_view(request):
    return HttpResponse("OK")