from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Property
from .forms import PropertyForm
from .utils import landlord_required

# List all properties for the logged-in landlord
@login_required
@landlord_required
def property_list(request):
    properties = Property.objects.filter(landlord=request.user)
    return render(request, 'properties/property_list.html', {'properties': properties})

# Add a new property
@login_required
@landlord_required
def property_add(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            property_instance = form.save(commit=False)
            property_instance.landlord = request.user
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
