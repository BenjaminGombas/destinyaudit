from typing import Dict, Any, Optional
from urllib.parse import urljoin
from .exceptions import BungieAPIException


def build_url(base_url: str, path: str) -> str:
    """Properly join base URL with path."""
    return urljoin(base_url.rstrip('/') + '/', path.lstrip('/'))


def handle_bungie_response(response_data: Dict[Any, Any]) -> Dict[Any, Any]:
    """Process Bungie API response and handle common error cases."""
    if not response_data.get('Response') and response_data.get('ErrorCode') != 1:
        error_status = response_data.get('ErrorStatus', 'Unknown Error')
        error_code = response_data.get('ErrorCode', 0)
        message = response_data.get('Message', 'No error message provided')

        raise BungieAPIException(
            f"{error_status}: {message}",
            error_code=error_code,
            response=response_data
        )

    return response_data.get('Response', response_data)
