"""
Azure AI Foundry integration module for FusionAiAutoCoder.
Provides interfaces to connect with Azure AI services.
"""

from typing import Dict, Any, Optional
import os
import logging
import json
import aiohttp
from datetime import datetime, timezone  # type: ignore
from datetime import timedelta

from src.mocks.azure_ai_foundry import FoundryClient as MockFoundryClient

logger: logging.Logger = logging.getLogger("fusion_ai")


class AzureAIFoundry:
    def __init__(self) -> None:
        # Get configuration from environment
        self.tenant_id: Optional[str] = os.environ.get("AZURE_TENANT_ID")
        self.client_id: Optional[str] = os.environ.get("AZURE_CLIENT_ID")
        self.client_secret: Optional[str] = os.environ.get("AZURE_CLIENT_SECRET")
        self.foundry_endpoint: str = os.environ.get(
            "AZURE_FOUNDRY_ENDPOINT", "https://api.foundry.azure.com"
        )

        # Configuration flags
        self.use_mock: bool = (
            os.environ.get("USE_MOCK_FOUNDRY", "true").lower() == "true"
        )
        self.cache_enabled: bool = (
            os.environ.get("ENABLE_CACHE", "true").lower() == "true"
        )
        self.is_configured: bool = all(
            [self.tenant_id, self.client_id, self.client_secret]
        )

        if not self.is_configured and not self.use_mock:
            logger.warning("Azure AI Foundry integration not fully configured")
            logger.info("Falling back to mock implementation")
            self.use_mock = True

        # Initialize components
        self.auth_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.mock_client: Optional[MockFoundryClient] = None
        self.request_cache: Dict[str, Any] = {}

    async def dispatch_task(
        self, task_type: str, task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Dispatch tasks to Azure AI Foundry or local agents based on requirements."""
        if task_type in ["code_generation", "code_optimization"]:
            if task_data.get("complexity", "medium") == "high":
                return await self.process_cloud_task(task_type, task_data)
            else:
                return self.process_local_task(task_type, task_data)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")

    async def process_cloud_task(
        self, task_type: str, task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process tasks using Azure AI Foundry."""
        # Implementation for cloud task processing
        return {"status": "not_implemented"}

    def process_local_task(
        self, task_type: str, task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process tasks using local agents."""
        # Implementation for local task processing
        return {"status": "not_implemented"}

    async def process_code_generation(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate code using Azure AI Foundry."""
        if self.use_mock:
            return self._get_mock_client().generate_code(
                prompt=prompt,
                language=options.get("language", "python") if options else "python",
            )

        try:
            await self._ensure_auth_token()
            endpoint: str = f"{self.foundry_endpoint}/v1/code/generate"
            payload: Dict[str, Any] = {"prompt": prompt, "options": options or {}}

            # Check cache if enabled
            cache_key: str = f"{endpoint}:{json.dumps(payload)}"
            if self.cache_enabled:
                if cache_key in self.request_cache:
                    return self.request_cache[cache_key]

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint, headers=self._get_headers(), json=payload
                ) as response:
                    if response.status == 200:
                        result: Dict[str, Any] = await response.json()

                        # Cache successful response
                        if self.cache_enabled:
                            self.request_cache[cache_key] = result

                        return result
                    else:
                        error_text: str = await response.text()
                        logger.error(
                            f"API call failed: {response.status} - {error_text}"
                        )
                        return {"error": f"API call failed: {error_text}"}

        except Exception as e:
            logger.error(f"Error in code generation: {str(e)}")
            return {"error": str(e)}

    async def process_code_optimization(
        self, code: str, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimize code using Azure AI Foundry."""
        if self.use_mock:
            return self._get_mock_client().optimize_code(
                code=code,
                target=(
                    options.get("target", "performance") if options else "performance"
                ),
                language=options.get("language", "python") if options else "python",
            )

        try:
            await self._ensure_auth_token()
            endpoint: str = f"{self.foundry_endpoint}/v1/code/optimize"
            payload: Dict[str, Any] = {"code": code, "options": options or {}}

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint, headers=self._get_headers(), json=payload
                ) as response:
                    if response.status == 200:
                        result: Dict[str, Any] = await response.json()

                        # Cache successful response
                        if self.cache_enabled:
                            cache_key: str = f"{endpoint}:{json.dumps(payload)}"
                            self.request_cache[cache_key] = result

                        return result
                    else:
                        error_text: str = await response.text()
                        logger.error(
                            f"API call failed: {response.status} - {error_text}"
                        )
                        return {"error": f"API call failed: {error_text}"}

        except Exception as e:
            logger.error(f"Error in code optimization: {str(e)}")
            return {"error": str(e)}

    def _get_mock_client(self) -> MockFoundryClient:
        """Get or create mock client instance."""
        if not self.mock_client:
            self.mock_client = MockFoundryClient()
        return self.mock_client

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
        }

    async def _ensure_auth_token(self) -> None:
        """Ensure we have a valid authentication token."""
        if not self.auth_token or self._is_token_expired():
            await self._refresh_auth_token()

    def _is_token_expired(self) -> bool:
        """Check if the current auth token is expired."""
        if not self.token_expiry:
            return True
        return datetime.now(timezone.utc) >= self.token_expiry

    async def _refresh_auth_token(self) -> None:
        """Refresh the authentication token."""
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "resource": "https://api.foundry.azure.com",
                    },
                )
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    expires_in = data.get("expires_in", 3600)
                    self.token_expiry = datetime.now(timezone.utc) + timedelta(
                        seconds=expires_in
                    )
                else:
                    raise Exception(f"Token refresh failed: {response.status}")
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            raise
