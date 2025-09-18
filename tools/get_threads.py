from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from zep_cloud.client import Zep


class GetThreadsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            api_key = self.runtime.credentials["zep_api_key"]
            api_url = self.runtime.credentials.get("zep_api_url")
            base_url = f"{api_url}/api/v2" if api_url else None
            client = Zep(api_key=api_key, base_url=base_url)

            threads = client.thread.list_all(
                page_number=tool_parameters.get("page_number"),
                page_size=tool_parameters.get("page_size"),
                order_by=tool_parameters.get("order_by"),
                asc=tool_parameters.get("asc"),
            )

            yield self.create_text_message(threads.json())
            yield self.create_json_message(
                {"status": "success", "threads": json.loads(threads.json())}
            )
        except Exception as e:
            err = str(e)
            yield self.create_json_message({"status": "error", "error": err})
