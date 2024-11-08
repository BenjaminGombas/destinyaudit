import httpx
import time
from typing import Dict, Any, Optional, List
import asyncio
from .exceptions import BungieAPIException, BungieRateLimitException
from .utils import build_url, handle_bungie_response


class BungieClient:
    """Async client for the Bungie API with a focus on PvP stats."""

    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.base_url = "https://www.bungie.net/Platform"
        self.timeout = timeout
        self.headers = {
            'x-API-Key': api_key,
            'Accept': 'application/json'
        }

        # Initialize HTTP client
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers=self.headers,
            follow_redirects=True
        )

        # Simple rate limiting
        self._last_request_time = 0
        # 100ms between requests
        self._min_time_between_requests = 0.1

    async def close(self):
        """Close the HTTP client session."""
        await self._client.aclose()

    async def _make_request(
            self,
            method: str,
            endpoint: str,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Dict[str, Any]] = None
    ) -> Dict[Any, Any]:
        """Make a request to the Bungie API with rate limiting and error handling."""
        # Basic rate limiting
        time_since_last = time.time() - self._last_request_time
        if time_since_last < self._min_time_between_requests:
            await asyncio.sleep(self._min_time_between_requests - time_since_last)

        url = build_url(self.base_url, endpoint)

        try:
            response = await self._client.request(
                method=method,
                url=url,
                params=params,
                json=data
            )
            self._last_request_time = time.time()

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 30))
                raise BungieRateLimitException(
                    f"Rate limit exceeded. Try again after {retry_after} seconds.",
                    response=response
                )

            # Ensure successful response
            response.raise_for_status()

            return handle_bungie_response(response.json())

        except httpx.HTTPStatusError as e:
            raise BungieAPIException(
                f"HTTP error occurred: {str(e)}",
                error_code=e.response.status_code,
                response=e.response
            )

        except httpx.RequestError as e:
            raise BungieAPIException(f"Request error occurred: {str(e)}")

    # Player search methods
    async def search_destiny_player(
        self,
        display_name: str,
        platform: Optional[str] = None
    ) -> Dict[Any, Any]:
        """
        Search for a Destiny 2 player by their Bungie name.

        Args:
            display_name: Full Bungie name (e.g., "PlayerName#1234")
            platform: Optional platform filter
        """
        membership_type = "-1"  # -1 searches all platforms
        if platform:
            # Map common platform names to Bungie's membership types
            platform_map = {
                "xbox": "1",
                "psn": "2",
                "steam": "3",
                "stadia": "5", # lol
                "epic": "6"
            }
            membership_type = platform_map.get(platform.lower(), "-1")

        endpoint = f"/Destiny2/SearchDestinyPlayer/{membership_type}/{display_name}"
        return await self._make_request('GET', endpoint)

    # Player Profile Methods
    async def get_profile(
            self,
            membership_type: int,
            destiny_membership_id: str,
            components: List[str]
    ) -> Dict[Any, Any]:
        """
        Get profile information for a Destiny 2 player.
        """
        endpoint = f"/Destiny2/{membership_type}/Profile/{destiny_membership_id}/"
        params = {"components": ",".join(components)}
        return await self._make_request('GET', endpoint, params=params)

    # Match History Methods
    async def get_activity_history(
            self,
            membership_type: int,
            destiny_membership_id: str,
            character_id: str,
            mode: Optional[int] = None,
            page: int = 0,
            count: int = 25
    ) -> Dict[Any, Any]:
        """
        Get PvP activity history for a character.
        """
        endpoint = f"/Destiny2/{membership_type}/Account/{destiny_membership_id}/Character/{character_id}/Stats/Activities/"
        params = {
            "page": page,
            "count": count
        }
        if mode is not None:
            params["mode"] = mode

        return await self._make_request('GET', endpoint, params=params)
