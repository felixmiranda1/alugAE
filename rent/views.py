from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader 
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .models import Template, Contract
from accounts.models import Landlord, Tenant
from properties.models import Property, Unit  # Model for Unit (from app properties)
from .services.contract_generation import generate_contract
from .services import validate_contract_data
from django.contrib import messages
from .forms import LandlordForm, TenantForm, PropertyForm, UnitForm
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template import engines
from django.utils.timezone import now
from datetime import timedelta

@login_required
def contract_setup_view(request):
    """
    View for landlords to select a unit, tenant, and template to generate a contract.
    """
    try:
        # Fetch the Landlord associated with the logged-in user
        landlord = Landlord.objects.get(user=request.user)
    except Landlord.DoesNotExist:
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Fetch properties, units, and tenants associated with the Landlord
    properties = Property.objects.filter(landlord_id=landlord.id)
    units = Unit.objects.filter(property__in=properties)
    tenants = Tenant.objects.filter(landlord=landlord)

    # # Serialize landlord, units, and tenants into JSON
    # landlord_json = json.dumps({
    #     "landlord": {
    #         "id": landlord.id,
    #         "user_id": landlord.user.id,
    #         "email": landlord.user.email,
    #         "marital_status": landlord.marital_status,
    #         "profession": landlord.profession,
    #     },
    #     "units": [
    #         {
    #             "id": unit.id,
    #             "property_id": unit.property.id,
    #             "unit_number": unit.unit_number,
    #             "status": unit.status, 
    #             "tenant_id": unit.tenant.id if unit.tenant else None,
    #         } for unit in units
    #     ],
    #     "tenants": [
    #         {
    #             "id": tenant.id,
    #             "user_id": tenant.user.id,
    #             "email": tenant.user.email,
    #             "marital_status": tenant.marital_status,
    #             "profession": tenant.profession,
    #         } for tenant in tenants
    #     ]
    # }, cls=DjangoJSONEncoder)

    if request.method == "POST":
        # Get selected unit, tenant, and template from the form
        unit_id = request.POST.get("unit")
        tenant_id = request.POST.get("tenant")
        template_id = request.POST.get("template")

        # Fetch objects
        unit = units.get(id=unit_id)  # Fetch unit from the filtered units
        tenant = tenants.get(id=tenant_id)  # Fetch tenant from the filtered tenants
        template = get_object_or_404(Template, id=template_id)

        # Redirect to the contract generation view
        return redirect("rent:review_contract_data", unit_id=unit.id, tenant_id=tenant.id, template_id=template.id)

    templates = Template.objects.all()

    context = {
        "units": units,
        "tenants": tenants,
        "templates": templates,
        # "landlord_json": landlord_json,
    }
    return render(request, "rent/contract_setup.html", context)

