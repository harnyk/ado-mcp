"""Minimal Azure DevOps API connectivity check using environment variables."""

import os
import sys

import httpx

API_VERSION = "7.1"


def main() -> None:
    token = os.environ.get("ADO_TOKEN")
    if not token:
        print("ADO_TOKEN is not set in environment", file=sys.stderr)
        sys.exit(1)

    org = os.environ.get("ADO_ORG")
    host = os.environ.get("ADO_HOST", "https://dev.azure.com").rstrip("/")

    auth = httpx.BasicAuth("", token)

    if org:
        url = f"{host}/{org}/_apis/projects"
        params = {"api-version": API_VERSION, "$top": 1}
        label = f"projects in org '{org}'"
    else:
        url = "https://app.vssps.visualstudio.com/_apis/profile/profiles/me"
        params = {"api-version": API_VERSION}
        label = "authenticated profile"

    print(f"GET {url}")

    with httpx.Client(auth=auth, timeout=30.0) as client:
        response = client.get(url, params=params)

    print(f"Status: {response.status_code}")

    if response.is_success:
        data = response.json()
        if org:
            count = data.get("count", 0)
            print(f"OK — token works, found {count} project(s) (showing up to 1).")
        else:
            display_name = data.get("displayName", "unknown")
            email = data.get("emailAddress", "n/a")
            print(f"OK — token works. User: {display_name} <{email}>")
            print("Tip: set ADO_ORG in environment to test org-scoped API calls.")
    else:
        print(response.text, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
