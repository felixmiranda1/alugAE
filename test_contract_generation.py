from rent.services.contract_generation import generate_contract

# Define the template
template = """
Este contrato é celebrado entre [NOME_DO_LANDLORD] ("Locador") e [NOME_DO_TENANT] ("Locatário").
O aluguel será de [VALOR_DO_ALUGUEL] por mês, com início em [DATA_DE_INICIO] e término em [DATA_DE_TERMINO].
"""

# Define the context
context = {
    "NOME_DO_LANDLORD": "João Silva",
    "NOME_DO_TENANT": "Maria Oliveira",
    "VALOR_DO_ALUGUEL": "R$ 1.500,00",
    "DATA_DE_INICIO": "01/01/2025",
    "DATA_DE_TERMINO": "31/12/2025",
}

# Test the function
try:
    final_contract = generate_contract(template, context)
    print("Generated Contract:\n")
    print(final_contract)
except Exception as e:
    print(f"Error during contract generation: {e}")
