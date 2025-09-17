from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from zep_cloud.client import Zep

class GetMessagesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            api_key = self.runtime.credentials["zep_api_key"]
            api_url = self.runtime.credentials.get("zep_api_url")
            base_url = f"{api_url}/api/v2" if api_url else None
            client = Zep(api_key=api_key, base_url=base_url)

            messages = client.thread.get(
                thread_id=tool_parameters["thread_id"],
                limit=tool_parameters.get("limit"),
                cursor=tool_parameters.get("cursor"),
                lastn=tool_parameters.get("lastn"),
            )

            yield self.create_text_message(messages.json())
            yield self.create_json_message(
                {"status": "success", "messages": json.loads(messages.json())}
            )

        except Exception as e:
            err = str(e)
            yield self.create_json_message({"status": "error", "error": err})
