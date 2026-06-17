"""Azure DevOps REST API client for work item operations."""

from __future__ import annotations

import os
import re
from typing import Any

import httpx

API_VERSION = "7.1"

DEFAULT_FIELDS = [
    "System.Id",
    "System.Title",
    "System.WorkItemType",
    "System.State",
    "System.AssignedTo",
    "System.Description",
    "System.Tags",
    "System.AreaPath",
    "System.IterationPath",
    "System.CreatedDate",
    "System.ChangedDate",
    "Microsoft.VSTS.Scheduling.RemainingWork",
    "Microsoft.VSTS.Scheduling.OriginalEstimate",
]


def _escape_wiql(value: str) -> str:
    return value.replace("'", "''")


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def _normalize_field_value(value: Any) -> Any:
    if isinstance(value, dict) and "displayName" in value:
        return value["displayName"]
    if isinstance(value, str) and "<" in value and ">" in value:
        return _strip_html(value)
    return value


def format_work_item(item: dict[str, Any]) -> dict[str, Any]:
    fields = item.get("fields", {})
    normalized = {
        key.rsplit(".", maxsplit=1)[-1]: _normalize_field_value(value)
        for key, value in fields.items()
    }
    return {
        "id": item.get("id"),
        "url": item.get("url"),
        "fields": normalized,
    }


class AdoClient:
    def __init__(self) -> None:
        token = os.environ.get("ADO_TOKEN")
        org = os.environ.get("ADO_ORG")
        if not token:
            raise RuntimeError("ADO_TOKEN is not set in environment")
        if not org:
            raise RuntimeError("ADO_ORG is not set in environment")

        self.org = org
        self.host = os.environ.get("ADO_HOST", "https://dev.azure.com").rstrip("/")
        self.auth = httpx.BasicAuth("", token)

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.host}/{self.org}/{path.lstrip('/')}"
        with httpx.Client(auth=self.auth, timeout=60.0) as client:
            response = client.request(method, url, **kwargs)
        if not response.is_success:
            raise RuntimeError(f"ADO API {response.status_code}: {response.text}")
        return response.json()

    def list_projects(self, top: int = 100) -> list[dict[str, Any]]:
        data = self._request(
            "GET",
            "_apis/projects",
            params={"api-version": API_VERSION, "$top": top},
        )
        return [
            {"id": project["id"], "name": project["name"], "state": project["state"]}
            for project in data.get("value", [])
        ]

    def query_wiql(self, query: str, top: int = 50) -> list[int]:
        data = self._request(
            "POST",
            "_apis/wit/wiql",
            params={"api-version": API_VERSION, "$top": top},
            json={"query": query},
        )
        return [item["id"] for item in data.get("workItems", [])]

    def get_work_items(
        self,
        ids: list[int],
        fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if not ids:
            return []

        selected_fields = fields or DEFAULT_FIELDS
        items: list[dict[str, Any]] = []

        for offset in range(0, len(ids), 200):
            chunk = ids[offset : offset + 200]
            data = self._request(
                "POST",
                "_apis/wit/workitemsbatch",
                params={"api-version": API_VERSION},
                json={"ids": chunk, "fields": selected_fields},
            )
            items.extend(data.get("value", []))

        return [format_work_item(item) for item in items]

    def get_work_item(self, work_item_id: int) -> dict[str, Any]:
        data = self._request(
            "GET",
            f"_apis/wit/workitems/{work_item_id}",
            params={"api-version": API_VERSION},
        )
        return format_work_item(data)

    def search_work_items(
        self,
        project: str,
        work_item_type: str | None = "Task",
        state: str | None = None,
        assigned_to: str | None = None,
        top: int = 20,
    ) -> list[dict[str, Any]]:
        conditions = [f"[System.TeamProject] = '{_escape_wiql(project)}'"]
        if work_item_type:
            conditions.append(
                f"[System.WorkItemType] = '{_escape_wiql(work_item_type)}'"
            )
        if state:
            conditions.append(f"[System.State] = '{_escape_wiql(state)}'")
        if assigned_to:
            conditions.append(
                f"[System.AssignedTo] CONTAINS '{_escape_wiql(assigned_to)}'"
            )

        query = (
            "SELECT [System.Id] FROM WorkItems "
            f"WHERE {' AND '.join(conditions)} "
            "ORDER BY [System.ChangedDate] DESC"
        )
        ids = self.query_wiql(query, top=top)
        return self.get_work_items(ids)
