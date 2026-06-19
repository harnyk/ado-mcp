# ado-mcp

MCP server for Azure DevOps work items (read, search, create, update, comments).

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11+.

```bash
git clone https://github.com/harnyk/ado-mcp.git
cd ado-mcp
uv sync
```

Create a [PAT](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate) with **Work Items (Read & write)** scope.

| Variable | Required | Example |
|----------|----------|---------|
| `ADO_TOKEN` | yes | your PAT |
| `ADO_ORG` | yes | `MyOrg` |
| `ADO_HOST` | no | `https://dev.azure.com` (default) |

Quick check:

```bash
export ADO_TOKEN=... ADO_ORG=CropScience-1
uv run python ado_test.py
```

## Cursor MCP config

Add to `~/.cursor/mcp.json` (adjust `cwd` and token):

```json
{
  "mcpServers": {
    "ado-mcp": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "env": {
        "ADO_TOKEN": "<your-pat>",
        "ADO_HOST": "https://dev.azure.com/",
        "ADO_ORG": "MyOrg"
      },
      "cwd": "/path/to/ado-mcp"
    }
  }
}
```

Reload MCP in Cursor after config or code changes.

## Tools

| Tool | Purpose |
|------|---------|
| `list_projects` | List ADO projects |
| `get_work_item` | Get work item by ID |
| `search_tasks` / `search_work_items` | Search by project, type, state, assignee |
| `query_work_items` | Run WIQL query |
| `create_work_item` | Create Task, Bug, User Story, etc. (optional `parent_id`) |
| `update_work_item_state` | Change state |
| `complete_work_item` | Close/resolve + optional comment |
| `add_work_item_comment` / `list_work_item_comments` | Discussion thread |
