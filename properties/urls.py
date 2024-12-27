from django.urls import path
from . import views

urlpatterns = [
    # List all properties
    path('list/', views.property_list, name='property_list'),
    
    # Add a new property
    path('add/', views.property_add, name='property_add'),
    
    # Edit an existing property
    path('<int:pk>/edit/', views.property_edit, name='property_edit'),
    
    # Delete a property
    path('<int:pk>/delete/', views.property_delete, name='property_delete'),
]
