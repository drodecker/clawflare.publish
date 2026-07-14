"""
cf_publish.py — Core publishing logic for ClawFlare skill.

MVP supports:
- Publishing a single HTML string (direct upload)
- Publishing a local directory (prefers Wrangler if available, falls back to simple cases)

This module encapsulates the reliable deployment flow so the agent doesn't have to.
"""

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, Union

import requests

CF_API_BASE = "https://api.cloudflare.com/client/v4"


def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "User-Agent": "ClawFlare-Skill/0.1"
    }


def _compute_file_hash(file_path: Path) -> str:
    """SHA-256 hash of file contents (hex)."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b" "):
            h.update(chunk)
    return h.hexdigest()


def publish_html_string(
    token: str,
    account_id: str,
    project_name: str,
    html_content: str,
    branch: str = "main"
) -> Dict:
    """
    Publish a single index.html using the direct deployments API.
    Reliable for quick HTML publishes without external dependencies.
    """
    content_hash = hashlib.sha256(html_content.encode("utf-8")).hexdigest()
    manifest = {"/index.html": content_hash}

    files = {
        "manifest": (None, json.dumps(manifest), "application/json"),
        "/index.html": ("index.html", html_content, "text/html")
    }

    url = f"{CF_API_BASE}/accounts/{account_id}/pages/projects/{project_name}/deployments"

    resp = requests.post(url, headers=get_headers(token), files=files, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("success"):
        return {"success": False, "error": data, "message": "Direct upload failed"}

    deployment = data.get("result", {})
    return {
        "success": True,
        "deployment_id": deployment.get("id"),
        "url": deployment.get("url") or deployment.get("production_url"),
        "project": project_name,
        "branch": branch,
        "method": "direct-upload",
        "raw": deployment
    }


def publish_directory(
    token: str,
    account_id: str,
    project_name: str,
    source_dir: Union[str, Path],
    branch: str = "main"
) -> Dict:
    """
    Publish a directory of static assets.
    Strategy:
      1. Prefer `wrangler pages deploy` if available (most robust, handles Functions, large sites, etc.)
      2. Fallback to direct upload for very simple cases (single index.html)
    """
    source_dir = Path(source_dir).resolve()
    if not source_dir.exists() or not source_dir.is_dir():
        return {"success": False, "error": f"Source directory not found: {source_dir}"}

    # Try Wrangler first (best experience)
    wrangler_cmd = shutil.which("wrangler") or "npx wrangler"
    try:
        # Quick check if wrangler works
        result = subprocess.run(
            [wrangler_cmd.split()[0], "--version"] if "npx" not in wrangler_cmd else ["npx", "wrangler", "--version"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            print("Using Wrangler for directory publish (recommended path)...")
            cmd = [
                wrangler_cmd.split()[0] if "npx" not in wrangler_cmd else "npx",
                "wrangler", "pages", "deploy", str(source_dir),
                "--project-name", project_name,
                "--branch", branch,
                "--commit-message", "Published via ClawFlare skill"
            ]
            if "npx" in wrangler_cmd:
                cmd = ["npx", "wrangler", "pages", "deploy", str(source_dir), "--project-name", project_name, "--branch", branch]

            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if proc.returncode == 0:
                # Parse URL from output (Wrangler prints it)
                output = proc.stdout + proc.stderr
                # Simple extraction — real skill would be more robust
                url = None
                for line in output.splitlines():
                    if "https://" in line and ".pages.dev" in line:
                        url = line.strip().split()[-1]
                        break
                return {
                    "success": True,
                    "url": url or f"https://{project_name}.pages.dev",
                    "project": project_name,
                    "branch": branch,
                    "method": "wrangler",
                    "output": output[:500]
                }
            else:
                print("Wrangler failed, falling back to direct upload if possible...")
    except Exception as e:
        print(f"Wrangler not available or failed ({e}). Trying direct upload fallback...")

    # Fallback: only support single index.html for now in direct mode
    index_file = source_dir / "index.html"
    if index_file.exists() and len(list(source_dir.iterdir())) == 1:
        with open(index_file, "r", encoding="utf-8") as f:
            html = f.read()
        return publish_html_string(token, account_id, project_name, html, branch)

    return {
        "success": False,
        "error": "Directory publish requires Wrangler for multi-file sites. "
                 "Install wrangler (npm install -g wrangler) or reduce to single index.html."
    }


def publish_content(
    token: str,
    account_id: str,
    project_name: str,
    html_content: Optional[str] = None,
    source_dir: Optional[Union[str, Path]] = None,
    branch: str = "main"
) -> Dict:
    """
    Unified publish entry point used by the agent/skill.
    Chooses the right backend based on what was provided.
    """
    if html_content:
        return publish_html_string(token, account_id, project_name, html_content, branch)
    elif source_dir:
        return publish_directory(token, account_id, project_name, source_dir, branch)
    else:
        return {"success": False, "error": "Must provide either html_content or source_dir"}