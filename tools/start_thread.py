from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from zep_cloud.client import Zep
from zep_cloud.errors import BadRequestError


class StartThreadTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            api_key = self.runtime.credentials["zep_api_key"]
            api_url = self.runtime.credentials.get("zep_api_url")
            base_url = f"{api_url}/api/v2" if api_url else None
            client = Zep(api_key=api_key, base_url=base_url)

            try:
                thread = client.thread.create(
                    thread_id=tool_parameters["thread_id"],
                    user_id=tool_parameters["user_id"],
                )
            except BadRequestError:
                # thread already exists
                raise Exception("Thread already exists")

            yield self.create_text_message(thread.json())
            yield self.create_json_message(
                {"status": "success", "thread": json.loads(thread.json())}
            )

        except Exception as e:
            err = str(e)
            yield self.create_json_message({"status": "error", "error": err})
