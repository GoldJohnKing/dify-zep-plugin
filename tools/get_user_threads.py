from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from zep_cloud.client import Zep
from zep_cloud import NotFoundError


class GetUserThreadsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            api_key = self.runtime.credentials["zep_api_key"]
            api_url = self.runtime.credentials.get("zep_api_url")
            base_url = f"{api_url}/api/v2" if api_url else None
            client = Zep(api_key=api_key, base_url=base_url)

            response = client.user.get_threads(
                user_id=tool_parameters["user_id"],
            )

            # client.user.get_threads returns typing.List[Thread], which needs to be parsed into dict
            dict_threads = [t.__dict__ for t in threads]

            yield self.create_text_message(json.dumps(dict_threads))
            yield self.create_json_message(
                {"status": "success", "response": dict_threads}
            )
        except Exception as e:
            err = str(e)
            yield self.create_json_message({"status": "error", "error": err})
