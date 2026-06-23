"""Unit tests for ADO client patch helpers."""

from ado_client import AdoClient


def test_replace_field_operations_builds_patch_json() -> None:
    ops = AdoClient._replace_field_operations(
        {"System.Title": "New title", "System.State": "Active"}
    )
    assert ops == [
        {"op": "replace", "path": "/fields/System.Title", "value": "New title"},
        {"op": "replace", "path": "/fields/System.State", "value": "Active"},
    ]


def test_replace_field_operations_adds_markdown_format_for_description() -> None:
    ops = AdoClient._replace_field_operations(
        {"System.Description": "## Goal\n\nHello"}
    )
    assert ops == [
        {"op": "replace", "path": "/fields/System.Description", "value": "## Goal\n\nHello"},
        {
            "op": "add",
            "path": "/multilineFieldsFormat/System.Description",
            "value": "Markdown",
        },
    ]


def test_wit_params_api_version_only() -> None:
    assert AdoClient._wit_params() == {"api-version": "7.1"}


def test_markdown_format_operations() -> None:
    ops = AdoClient._markdown_format_operations(["System.Description", "System.State"])
    assert ops == [
        {
            "op": "add",
            "path": "/multilineFieldsFormat/System.Description",
            "value": "Markdown",
        },
    ]
