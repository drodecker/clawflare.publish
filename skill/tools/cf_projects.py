"""
cf_projects.py — List, get, and create Cloudflare Pages projects.
"""

import requests
from typing import List, Dict, Optional

CF_API_BASE = "https://api.cloudflare.com/client/v4"


def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "User-Agent": "ClawFlare-Skill/0.1"
    }


def list_projects(token: str, account_id: str) -> List[Dict]:
    """List all Pages projects for the account. Returns list of project dicts."""
    url = f"{CF_API_BASE}/accounts/{account_id}/pages/projects"
    resp = requests.get(url, headers=get_headers(token))
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"Failed to list projects: {data}")
    return data.get("result", [])


def get_project(token: str, account_id: str, project_name: str) -> Optional[Dict]:
    """Get details for a specific project."""
    url = f"{CF_API_BASE}/accounts/{account_id}/pages/projects/{project_name}"
    resp = requests.get(url, headers=get_headers(token))
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    data = resp.json()
    return data.get("result") if data.get("success") else None


def create_project(
    token: str,
    account_id: str,
    name: str,
    production_branch: str = "main",
    description: Optional[str] = None
) -> Dict:
    """
    Create a new Pages project.
    Note: Some accounts may have restrictions; this uses the standard API.
    """
    url = f"{CF_API_BASE}/accounts/{account_id}/pages/projects"
    payload = {
        "name": name,
        "production_branch": production_branch
    }
    if description:
        payload["description"] = description

    resp = requests.post(url, headers=get_headers(token), json=payload)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"Project creation failed: {data}")
    return data.get("result", {})