from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from zep_cloud.client import Zep
from zep_cloud.core.api_error import ApiError


class ZepProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        api_key = credentials.get("zep_api_key")
        if not api_key:
            raise ToolProviderCredentialValidationError("Missing 'zep_api_key'")

        try:
            client = Zep(api_key=api_key)
            # Make a lightweight request to verify the API key without assuming
            # any specific sessions exist.
            client.memory.list_sessions(page_size=1)
        except ApiError as e:
            if e.status_code == 401:
                raise ToolProviderCredentialValidationError(str(e)) from e
            raise
