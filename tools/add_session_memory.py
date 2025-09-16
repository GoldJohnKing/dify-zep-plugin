from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from zep_cloud.client import Zep
from zep_cloud import Message


class AddSessionMemoryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            api_key = self.runtime.credentials["zep_api_key"]
            client = Zep(api_key=api_key)

            return_context = tool_parameters.get("return_context")
            if isinstance(return_context, str):
                return_context = return_context.lower() == "true"

            ignore_roles = tool_parameters.get("ignore_roles") or []
            if isinstance(ignore_roles, str):
                try:
                    ignore_roles = json.loads(ignore_roles)
                except json.JSONDecodeError:
                    ignore_roles = [r.strip() for r in ignore_roles.split(",") if r.strip()]

            memory_resp = client.memory.add(
                session_id=tool_parameters["session_id"],
                messages=[
                    Message(
                        content=tool_parameters["message"],
                        role_type=tool_parameters["role_type"],
                    ),
                ],
                return_context=return_context,
                ignore_roles=ignore_roles if ignore_roles else None,
            )

            payload: dict[str, Any] = {"status": "success"}
            if memory_resp and getattr(memory_resp, "context", None):
                payload["context"] = memory_resp.context

            yield self.create_json_message(payload)
            if payload.get("context"):
                yield self.create_text_message(payload["context"])
        except Exception as e:
            err = str(e)
            yield self.create_json_message({"status": "error", "error": err})
