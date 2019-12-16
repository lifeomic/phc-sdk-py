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


__all__ = [
    "Accounts",
    "Analytics",
    "Fhir",
    "Projects",
    "Files",
    "Cohorts",
    "Genomics",
]

__pdoc__ = {
    "accounts": False,
    "analytics": False,
    "fhir": False,
    "projects": False,
    "files": False,
    "cohorts": False,
    "genomics": False,
}
