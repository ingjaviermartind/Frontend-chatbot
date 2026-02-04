import asyncio
import httpx
from Config import Configuration

class SessionExpired(Exception):
    pass

class ApiClient:

    MAX_RETRIES = 3

    def __init__(self, context):
        self.context = context
        self.base_url = f"http://{Configuration.getServer()}:{Configuration.getPort()}/api"
        self.client = httpx.AsyncClient(timeout=10)

    def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        token = self.context.user_data.get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
        
    async def _refresh_token(self):
        refresh = self.context.user_data.get("refresh")
        if not refresh:
            return False
        
        response = await self.client.post(
            f"{self.base_url}/token/refresh/",
            json={"refresh": refresh},
        )
                        
        if response.status_code != 200:
            return False
        
        data = response.json()
        self.context.user_data["token"] = data["access"]
        return True

    async def _handle_401(self, method, endpoint, **kwargs):
        refreshed = await self._refresh_token()
        if not refreshed:
            await self._force_logout()
            raise SessionExpired()
        response = await self.client.request(
            method,
            f"{self.base_url}{endpoint}",
            headers=self._get_headers(),
            **kwargs
        )
        if response.status_code == 401:
            await self._force_logout()
            raise SessionExpired()
        return response

    async def _force_logout(self):
        self.context.user_data.clear()
        self.context.user_data["authenticated"] = False
        await self.client.aclose()

    async def _request(self, method, endpoint, **kwargs):
        delay = 0.5
        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self.client.request(
                    method,
                    f"{self.base_url}{endpoint}",
                    headers=self._get_headers(),
                    **kwargs
                )
                if response.status_code == 401:
                    return await self._handle_401(method, endpoint, **kwargs)
                if response.status_code in (500,502,503,504):
                    raise httpx.HTTPError("Error en el servidor")
                return response
            
            except (httpx.TimeoutException, httpx.HTTPError):
                if attempt == self.MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(delay)
                delay *= 2

    async def get(self, path, params=None):
        return await self._request("GET", path, params=params)

    async def post(self, path, json=None):
        return await self._request("POST", path, json=json)

    async def put(self, path, json=None):
        return await self._request("PUT", path, json=json)

    async def delete(self, path):
        return await self._request("DELETE", path)

    async def patch(self, path, json=None):
        return await self._request("PATCH", path, json=json)
#
# EOF
#