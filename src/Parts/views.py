from django.shortcuts import render

from .models import Component

# Create your views here.
def PartListView(request):
    queryset = Component.objects.all()
    context = {
        'object_list': queryset
    }
    return render(request, 'pages/part_list.html', context)  

def PartDetailSlugView(request, id):
    return render(request, 'pages/part_detail.html', {'id': id})    



