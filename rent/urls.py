from django.urls import path
from rent.views import generate_contract_view,contract_setup_view, preview_contract_view

app_name = "rent" 

urlpatterns = [
    path('generate/<int:contract_id>/', generate_contract_view, name='generate_contract'),
    path("setup/", contract_setup_view, name="contract_setup"),
    path("preview/<int:unit_id>/<int:tenant_id>/<int:template_id>/", preview_contract_view, name="preview_contract"),
]
