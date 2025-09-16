from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from zep_cloud.client import Zep


class GetSessionTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            api_key = self.runtime.credentials["zep_api_key"]
            client = Zep(api_key=api_key)

            session = client.memory.get_session(session_id=tool_parameters["session_id"])
            yield self.create_json_message(
                {"status": "success", "session": json.loads(session.json())}
            )
        except Exception as e:  # pragma: no cover - simple passthrough
            err = str(e)
            yield self.create_json_message({"status": "error", "error": err})
