from django.shortcuts import render, redirect, get_object_or_404
from .forms import EssentialLandlordForm, OptionalLandlordForm, TenantSignupForm
from .models import CustomUser, Landlord
from django.contrib.auth.decorators import login_required

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
