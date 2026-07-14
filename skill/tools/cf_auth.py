"""
cf_auth.py — Cloudflare API Token handling for ClawFlare skill.

MVP: Simple validation + storage guidance.
In full OpenClaw integration this would hook into workspace secrets / env.
"""

import os
import requests
from typing import Optional, Dict

CF_API_BASE = "https://api.cloudflare.com/client/v4"


def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "User-Agent": "ClawFlare-Skill/0.1"
    }


def validate_token(token: str) -> Dict:
    """
    Validate the token has at least basic account access and Pages permission.
    Returns dict with success + details or error info.
    """
    if not token or len(token) < 20:
        return {"success": False, "error": "Token looks invalid (too short)"}

    # Try listing accounts as a basic capability check
    try:
        resp = requests.get(f"{CF_API_BASE}/accounts", headers=get_headers(token), timeout=10)
        if resp.status_code == 200 and resp.json().get("success"):
            accounts = resp.json().get("result", [])
            return {
                "success": True,
                "message": f"Token valid. Found {len(accounts)} account(s).",
                "accounts_count": len(accounts)
            }
        else:
            return {
                "success": False,
                "error": f"Token validation failed: {resp.status_code}",
                "details": resp.text[:300]
            }
    except Exception as e:
        return {"success": False, "error": f"Network/validation error: {str(e)}"}


def setup_token(token: Optional[str] = None) -> Dict:
    """
    Interactive or programmatic token setup.
    In real skill this would prompt the agent/user and store securely.
    For now: accepts token or reads from env CLAWFLARE_CF_TOKEN.
    """
    if token:
        result = validate_token(token)
        if result["success"]:
            # In production skill: store in OpenClaw secrets / workspace config
            os.environ["CLAWFLARE_CF_TOKEN"] = token
            return {"success": True, "message": "Token validated and stored for this session."}
        return result

    # Fallback to environment
    env_token = os.environ.get("CLAWFLARE_CF_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN")
    if env_token:
        return validate_token(env_token)

    return {
        "success": False,
        "error": "No token provided. Please pass a Cloudflare API token with Pages:Write permission."
    }