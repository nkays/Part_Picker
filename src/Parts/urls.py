from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.ComponentListView.as_view(), name='entry-list'),
    path('<int:id>/', views.PartDetailSlugView, name='entry-detail'), 
]
