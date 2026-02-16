from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


# def index(request):
#     return render("Hello, world. Youre at the Motors index")

def index(request):
    return render(request, "Motors_ESCs/home.html")
