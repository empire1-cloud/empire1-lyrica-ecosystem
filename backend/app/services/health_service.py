"""Health service module for system health checks."""

from typing import Dict


def get_health() -> Dict[str, str]:
    """Get the health status of the service.
    
    Returns:
        Dict[str, str]: A dictionary containing health status information with keys:
            - status: The current health status of the service
            - module: The name of this service module
    """
    return {
        "status": "healthy",
        "module": "health_service"
    }
