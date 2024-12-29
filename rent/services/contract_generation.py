import logging

# Set up logging for auditing purposes
logger = logging.getLogger(__name__)

class ContractGenerationError(Exception):
    """Custom exception for errors during contract generation."""
    pass

def validate_context(template_content, context):
    """
    Validate that all placeholders in the template are present in the context.

    Args:
        template_content (str): The template content with placeholders.
        context (dict): The context with data for the placeholders.

    Raises:
        ContractGenerationError: If a required placeholder is missing.
    """
    placeholders = [word.strip('[]') for word in template_content.split() if word.startswith('[') and word.endswith(']')]
    missing_keys = [key for key in placeholders if key not in context]

    if missing_keys:
        raise ContractGenerationError(f"Missing placeholders in context: {', '.join(missing_keys)}")


def replace_placeholders(template_content, context):
    """
    Replace placeholders in the template with values from the context.

    Args:
        template_content (str): The template with placeholders.
        context (dict): A dictionary with data to replace the placeholders.

    Returns:
        str: The template with placeholders replaced by actual values.
    """
    for key, value in context.items():
        placeholder = f"[{key}]"
        template_content = template_content.replace(placeholder, str(value))
    return template_content


def generate_contract(template_content, context):
    """
    Generate a contract by replacing placeholders in the template.

    Args:
        template_content (str): The template with placeholders.
        context (dict): A dictionary with the data to replace the placeholders.

    Returns:
        str: The final contract content.

    Raises:
        ContractGenerationError: If validation fails.
    """
    # Validate the context
    validate_context(template_content, context)

    # Replace placeholders
    try:
        contract_content = replace_placeholders(template_content, context)
    except Exception as e:
        logger.error(f"Error generating contract: {str(e)}")
        raise ContractGenerationError("An error occurred while generating the contract.")

    # Log successful generation
    logger.info("Contract generated successfully.")
    return contract_content
