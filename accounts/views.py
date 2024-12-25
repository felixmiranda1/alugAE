from django.shortcuts import render, redirect
from .forms import EssentialLandlordForm, OptionalLandlordForm
from .models import CustomUser, Landlord

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
def landlord_signup_step2(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return redirect("landlord_signup_step1")  # Redirect back to step 1 if user doesn't exist

    if request.method == "POST":
        form = OptionalLandlordForm(request.POST)
        if form.is_valid():
            form.save(user=user)  # Save optional data linked to the user
            return redirect("account_login")  # Redirect to login page after successful registration
    else:
        form = OptionalLandlordForm()

    return render(request, "accounts/landlord_signup_step2.html", {"form": form})
