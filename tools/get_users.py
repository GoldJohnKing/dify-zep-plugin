from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from zep_cloud.client import Zep


class GetUsersTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            api_key = self.runtime.credentials["zep_api_key"]
            api_url = self.runtime.credentials.get("zep_api_url")
            base_url = f"{api_url}/api/v2" if api_url else None
            client = Zep(api_key=api_key, base_url=base_url)

            response = client.user.list_ordered(
                page_number=tool_parameters.get("page_number"),
                page_size=tool_parameters.get("page_size"),
            )

            yield self.create_text_message(response.json())
            yield self.create_json_message(
                {"status": "success", "users": json.loads(response.json())}
            )
        except Exception as e:
            err = str(e)
            yield self.create_json_message({"status": "error", "error": err})
