from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader 
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .models import Template, Contract
from accounts.models import Landlord, Tenant
from properties.models import Property, Unit  # Model for Unit (from app properties)
from .services.contract_generation import generate_contract
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template import engines

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
        return redirect("rent:preview_contract", unit_id=unit.id, tenant_id=tenant.id, template_id=template.id)

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
def generate_contract_view(request, contract_id):
    """
    Django view to generate a contract based on a template and contract data.

    Args:
        request: Django HTTP request object.
        contract_id: ID of the contract to generate.

    Returns:
        JsonResponse: The generated contract content or an error message.
    """
    try:
        # Fetch the contract and associated template
        contract = get_object_or_404(Contract, id=contract_id)
        landlord = contract.landlord

        # Fetch properties, units, and tenants associated with the Landlord
        properties = Property.objects.filter(landlord_id=landlord.id)
        units = Unit.objects.filter(property__in=properties)
        tenants = Tenant.objects.filter(landlord=landlord)

        # Fetch template and validate context
        template = contract.template
        if not template:
            return JsonResponse({"error": "No template associated with this contract."}, status=400)

        # Build the context for the placeholders
        context = {
            "NOME_DO_LANDLORD": f"{landlord.user.first_name} {landlord.user.last_name}",
            "NOME_DO_TENANT": f"{contract.tenant.user.first_name} {contract.tenant.user.last_name}",
            "VALOR_DO_ALUGUEL": contract.rent_value,
            "DATA_DE_INICIO": contract.start_date.strftime("%d/%m/%Y"),
            "DATA_DE_TERMINO": contract.end_date.strftime("%d/%m/%Y"),
        }

        # Generate the contract content
        contract_content = generate_contract(template.content, context)

        return JsonResponse({"contract": contract_content}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
