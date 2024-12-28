from django.shortcuts import render, get_object_or_404, redirect
from .models import Property, Unit
from .forms import PropertyForm, UnitForm
from django.contrib.auth.decorators import login_required
from .utils import landlord_required

# List all properties for the logged-in landlord
@login_required
def property_list(request):
    properties = Property.objects.filter(landlord=request.user)
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
            return redirect('property_list')
    else:
        form = PropertyForm()
    return render(request, 'properties/property_form.html', {'form': form})

# Edit an existing property
@login_required
def property_edit(request, pk):
    property_instance = get_object_or_404(Property, pk=pk, landlord=request.user)
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property_instance)
        if form.is_valid():
            form.save()
            return redirect('property_list')
    else:
        form = PropertyForm(instance=property_instance)
    return render(request, 'properties/property_form.html', {'form': form})

# Delete a property
@login_required
def property_delete(request, pk):
    property_instance = get_object_or_404(Property, pk=pk, landlord=request.user)
    property_instance.delete()
    return redirect('property_list')

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
    property_instance = get_object_or_404(Property, pk=property_id, landlord=request.user)
    units = property_instance.units.all()  # Retrieve all units associated with the property
    return render(request, 'properties/unit_list.html', {'property': property_instance, 'units': units})

# Add a new unit to a property
@login_required
@landlord_required
def unit_add(request, property_id):
    """Adicionar uma nova unidade a uma propriedade específica."""
    property_instance = get_object_or_404(Property, pk=property_id, landlord=request.user)
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save(commit=False)  # Não salva ainda no banco
            unit.property = property_instance  # Relaciona a unidade com a propriedade
            unit.save()  # Salva no banco de dados
            return redirect('unit_list', property_id=property_instance.pk)
    else:
        form = UnitForm()
    return render(request, 'properties/unit_form.html', {'form': form, 'property': property_instance})


# Edit an existing unit
@login_required
@landlord_required
def unit_edit(request, unit_id):
    """Edit a unit and return to the property's detail page."""
    unit = get_object_or_404(Unit, pk=unit_id, property__landlord=request.user)  # Acessa o landlord via property
    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            return redirect('property_detail', pk=unit.property.pk)  # Corrige o redirecionamento
    else:
        form = UnitForm(instance=unit)
    return render(request, 'properties/unit_form.html', {'form': form, 'unit': unit})

# Delete a unit
@login_required
@landlord_required
def unit_delete(request, unit_id):
    """Delete a unit and return to the property's detail page."""
    unit = get_object_or_404(Unit, pk=unit_id, property_ptr__landlord=request.user)
    property_id = unit.property_ptr.pk
    unit.delete()
    return redirect('property_detail', pk=property_id)
