# ado-mcp

MCP server for Azure DevOps work items (read, search, create, update, comments).

Requires [uv](https://docs.astral.sh/uv/) (includes `uvx`).

## Credentials

Create a [PAT](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate) with **Work Items (Read & write)** scope.

| Variable | Required | Example |
|----------|----------|---------|
| `ADO_TOKEN` | yes | your PAT |
| `ADO_ORG` | yes | `MyOrg` |
| `ADO_HOST` | no | `https://dev.azure.com` (default) |

## Cursor MCP config

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "ado-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/harnyk/ado-mcp", "ado-mcp"],
      "env": {
        "ADO_TOKEN": "<your-pat>",
        "ADO_HOST": "https://dev.azure.com/",
        "ADO_ORG": "MyOrg"
      }
    }
  }
}
```

Reload MCP in Cursor after saving the config.

## Tools

| Tool | Purpose |
|------|---------|
| `list_projects` | List ADO projects |
| `get_work_item` | Get work item by ID |
| `search_tasks` / `search_work_items` | Search by project, type, state, assignee |
| `query_work_items` | Run WIQL query |
| `create_work_item` | Create Task, Bug, User Story, etc. (optional `parent_id`; Description as Markdown) |
| `update_work_item` | Patch title, description (Markdown), assignee, area/iteration, tags, state |
| `update_work_item_state` | Change state only |
| `complete_work_item` | Close/resolve + optional comment |
| `add_work_item_comment` / `list_work_item_comments` | Discussion thread |

Description and other rich-text fields are stored as Markdown via a `/multilineFieldsFormat/<field>` patch op (ADO defaults to HTML without it).
