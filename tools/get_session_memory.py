from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from zep_cloud.client import Zep


class GetSessionMemoryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            api_key = self.runtime.credentials["zep_api_key"]
            client = Zep(api_key=api_key)

            lastn = tool_parameters.get("lastn")
            if isinstance(lastn, str) and lastn.isdigit():
                lastn = int(lastn)

            min_rating = tool_parameters.get("min_rating")
            if isinstance(min_rating, str):
                try:
                    min_rating = float(min_rating)
                except ValueError:
                    min_rating = None

            memory = client.memory.get(
                session_id=tool_parameters["session_id"],
                lastn=lastn,
                min_rating=min_rating,
            )

            yield self.create_json_message(
                {"status": "success", "memory": json.loads(memory.json())}
            )
            yield self.create_text_message(memory.context or "")
        except Exception as e:
            err = str(e)
            yield self.create_json_message({"status": "error", "error": err})
            yield self.create_text_message(f"failed to retrieve memory: {err}")
