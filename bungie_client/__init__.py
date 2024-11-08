"""
Bungie API client for Destiny 2 PvP stats tracking.
"""

from .client import BungieClient
from .exceptions import (
    BungieAPIException,
    BungieRateLimitException,
    BungieMaintenanceException
)

__version__ = "0.1.0"
__all__ = [
    "BungieClient",
    "BungieAPIException",
    "BungieRateLimitException",
    "BungieMaintenanceException"
]