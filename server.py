"""MCP server exposing Azure DevOps work item tools."""

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
def create_work_item(
    project: str,
    work_item_type: str,
    title: str,
    description: str | None = None,
    assigned_to: str | None = None,
    area_path: str | None = None,
    iteration_path: str | None = None,
    tags: str | None = None,
    parent_id: int | None = None,
) -> str:
    """Create a work item in a project (Task, Bug, User Story, etc.).

    Optional parent_id links the new item as a child of an existing work item.
    assigned_to accepts an email or display name recognized by Azure DevOps.
    """
    return _json(
        client.create_work_item(
            project=project,
            work_item_type=work_item_type,
            title=title,
            description=description,
            assigned_to=assigned_to,
            area_path=area_path,
            iteration_path=iteration_path,
            tags=tags,
            parent_id=parent_id,
        )
    )


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


@mcp.tool()
def update_work_item_state(work_item_id: int, state: str) -> str:
    """Update the state of a work item (e.g. Active, Closed, Resolved)."""
    return _json(client.update_work_item_state(work_item_id, state))


@mcp.tool()
def complete_work_item(
    work_item_id: int,
    comment: str | None = None,
    state: str = "Closed",
) -> str:
    """Mark a work item as done by setting its state (default: Closed). Optionally add a comment."""
    result: dict[str, object] = {
        "workItem": client.update_work_item_state(work_item_id, state),
    }
    if comment:
        result["comment"] = client.add_work_item_comment(work_item_id, comment)
    return _json(result)


@mcp.tool()
def add_work_item_comment(work_item_id: int, text: str) -> str:
    """Add a discussion comment to a work item. Project is resolved from the work item."""
    return _json(client.add_work_item_comment(work_item_id, text))


@mcp.tool()
def list_work_item_comments(work_item_id: int, top: int = 50) -> str:
    """List discussion comments on a work item. Project is resolved from the work item."""
    comments = client.list_work_item_comments(work_item_id, top=top)
    return _json({"count": len(comments), "comments": comments})


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
