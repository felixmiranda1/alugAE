def validate_contract_data(landlord, tenant, property, unit):
    """
    Validates if all necessary fields for generating a contract are filled.
    Returns a list of missing fields if any.
    """
    missing_fields = []

    # Validate Landlord fields
    if not landlord.user.first_name:
        missing_fields.append("Landlord: First Name")
    if not landlord.user.last_name:
        missing_fields.append("Landlord: Last Name")
    if not landlord.user.cpf:
        missing_fields.append("Landlord: CPF")

    # Validate Tenant fields
    if not tenant.user.first_name:
        missing_fields.append("Tenant: First Name")
    if not tenant.user.last_name:
        missing_fields.append("Tenant: Last Name")
    if not tenant.user.cpf:
        missing_fields.append("Tenant: CPF")
    if not tenant.profession:
        missing_fields.append("Tenant: Profession")

    # Validate Property fields
    if not property.street:
        missing_fields.append("Property: Street")
    if not property.city:
        missing_fields.append("Property: City")
    if not property.state:
        missing_fields.append("Property: State")

    # Validate Unit fields
    if not unit.unit_number:
        missing_fields.append("Unit: Unit Number")

    return missing_fields
