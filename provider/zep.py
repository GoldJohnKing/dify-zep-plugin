from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from zep_cloud.client import Zep
from zep_cloud.core.api_error import ApiError


class ZepProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            client = Zep(api_key=credentials["zep_api_key"])
            # Make a lightweight request to verify the API key without assuming
            # any specific sessions exist.
            client.memory.list_sessions(page_size=1)
        except Exception as e:
            if isinstance(e, ApiError) and e.status_code == 401:
                raise ToolProviderCredentialValidationError(str(e)) from e
