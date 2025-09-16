from collections.abc import Generator
from typing import Any
from datetime import datetime

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from zep_cloud.client import Zep


class SearchUserGraphTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            api_key = self.runtime.credentials["zep_api_key"]

            client = Zep(api_key=api_key)

            graph_edges = client.graph.search(
                user_id=tool_parameters["user_id"],
                query=tool_parameters["query"],
                scope="edges",
            ).edges
            graph_nodes = client.graph.search(
                user_id=tool_parameters["user_id"],
                query=tool_parameters["query"],
                scope="nodes",
            ).nodes

            facts_list = []
            for edge in graph_edges or []:
                created_at = datetime.fromisoformat(edge.created_at.replace("Z", ""))
                if edge.invalid_at:
                    invalid_at_dt = datetime.fromisoformat(edge.invalid_at.replace("Z", ""))
                    invalid_at = invalid_at_dt.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    invalid_at = "present"
                facts_list.append(
                    f"  - {edge.fact} ({created_at.strftime('%Y-%m-%d %H:%M:%S')} - {invalid_at})"
                )
            facts_str = ""
            if len(facts_list):
                facts_str = f"""
# These are the most relevant facts and their valid date ranges
# format: FACT (Date range: from - to)
<FACTS>
{"\n".join(facts_list)}
</FACTS>""".strip()

            entities_list = list(
                map(lambda node: f"  - {node.name}: {node.summary}", graph_nodes or [])
            )
            entities_str = ""
            if len(entities_list):
                entities_str = f"""
# These are the most relevant entities
# ENTITY_NAME: entity summary
<ENTITIES>
{"\n".join(entities_list)}
</ENTITIES>""".strip()

            context_str = ""
            if facts_str or entities_str:
                context_str = f"""
FACTS and ENTITIES represent relevant context to the current conversation.

{facts_str}
{entities_str}
""".strip()

            yield self.create_json_message(
                {"status": "success", "context": context_str}
            )
            yield self.create_text_message(context_str)
        except Exception as e:
            err = str(e)
            yield self.create_json_message({"status": "error", "error": err})
            yield self.create_text_message(f"failed to retrieve memory: {err}")
