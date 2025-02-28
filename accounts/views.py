from django.shortcuts import render, redirect, get_object_or_404
from .forms import EssentialLandlordForm, OptionalLandlordForm, TenantSignupForm, LandlordUpdateForm, TenantUpdateForm
from .models import CustomUser, Landlord, Tenant, AdoptionCode
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,authenticate
from django.contrib.auth import get_backends

def home(request):
    """
    Displays the homepage of the application.
    """
    return render(request, "home.html")

@login_required
def landlord_panel(request):
    return render(request, "accounts/landlord_panel.html")

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
            return redirect("accounts:landlord_signup_step1")
        elif user_type == "tenant":
            return redirect("accounts:tenant_signup")
    return render(request, "accounts/user_type_selection.html")


# View for the first part of registration (Essential Data)


def landlord_signup_step1(request):
    if request.method == "POST":
        form = EssentialLandlordForm(request.POST)
        if form.is_valid():
            user = form.save()  # Criamos o usuário corretamente

            # Criamos o Landlord associado ao usuário recém-criado
            landlord = Landlord.objects.create(user=user)

            # Obter o backend correto
            backend = get_backends()[0]  # Pega o primeiro backend disponível
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"  # Define o backend explicitamente

            # Loga o usuário automaticamente após o Step 1
            login(request, user, backend=user.backend)

            # Redireciona diretamente para o Step 2
            return redirect("accounts:landlord_signup_step2", user_id=user.id) 

    else:
        form = EssentialLandlordForm()

    return render(request, "accounts/landlord_signup_step1.html", {"form": form})

# View for the second part of registration (Optional Data)
@login_required
def landlord_signup_step2(request, user_id):

    user = get_object_or_404(CustomUser, id=user_id)

    # Ensure the logged-in user matches the user being edited
    if not request.user.is_authenticated or request.user != user:
        return redirect("accounts:landlord_signup_step1")

    if request.method == "POST":
        form = OptionalLandlordForm(request.POST)
        if form.is_valid():
            form.save(user=user)
            return redirect("account_login")  # Redirect to login page
    else:
        form = OptionalLandlordForm()

    return render(request, "accounts/landlord_signup_step2.html", {"form": form})

#View for tenant signup 
def tenant_signup(request):
    if request.method == "POST":
        form = TenantSignupForm(request.POST)
        if form.is_valid():
            form.save()  # O formulário já salva o Tenant com o landlord_id correto
            return redirect("account_login")  
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
        return redirect("accounts:update_landlord")
    elif hasattr(request.user, 'tenant'):
        return redirect("accounts:update_tenant")
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
            return redirect("accounts:profile")  # Redirect to the profile page after update
    else:
        form = LandlordUpdateForm(instance=request.user)
    return render(request, "accounts/update_landlord.html", {"form": form})

@login_required
def update_tenant(request, tenant_id):
    """
    Allows a logged-in Tenant to update their own profile,
    or a Landlord to update their associated Tenants' profiles.
    """
    tenant = get_object_or_404(Tenant, id=tenant_id)

    # Ensure that the logged-in user is either the Tenant or the Landlord who owns the property
    if request.user != tenant.user and not hasattr(request.user, 'landlord'):
        return redirect("home")  # Redirect if unauthorized

    if hasattr(request.user, 'landlord') and tenant.landlord != request.user.landlord:
        return redirect("home")  # Ensure Landlord only edits their own Tenants

    if request.method == "POST":
        form = TenantUpdateForm(request.POST, instance=tenant.user)
        if form.is_valid():
            form.save(user=tenant.user)
            return redirect("profile")  # Redirect to the profile page after update
    else:
        form = TenantUpdateForm(instance=tenant.user)
    
    return render(request, "accounts/update_tenant.html", {"form": form})

@login_required
def list_tenants(request):
    # Obtém todos os tenants associados ao Landlord logado
    tenants = Tenant.objects.filter(landlord=request.user.landlord)
    
    return render(request, "accounts/list_tenants.html", {"tenants": tenants})
