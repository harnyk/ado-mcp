"""MCP server exposing Azure DevOps work item read tools."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from ado_client import AdoClient

mcp = FastMCP("ado-mcp")
client = AdoClient()


def _json(data: object) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


@mcp.tool()
def list_projects() -> str:
    """List Azure DevOps projects in the configured organization."""
    return _json(client.list_projects())


@mcp.tool()
def get_work_item(work_item_id: int) -> str:
    """Get a single work item by ID (task, bug, user story, etc.)."""
    return _json(client.get_work_item(work_item_id))


@mcp.tool()
def search_tasks(
    project: str,
    state: str | None = None,
    assigned_to: str | None = None,
    top: int = 20,
) -> str:
    """Search Task work items in a project. Optionally filter by state or assignee."""
    items = client.search_work_items(
        project=project,
        work_item_type="Task",
        state=state,
        assigned_to=assigned_to,
        top=top,
    )
    return _json({"count": len(items), "items": items})


@mcp.tool()
def search_work_items(
    project: str,
    work_item_type: str | None = None,
    state: str | None = None,
    assigned_to: str | None = None,
    top: int = 20,
) -> str:
    """Search work items in a project with optional type/state/assignee filters."""
    items = client.search_work_items(
        project=project,
        work_item_type=work_item_type,
        state=state,
        assigned_to=assigned_to,
        top=top,
    )
    return _json({"count": len(items), "items": items})


@mcp.tool()
def query_work_items(wiql: str, top: int = 50) -> str:
    """Run a WIQL query and return matching work items with details."""
    ids = client.query_wiql(wiql, top=top)
    items = client.get_work_items(ids)
    return _json({"count": len(items), "ids": ids, "items": items})


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
