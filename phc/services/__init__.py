"""
Contains services for accessing different parts of the PHC platform.
"""

from phc.services.accounts import Accounts
from phc.services.analytics import Analytics
from phc.services.fhir import Fhir
from phc.services.projects import Projects


__all__ = ["Accounts", "Analytics", "Fhir", "Projects"]

__pdoc__ = {
    "accounts": False,
    "analytics": False,
    "fhir": False,
    "projects": False,
}
