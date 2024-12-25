from django.urls import path
from .views import landlord_signup_step1, landlord_signup_step2

urlpatterns = [
    path("landlord/signup/step1/", landlord_signup_step1, name="landlord_signup_step1"),
    path("landlord/signup/step2/<int:user_id>/", landlord_signup_step2, name="landlord_signup_step2"),
]
