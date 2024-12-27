from django.shortcuts import render, redirect, get_object_or_404
from .forms import EssentialLandlordForm, OptionalLandlordForm, TenantSignupForm, LandlordUpdateForm, TenantUpdateForm
from .models import CustomUser, Landlord
from django.contrib.auth.decorators import login_required


def home(request):
    """
    Displays the homepage of the application.
    """
    return render(request, "home.html")

@login_required
def profile(request):
    """
    Displays the profile of the logged-in user.
    """
    return render(request, "accounts/profile.html", {"user": request.user})

# View to select the type of user (landlord or tenant)
def user_type_selection(request):
    if request.method == "POST":
        user_type = request.POST.get("user_type")
        if user_type == "landlord":
            return redirect("landlord_signup_step1")
        elif user_type == "tenant":
            return redirect("tenant_signup") 
    return render(request, "accounts/user_type_selection.html")

# View for the first part of registration (Essential Data)
def landlord_signup_step1(request):
    if request.method == "POST":
        form = EssentialLandlordForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create an empty landlord profile linked to the user
            Landlord.objects.create(user=user)
            # Redirect to the second step of the registration process
            return redirect("landlord_signup_step2", user_id=user.id)
    else:
        form = EssentialLandlordForm()

    return render(request, "accounts/landlord_signup_step1.html", {"form": form})

# View for the second part of registration (Optional Data)
@login_required
def landlord_signup_step2(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    # Ensure the logged-in user matches the user being edited
    if request.user != user:
        return redirect("landlord_signup_step1")  # Redirect to step 1 if unauthorized

    if request.method == "POST":
        form = OptionalLandlordForm(request.POST)
        if form.is_valid():
            form.save(user=user)
            return redirect("account_login")  # Redirect to login page
    else:
        form = OptionalLandlordForm()

    return render(request, "accounts/landlord_signup_step2.html", {"form": form})

# View for tenant SignUp form
def tenant_signup(request):
    if request.method == "POST":
        form = TenantSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("account_login")  # Redirect to login after successful signup
    else:
        form = TenantSignupForm()
    return render(request, "accounts/tenant_signup.html", {"form": form})

# View for profile update (both landlord and tenant)
@login_required
def update_profile(request):
    """
    Redirects the user to the appropriate update form based on their type.
    """
    if hasattr(request.user, 'landlord'):
        return redirect("update_landlord")
    elif hasattr(request.user, 'tenant'):
        return redirect("update_tenant")
    else:
        return redirect("home")

@login_required
def update_landlord(request):
    """
    Allows a logged-in Landlord to update their profile information.
    Ensures only Landlords can access this view.
    """
    # Verify the user is a Landlord
    if not hasattr(request.user, 'landlord'):
        return redirect("home")  # Redirect if the user is not a Landlord

    if request.method == "POST":
        form = LandlordUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save(user=request.user)
            return redirect("profile")  # Redirect to the profile page after update
    else:
        form = LandlordUpdateForm(instance=request.user)
    return render(request, "accounts/update_landlord.html", {"form": form})

@login_required
def update_tenant(request):
    """
    Allows a logged-in Tenant to update their profile information.
    Ensures only Tenants can access this view.
    """
    # Verify the user is a Tenant
    if not hasattr(request.user, 'tenant'):
        return redirect("home")  # Redirect if the user is not a Tenant

    if request.method == "POST":
        form = TenantUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save(user=request.user)
            return redirect("profile")  # Redirect to the profile page after update
    else:
        form = TenantUpdateForm(instance=request.user)
    return render(request, "accounts/update_tenant.html", {"form": form})