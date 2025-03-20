from django.urls import path
from payments import views

urlpatterns = [
    # Upload do tenant via link público (token)
    path('upload/<int:payment_id>/<str:upload_token>/', views.upload_receipt_form_public, name='upload_receipt_form_public'),

    # Upload do landlord via painel (login necessário)
    path('upload/', views.upload_receipt_form_landlord, name='upload_receipt_landlord'),
]