from django.shortcuts import render, get_object_or_404, redirect
from .models import Property, Unit
from accounts.models import Tenant
from .forms import PropertyForm, UnitForm
from django.contrib.auth.decorators import login_required
from .utils import landlord_required

# List all properties for the logged-in landlord
@login_required
def property_list(request):
    try:
        landlord = request.user.landlord  # Obtém o Landlord associado ao usuário logado
    except AttributeError:
        landlord = None
    if landlord:
        properties = Property.objects.filter(landlord_id=landlord.id)  # Filtramos pelo ID do Landlord
    else:
        properties = Property.objects.none()
    return render(request, 'properties/property_list.html', {'properties': properties})

# Add a new property
@login_required
def property_add(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            property_instance = form.save(commit=False)
            property_instance.landlord = request.user  # Associate with the logged-in landlord
            property_instance.save()
            return redirect('properties:property_list')
    else:
        form = PropertyForm()
    return render(request, 'properties/property_form.html', {'form': form})

@login_required
def property_edit(request, pk):
    try:
        landlord = request.user.landlord  # Obtém o Landlord associado ao usuário logado
    except AttributeError:
        return redirect('properties:property_list')  # Se não for um Landlord, redireciona
    property_instance = get_object_or_404(Property, id=pk, landlord_id=landlord.id)  # Filtra corretamente
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property_instance)
        if form.is_valid():
            form.save()
            return redirect('properties:property_list')  
    else:
        form = PropertyForm(instance=property_instance)

    return render(request, 'properties/property_form.html', {'form': form, 'property': property_instance})

# Delete a property
@login_required
def property_delete(request, pk):
    landlord = request.user.landlord  # Obtém o Landlord autenticado
    property_instance = get_object_or_404(Property, id=pk, landlord_id=landlord.id)  # Garante que o landlord só pode deletar suas propriedades

    if request.method == 'POST':
        property_instance.delete()
        return redirect('properties:property_list')

    return render(request, 'properties/property_confirm_delete.html', {'property': property_instance})

# List property details and its units
@login_required
@landlord_required
def property_detail(request, pk):
    """Display details of a property along with its units."""
    property_instance = get_object_or_404(Property, pk=pk, landlord=request.user)
    units = property_instance.units.all()  # Retrieve all units associated with the property
    return render(request, 'properties/property_detail.html', {
        'property': property_instance,
        'units': units
    })

# List all units for a property
@login_required
@landlord_required
def unit_list(request, property_id):
    property_instance = get_object_or_404(Property, id=property_id)  # Garante que a propriedade existe
    units = Unit.objects.filter(property=property_instance)

    return render(request, 'properties/unit_list.html', {'property': property_instance, 'units': units})

# Add a new unit to a property
@login_required
def unit_add(request, property_id):
    """Adicionar uma nova unidade a uma propriedade específica."""
    landlord = request.user.landlord

    property_instance = get_object_or_404(Property, id=property_id, landlord_id=landlord.id)
    tenants = Tenant.objects.filter(landlord=landlord)

    if request.method == 'POST':
        form = UnitForm(request.POST, landlord=landlord)
        if form.is_valid():
            unit = form.save(commit=False)
            unit.property = property_instance
            unit.save()
            return redirect('properties:unit_list', property_id=property_instance.id)
    else:
        form = UnitForm(landlord=landlord)  # <<< AQUI ESTAVA FALTANDO

    return render(request, 'properties/unit_form.html', {'form': form, 'property': property_instance, 'tenants': tenants})

# Edit an existing unit
@login_required
def unit_edit(request, unit_id):
    """Editar uma unidade específica."""
    landlord = request.user.landlord

    unit = get_object_or_404(Unit, id=unit_id, property__landlord_id=landlord.id)
    tenants = Tenant.objects.filter(landlord=landlord)

    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit, landlord=landlord)
        if form.is_valid():
            form.save()
            return redirect('properties:unit_list', property_id=unit.property.id)
    else:
        form = UnitForm(instance=unit, landlord=landlord)  # ✅ landlord incluído aqui

    return render(request, 'properties/unit_form.html', {
        'form': form,
        'unit': unit,
        'property': unit.property,
        'tenants': tenants
    })
# Delete a unit
@login_required
@landlord_required
def unit_delete(request, unit_id):
    """Delete a unit and return to the property's detail page."""
    unit = get_object_or_404(Unit, pk=unit_id, property_ptr__landlord=request.user)
    property_id = unit.property_ptr.pk
    unit.delete()
    return redirect('property_detail', pk=property_id)
