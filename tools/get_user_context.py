from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from zep_cloud.client import Zep
from zep_cloud.errors import NotFoundError


class GetUserContext(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            api_key = self.runtime.credentials["zep_api_key"]
            api_url = self.runtime.credentials.get("zep_api_url")
            base_url = f"{api_url}/api/v2" if api_url else None
            client = Zep(api_key=api_key, base_url=base_url)

            mode = tool_parameters.get("mode")

            min_rating = tool_parameters.get("min_rating")
            if min_rating and not 0 <= min_rating <= 1:
                raise Exception("\"min_rating\" exceeds valid range [0, 1]")

            try:
                response = client.thread.get_user_context(
                    thread_id=tool_parameters["thread_id"],
                    min_rating=min_rating,
                    mode=mode,
                )
            except NotFoundError:
                raise Exception("Thread does not exist")

            yield self.create_text_message(response.context)
            yield self.create_json_message(
                {"status": "success", "response": json.loads(response.json())}
            )

        except Exception as e:
            err = str(e)
            yield self.create_json_message({"status": "error", "error": err})
