from django.urls import path
from .views import user_type_selection, landlord_signup_step1, landlord_signup_step2, tenant_signup, update_landlord, update_tenant,profile,update_profile

app_name = "accounts" 

urlpatterns = [
    # URL for profile page
    path("profile/", profile, name="profile"),

    # URL for user type selection
    path("signup/", user_type_selection, name="user_type_selection"),

    # URLs for Landlord signup flow
    path("landlord/signup/step1/", landlord_signup_step1, name="landlord_signup_step1"),
    path("landlord/signup/step2/<int:user_id>/", landlord_signup_step2, name="landlord_signup_step2"),

    # Placeholder for Tenant signup flow (to be implemented later)
    path("tenant/signup/", tenant_signup, name="tenant_signup"),

    # URLs for LandLord and Tenant update flow 
    path("update-profile/", update_profile, name="update_profile"),
    path("update-landlord/", update_landlord, name="update_landlord"),
    path("update-tenant/", update_tenant, name="update_tenant"),
]
