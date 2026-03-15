from django.shortcuts import render
from django.views.generic import ListView

from .models import Component

# Create your views here.
def PartListView(request):
    queryset = Component.objects.all()
    context = {
        'object_list': queryset
    }
    return render(request, 'pages/tabled_list.html', context)  

def PartDetailSlugView(request, id):
    return render(request, 'pages/part_detail.html', {'id': id})    



class ComponentListView(ListView):
    model = Component
    template_name = "pages/tabled_list.html"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()

        category = self.request.GET.get("category")
        brand = self.request.GET.get("brand")

        print("CATEGORY PARAM:", category)

        if category:
            qs = qs.filter(**{category: True})

        if brand:
            qs = qs.filter(brand__iexact=brand)

        return qs