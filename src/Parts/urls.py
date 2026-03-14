from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.PartListView, name='entry-list'),
    path('<int:id>/', views.PartDetailSlugView, name='entry-detail'), 
]
