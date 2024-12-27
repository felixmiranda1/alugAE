from django import forms
from .models import Property

# Form for creating and updating properties
class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'name',
            'street',
            'number',
            'complement',
            'city',
            'state',
            'zip_code',
            'is_standalone',
        ]
