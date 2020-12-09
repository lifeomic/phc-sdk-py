"""
Contains services for accessing different parts of the PHC platform.
"""

from phc.services.accounts import Accounts
from phc.services.analytics import Analytics
from phc.services.fhir import Fhir
from phc.services.projects import Projects
from phc.services.files import Files
from phc.services.cohorts import Cohorts
from phc.services.genomics import Genomics
from phc.services.tools import Tools
from phc.services.workflows import Workflows


__all__ = [
    "Accounts",
    "Analytics",
    "Fhir",
    "Projects",
    "Files",
    "Cohorts",
    "Genomics",
    "Tools",
    "Workflows",
]

__pdoc__ = {
    "accounts": False,
    "analytics": False,
    "fhir": False,
    "projects": False,
    "files": False,
    "cohorts": False,
    "genomics": False,
    "tools": False,
    "workflows": False,
}
