#!/usr/bin/env python3
"""
ClawFlare Prototype — Immediate Test Script
===========================================
Test the core Cloudflare Pages publishing flow right now with your API token.

This is a standalone prototype to validate the approach before building the full skill.
It focuses on the **direct upload API** for a single HTML file (no Wrangler dependency for this test).

Usage examples:
  # 1. List your accounts
  python prototype_clawflare.py --token YOUR_CF_API_TOKEN list-accounts

  # 2. List projects in a specific account
  python prototype_clawflare.py --token YOUR_CF_API_TOKEN --account-id xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx list-projects

  # 3. Publish a simple HTML page (creates deployment in existing project)
  python prototype_clawflare.py --token YOUR_CF_API_TOKEN --account-id xxxxx... \\
      publish-html --project my-test-project \\
      --html '<!DOCTYPE html><html><head><title>ClawFlare Test</title></head><body><h1>Hello from ClawFlare prototype!</h1><p>Published at $(date)</p></body></html>' \\
      --branch main

Requirements: requests (pip install requests)

After successful publish you will get a live URL like:
  https://my-test-project.pages.dev
  or a preview: https://<branch>.my-test-project.pages.dev
"""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import requests

CF_API_BASE = "https://api.cloudflare.com/client/v4"


def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "User-Agent": "ClawFlare-Prototype/0.1"
    }


def list_accounts(token: str):
    """List all Cloudflare accounts the token can access."""
    url = f"{CF_API_BASE}/accounts"
    resp = requests.get(url, headers=get_headers(token))
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        print("Error listing accounts:", data)
        return []
    accounts = data.get("result", [])
    print(f"\nFound {len(accounts)} account(s):")
    for acc in accounts:
        print(f"  • {acc['name']}  (id: {acc['id']})")
    return accounts


def list_projects(token: str, account_id: str):
    """List Pages projects for the given account."""
    url = f"{CF_API_BASE}/accounts/{account_id}/pages/projects"
    resp = requests.get(url, headers=get_headers(token))
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        print("Error listing projects:", data)
        return []
    projects = data.get("result", [])
    print(f"\nFound {len(projects)} Pages project(s) in account {account_id}:")
    for p in projects:
        subdomain = p.get("subdomain", "N/A")
        canonical = p.get("canonical_deployment", {}).get("url", "N/A")
        print(f"  • {p['name']}  ?  {subdomain}.pages.dev   (last: {canonical})")
    return projects


def create_deployment_direct(token: str, account_id: str, project_name: str,
                             html_content: str, branch: str = "main") -> dict:
    """
    Publish a single index.html using the direct upload deployments API.
    This is the simplest reliable path for the prototype (no Wrangler needed).
    """
    # Compute SHA-256 hash of the content (Cloudflare expects this in manifest)
    content_hash = hashlib.sha256(html_content.encode("utf-8")).hexdigest()

    manifest = {
        "/index.html": content_hash
    }

    # Form data: manifest as JSON + the file itself
    files = {
        "manifest": (None, json.dumps(manifest), "application/json"),
        "/index.html": ("index.html", html_content, "text/html")
    }

    url = f"{CF_API_BASE}/accounts/{account_id}/pages/projects/{project_name}/deployments"

    print(f"\n?? Publishing to project '{project_name}' (branch: {branch}) via direct upload...")
    print(f"   Manifest: {manifest}")

    resp = requests.post(url, headers=get_headers(token), files=files)
    
    if resp.status_code >= 400:
        print("? Deployment failed:")
        print(resp.text)
        try:
            err = resp.json()
            print(json.dumps(err, indent=2))
        except Exception:
            pass
        return {"success": False, "error": resp.text}

    result = resp.json()
    if not result.get("success"):
        print("? API reported failure:", result)
        return {"success": False, "error": result}

    deployment = result.get("result", {})
    url_live = deployment.get("url") or deployment.get("production_url") or "N/A"
    deployment_id = deployment.get("id", "N/A")

    print("\n? Deployment successful!")
    print(f"   Deployment ID : {deployment_id}")
    print(f"   Live URL      : {url_live}")
    if branch != "main":
        print(f"   Preview URL   : https://{branch}.{project_name}.pages.dev (usually)")

    return {
        "success": True,
        "deployment_id": deployment_id,
        "url": url_live,
        "project": project_name,
        "branch": branch,
        "raw": deployment
    }


def main():
    parser = argparse.ArgumentParser(description="ClawFlare Prototype - Test Cloudflare Pages publishing immediately")
    parser.add_argument("--token", required=True, help="Cloudflare API Token with Pages:Write permission")
    parser.add_argument("--account-id", help="Cloudflare Account ID (required for most commands)")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # list-accounts
    subparsers.add_parser("list-accounts", help="List all accessible Cloudflare accounts")

    # list-projects
    subparsers.add_parser("list-projects", help="List Pages projects in the account")

    # publish-html
    publish_parser = subparsers.add_parser("publish-html", help="Publish a single HTML string as index.html")
    publish_parser.add_argument("--project", required=True, help="Target Pages project name")
    publish_parser.add_argument("--html", required=True, help="HTML content to publish (string)")
    publish_parser.add_argument("--branch", default="main", help="Branch name (default: main)")

    args = parser.parse_args()

    token = args.token.strip()
    account_id = args.account_id.strip() if args.account_id else None

    if args.command == "list-accounts":
        list_accounts(token)

    elif args.command == "list-projects":
        if not account_id:
            print("ERROR: --account-id is required for list-projects")
            sys.exit(1)
        list_projects(token, account_id)

    elif args.command == "publish-html":
        if not account_id:
            print("ERROR: --account-id is required for publish-html")
            sys.exit(1)
        result = create_deployment_direct(
            token=token,
            account_id=account_id,
            project_name=args.project,
            html_content=args.html,
            branch=args.branch
        )
        if result.get("success"):
            print("\n?? Done! You can now visit the URL above.")
            print("   Tip: In the real ClawFlare skill this will be wrapped in a clean tool interface with clarification prompts.")


if __name__ == "__main__":
    main()
