from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from zep_cloud.client import Zep
from zep_cloud import Message, RoleType


class AddSessionMemoryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            api_key = self.runtime.credentials["zep_api_key"]
            api_url = self.runtime.credentials.get("zep_api_url")
            base_url = f"{api_url}/api/v2" if api_url else None
            client = Zep(api_key=api_key, base_url=base_url)

            ignore_roles = tool_parameters.get("ignore_roles") or []
            if isinstance(ignore_roles, str):
                try:
                    ignore_roles = json.loads(ignore_roles)
                except json.JSONDecodeError:
                    ignore_roles = [r.strip() for r in ignore_roles.split(",") if r.strip()]

            response = client.thread.add_messages(
                thread_id=tool_parameters["thread_id"],
                messages=[
                    Message(
                        content=tool_parameters["content"],
                        role=tool_parameters["role"],
                        created_at=tool_parameters.get("created_at") or None,
                        name=tool_parameters.get("name") or None,
                        processed=tool_parameters.get("processed") or None,
                        uuid_=tool_parameters.get("uuid") or None,
                    ),
                ],
                ignore_roles=ignore_roles or None,
                return_context=tool_parameters.get("return_context") or None,
            )

            if response.context :
                yield self.create_text_message(response.context)
            yield self.create_json_message(
                {"status": "success", "response": json.loads(response.json())}
            )

        except Exception as e:
            err = str(e)
            yield self.create_json_message({"status": "error", "error": err})
