from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from zep_cloud.client import Zep


class GraphSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            api_key = self.runtime.credentials["zep_api_key"]
            api_url = self.runtime.credentials.get("zep_api_url")
            base_url = f"{api_url}/api/v2" if api_url else None
            client = Zep(api_key=api_key, base_url=base_url)

            search_type = tool_parameters.get("search_type")
            user_id_or_graph_id = tool_parameters.get("user_id_or_graph_id")
            user_id = user_id_or_graph_id if search_type == "user" else None
            graph_id = user_id_or_graph_id if search_type == "graph" else None

            bfs_origin_node_uuids = tool_parameters.get("bfs_origin_node_uuids") or []
            if isinstance(bfs_origin_node_uuids, str):
                try:
                    bfs_origin_node_uuids = json.loads(bfs_origin_node_uuids)
                except json.JSONDecodeError:
                    bfs_origin_node_uuids = [r.strip() for r in bfs_origin_node_uuids.split(",") if r.strip()]

            response = client.graph.search(
                query=tool_parameters["query"],
                user_id=user_id,
                graph_id=graph_id,
                reranker=tool_parameters.get("reranker"),
                mmr_lambda = tool_parameters.get("mmr_lambda"),
                center_node_uuid = tool_parameters.get("center_node_uuid"),
                bfs_origin_node_uuids = bfs_origin_node_uuids or None,
                min_fact_rating = tool_parameters.get("min_fact_rating"),
                limit = tool_parameters.get("limit"),
                scope = tool_parameters.get("scope"),
            )

            yield self.create_text_message(response.json())
            yield self.create_json_message(
                {"status": "success", "response": json.loads(response.json())}
            )

        except Exception as e:
            err = str(e)
            yield self.create_json_message({"status": "error", "error": err})
