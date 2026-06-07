from typing import Any, Optional
import httpx
from fastapi import HTTPException

from config import settings


class ServiceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    async def _request(
            self,
            method: str,
            path: str,
            token: Optional[str] = None,
            json: Optional[dict] = None,
            data: Optional[dict] = None,
            files: Optional[list] = None,
            params: Optional[dict] = None
    ) -> Any:
        url = f"{self.base_url}{path}"
        headers = {}

        if token:
            headers["Authorization"] = f"Bearer {token}"

        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json,
                    data=data,
                    files=files,
                    params=params
                )

                if response.status_code >= 400:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json() if response.content else response.text
                    )

                if response.status_code == 204:
                    return None

                return response.json() if response.content else None

            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Service timeout")
            except httpx.RequestError as e:
                raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")