
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

PROJECT_NAME = getattr(settings, "PROJECT_NAME", "Unset Project in Views")

def Blog1(request):
    return render(request, "Blog1.html", {
        "project_name": PROJECT_NAME
    })


def healthz_view(request):
    return JsonResponse({"status": "ok"})