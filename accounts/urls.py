from django.urls import path, include
from .views import user_type_selection, landlord_signup_step1, landlord_signup_step2, tenant_signup, update_landlord, update_tenant,profile,update_profile,landlord_panel, list_tenants
from django.contrib.auth.views import LoginView

app_name = "accounts" 

urlpatterns = [
    # URL for profile page
    path("profile/", profile, name="profile"),

    #URL for the panel page
    path("landlord/panel/", landlord_panel, name="landlord_panel"),

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
    path("update-tenant/<int:tenant_id>/", update_tenant, name="update_tenant"),

    #URLs for login 
    path("login/", LoginView.as_view(template_name="registration/login.html"), name="account_login"),  # Aponta para o template correto
    path("", include("allauth.urls")),

    #URLs for tenant list 
    path("tenants/list/", list_tenants, name="list_tenants"),


]