@login_required
def preview_contract_view(request, unit_id, tenant_id, template_id):
    """
    View to generate and preview the contract as a PDF.
    """
    landlord = get_object_or_404(Landlord, user=request.user)

    # Fetch properties, units, and tenants associated with the Landlord
    properties = Property.objects.filter(landlord_id=landlord.id)
    units = Unit.objects.filter(property__in=properties)
    tenants = Tenant.objects.filter(landlord=landlord)

    # Fetch filtered objects
    unit = units.get(id=unit_id)
    tenant = tenants.get(id=tenant_id)
    template = get_object_or_404(Template, id=template_id)

    # Build the context for the placeholders
    context = {
        "NOME_DO_LANDLORD": f"{landlord.user.first_name} {landlord.user.last_name}",
        "ESTADO_CIVIL_LANDLORD": landlord.marital_status,
        "PROFISSAO_LANDLORD": landlord.profession,
        "CPF_LANDLORD": landlord.user.cpf,
        "ENDERECO_LANDLORD": "Landlord Address Placeholder",
        "NOME_DO_TENANT": f"{tenant.user.first_name} {tenant.user.last_name}",
        "ESTADO_CIVIL_TENANT": tenant.marital_status,
        "PROFISSAO_TENANT": tenant.profession,
        "CPF_TENANT": tenant.user.cpf,
        "ENDERECO_TENANT": "Tenant Address Placeholder",
        "PRAZO_LOCACAO": "12",
        "DATA_INICIO_LOCACAO": "01/01/2025",
        "VALOR_ALUGUEL": "1500,00",
        "DIA_VENCIMENTO": "10",
        "CONDICOES_ESPECIAIS": "No special conditions.",
        "DATA_ASSINATURA": "01/01/2025",
    }

    # Replace placeholders in the content from the database
    contract_content = template.content
    for key, value in context.items():
        placeholder = f"[{key}]"
        contract_content = contract_content.replace(placeholder, str(value))

    # Wrap the content with the layout
    html_content = render_to_string("rent/layout_template.html", {"content": contract_content})

    # Create a response object for the PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=contract.pdf"

    # Convert HTML to PDF using xhtml2pdf
    pisa_status = pisa.CreatePDF(html_content, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    return response


@login_required
def generate_contract_view(request, unit_id, tenant_id, template_id):
    """
    Generates a contract after the Landlord has reviewed and confirmed all data.
    """
    try:
        # Buscar o Landlord associado ao usuário logado
        landlord = Landlord.objects.get(user=request.user)

        # Buscar propriedades, unidades, e tenants associados ao Landlord
        properties = Property.objects.filter(landlord_id=landlord.id)  # Corrigido
        units = Unit.objects.filter(property__in=properties)
        tenants = Tenant.objects.filter(landlord=landlord)

        # Buscar os objetos específicos com base nos IDs
        unit = units.get(id=unit_id)
        tenant = tenants.get(id=tenant_id)
        template = get_object_or_404(Template, id=template_id)

        # Criar o contrato, se necessário
        contract, created = Contract.objects.get_or_create(
            landlord=landlord.user,
            tenant=tenant.user,
            unit=unit,
            template=template,
            defaults={
                "status": "active",
                "rent_value": unit.monthly_rent,
                "start_date": now(),
                "end_date": now() + timedelta(days=365),
                "payment_due_date": 1,
            },
        )

        # Gerar o conteúdo do contrato
        context = {
            "NOME_DO_LANDLORD": f"<b>{landlord.user.first_name} {landlord.user.last_name}</b>",
            "RG_LANDLORD": "<b>00000000</b>",
            "CPF_LANDLORD": f"<b>{landlord.user.cpf}</b>",
            "NOME_DO_TENANT": f"<b>{tenant.user.first_name} {tenant.user.last_name}</b>",
            "RG_TENANT": "<b>00000000</b>",
            "CPF_TENANT": f"<b>{tenant.user.cpf}</b>",
            "ENDERECO_UNIDADE": f"<b>{unit.unit_number}, {unit.property.street}, {unit.property.city}</b>",
            "VALOR_DO_ALUGUEL": f"<b>{contract.rent_value}</b>",
            "DATA_DE_INICIO": f"<b>{contract.start_date.strftime('%d/%m/%Y')}</b>",
            "DATA_DE_TERMINO": f"<b>{contract.end_date.strftime('%d/%m/%Y')}</b>",
            "PRAZO_LOCACAO": "<b>12 meses</b>",
            "DIA_VENCIMENTO": "<b>5</b>",
            }
        contract_content = generate_contract(template.content, context)

        return redirect("rent:preview_contract", unit_id=unit.id, tenant_id=tenant.id, template_id=template.id)
    except Landlord.DoesNotExist:
        return JsonResponse({"error": "Landlord does not exist or is not authorized."}, status=403)
    except Unit.DoesNotExist:
        return JsonResponse({"error": "Unit does not exist or is not associated with the Landlord."}, status=403)
    except Tenant.DoesNotExist:
        return JsonResponse({"error": "Tenant does not exist or is not associated with the Landlord."}, status=403)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def review_contract_data(request, unit_id, tenant_id, template_id):
    """
    Allows the Landlord to review and edit all data before generating the contract.
    """
    try:
        landlord = Landlord.objects.get(user=request.user)
    except Landlord.DoesNotExist:
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Fetch properties, units, and tenants associated with the Landlord
    properties = Property.objects.filter(landlord_id=landlord.id)
    units = Unit.objects.filter(property__in=properties)
    tenants = Tenant.objects.filter(landlord=landlord)

    # Fetch the specific objects based on IDs
    unit = units.get(id=unit_id)
    tenant = tenants.get(id=tenant_id)
    template = get_object_or_404(Template, id=template_id)

    # Initialize forms
    landlord_form = LandlordForm(instance=landlord, user_instance=landlord.user)
    tenant_form = TenantForm(instance=tenant, user_instance=tenant.user)
    property_form = PropertyForm(instance=unit.property)
    unit_form = UnitForm(instance=unit)

    if request.method == "POST":
        if "update_landlord" in request.POST:
            landlord_form = LandlordForm(request.POST, instance=landlord, user_instance=landlord.user)
            if landlord_form.is_valid():
                landlord_form.save()
                messages.success(request, "Landlord information updated successfully!")
        elif "update_tenant" in request.POST:
            tenant_form = TenantForm(request.POST, instance=tenant, user_instance=tenant.user)
            if tenant_form.is_valid():
                tenant_form.save()
                messages.success(request, "Tenant information updated successfully!")
        elif "update_property" in request.POST:
            property_form = PropertyForm(request.POST, instance=unit.property)
            if property_form.is_valid():
                property_form.save()
                messages.success(request, "Property information updated successfully!")
        elif "update_unit" in request.POST:
            unit_form = UnitForm(request.POST, instance=unit)
            if unit_form.is_valid():
                unit_form.save()
                messages.success(request, "Unit information updated successfully!")

    # Validate the data
    from .services import validate_contract_data
    missing_fields = validate_contract_data(landlord, tenant, unit.property, unit)

    context = {
        "landlord": landlord,
        "tenant": tenant,
        "property": unit.property,
        "unit": unit,
        "template": template,
        "missing_fields": missing_fields,
        "landlord_form": landlord_form,
        "tenant_form": tenant_form,
        "property_form": property_form,
        "unit_form": unit_form,
    }

    return render(request, "rent/review_contract_data.html", context)
