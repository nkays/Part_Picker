from django.shortcuts import render

# Create your views here.
def PartListView(request):
    return render(request, 'Parts/part_list.html')  

def PartDetailSlugView(request, id):
    return render(request, 'Parts/part_detail.html', {'id': id})    
