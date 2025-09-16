from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from zep_cloud.client import Zep
from zep_cloud import BadRequestError


class AddUserTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            api_key = self.runtime.credentials["zep_api_key"]
            api_url = self.runtime.credentials.get("zep_api_url")
            base_url = f"{api_url}/api/v2" if api_url else None
            client = Zep(api_key=api_key, base_url=base_url)

            fact_rating_instruction = tool_parameters.get("fact_rating_instruction")
            fact_rating_instruction = json.loads(fact_rating_instruction) if fact_rating_instruction else None

            try:
                user = client.user.add(
                    user_id=tool_parameters["user_id"],
                    email=tool_parameters.get("email"),
                    first_name=tool_parameters.get("first_name"),
                    last_name=tool_parameters.get("last_name"),
                    fact_rating_instruction = fact_rating_instruction,
                    metadata=tool_parameters.get("metadata"),
                )
            except BadRequestError:
                # user already exists
                raise Exception("User already exists")

            yield self.create_text_message(user.json())
            yield self.create_json_message(
                {"status": "success", "user": json.loads(user.json())}
            )

        except Exception as e:
            err = str(e)
            yield self.create_json_message({"status": "error", "error": err})
