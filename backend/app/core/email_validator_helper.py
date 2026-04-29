"""Email validator helper module.

Provides basic email validation functionality for the application.
"""

from typing import Optional


def validate_email(email: Optional[str]) -> bool:
    """Validate that the email input is a non-empty string.

    Args:
        email: The email string to validate. Can be None.

    Returns:
        bool: True if email is a non-empty string, False otherwise.

    Examples:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("")
        False
        >>> validate_email(None)
        False
    """
    if email is None:
        return False
    
    if not isinstance(email, str):
        return False
    
    return len(email.strip()) > 0
