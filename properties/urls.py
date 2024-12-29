from django.urls import path
from . import views

app_name = "properties" 

urlpatterns = [
    # Properties
    path('list/', views.property_list, name='property_list'),
    path('<int:pk>/', views.property_detail, name='property_detail'),  # Página da propriedade com unidades
    path('add/', views.property_add, name='property_add'),
    path('<int:pk>/edit/', views.property_edit, name='property_edit'),
    path('<int:pk>/delete/', views.property_delete, name='property_delete'),

    # Units
    path('<int:property_id>/units/add/', views.unit_add, name='unit_add'),
    path('units/<int:unit_id>/edit/', views.unit_edit, name='unit_edit'),
    path('units/<int:unit_id>/delete/', views.unit_delete, name='unit_delete'),
    path('<int:property_id>/units/', views.unit_list, name='unit_list'),
]
