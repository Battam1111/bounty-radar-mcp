"""Bounty Radar MCP server.

Exposes the live Bounty Radar feed (battam1111.github.io/bounty-radar-data/feed.json)
as MCP tools so any MCP client (Claude Desktop, Claude Code, Cursor, Windsurf,
LibreChat, etc.) can search ZK + AI bounties from within the editor.

Free tier: top 200 open bounties refreshed every 30 min.
For real-time alerts + private API + competitor heat-map, upgrade at
https://battam1111.github.io/bounty-radar-data/
"""
from __future__ import annotations

import json
import time
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP


FEED_URL = "https://battam1111.github.io/bounty-radar-data/feed.json"
FREE_FEED_URL = "https://battam1111.github.io/bounty-radar-data/feed-free.json"
LANDING_URL = "https://battam1111.github.io/bounty-radar-data/"
COOKBOOK_URL = "https://battam1111.github.io/midnight-zk-cookbook/"
USER_AGENT = "bounty-radar-mcp/0.1.0"

# In-process cache to avoid hammering the public feed
_cache: dict[str, Any] = {"data": None, "fetched_at": 0.0}
_CACHE_TTL_SEC = 60


def _fetch_feed() -> dict:
    """Fetch and cache the public bounty feed (60s TTL)."""
    now = time.time()
    if _cache["data"] is not None and (now - _cache["fetched_at"]) < _CACHE_TTL_SEC:
        return _cache["data"]
    with httpx.Client(timeout=15.0, headers={"User-Agent": USER_AGENT}) as c:
        r = c.get(FEED_URL)
        r.raise_for_status()
        data = r.json()
    _cache["data"] = data
    _cache["fetched_at"] = now
    return data


mcp = FastMCP("bounty-radar")


@mcp.tool()
def search_bounties(
    query: str | None = None,
    source: str | None = None,
    ecosystem: str | None = None,
    min_reward_usd: int = 0,
    limit: int = 20,
) -> list[dict]:
    """Search the live Bounty Radar feed for open ZK + AI bounties.

    Args:
        query: text to match against bounty title (case-insensitive substring)
        source: filter by source platform (e.g. "algora", "github_labels", "drips_wave", "code4rena", "bountycaster")
        ecosystem: filter by ecosystem (e.g. "midnightntwrk", "AleoHQ", "noir-lang", "AztecProtocol", "stacks-network", "starknet-io", "o1-labs", "risc0")
        min_reward_usd: minimum reward in USD
        limit: max bounties to return (1-50)

    Returns: list of matching bounties with id, title, reward, repo, issue_url, source, scoring.
    """
    feed = _fetch_feed()
    bounties = feed.get("bounties", [])
    out = []
    q_lower = query.lower() if query else None
    for b in bounties:
        if q_lower and q_lower not in (b.get("title") or "").lower():
            continue
        if source and b.get("source") != source:
            continue
        if ecosystem:
            repo = b.get("repo") or ""
            if not repo.startswith(ecosystem + "/") and repo != ecosystem:
                continue
        reward = b.get("reward_usd") or 0
        if reward and reward < min_reward_usd:
            continue
        out.append({
            "id": b.get("id"),
            "title": b.get("title"),
            "reward": b.get("reward"),
            "reward_usd": b.get("reward_usd"),
            "repo": b.get("repo"),
            "issue_url": b.get("issue_url"),
            "source": b.get("source"),
            "first_seen_at": b.get("first_seen_at"),
            "scoring": b.get("scoring"),
            "competition": b.get("competition"),
        })
        if len(out) >= max(1, min(limit, 50)):
            break
    return out


@mcp.tool()
def get_bounty(bounty_id: str) -> dict | None:
    """Get full details of one bounty by its ID.

    Args:
        bounty_id: the bounty id (e.g. "gh-midnightntwrk-contributor-hub-289")

    Returns: full bounty record, or None if not found.
    """
    feed = _fetch_feed()
    for b in feed.get("bounties", []):
        if b.get("id") == bounty_id:
            return b
    return None


@mcp.tool()
def list_ecosystems() -> list[str]:
    """List all ecosystems currently represented in the feed."""
    feed = _fetch_feed()
    return sorted(feed.get("ecosystems", []))


@mcp.tool()
def list_sources() -> list[str]:
    """List all source platforms currently represented in the feed."""
    feed = _fetch_feed()
    return sorted(feed.get("sources", []))


@mcp.tool()
def radar_summary() -> dict:
    """Top-level radar status: total open bounties, sources covered, last refresh time."""
    feed = _fetch_feed()
    return {
        "total_open_bounties": feed.get("total"),
        "sources": feed.get("sources", []),
        "ecosystems": feed.get("ecosystems", []),
        "generated_at": feed.get("generated_at"),
        "feed_url": FEED_URL,
        "landing_url": LANDING_URL,
    }


@mcp.tool()
def upgrade_info() -> dict:
    """Get information on paid Bounty Radar Pro tiers — real-time alerts, private API, competitor heat-map.

    Returns: pricing tiers + checkout URLs.
    """
    return {
        "free_tier": {
            "feed": FREE_FEED_URL,
            "refresh_rate": "30 min",
            "limit": "top 20 bounties",
        },
        "paid_tiers": {
            "hobbyist_19_usd_monthly": "https://polar.sh/checkout/polar_c_BbZbN6eJnZ7rwsUfT1pMsj4lTftwnfMoGdWBo0KozKU",
            "pro_97_usd_monthly": "https://polar.sh/checkout/polar_c_CKKhyOq11BHuG2AulflWkm53YU98pLdrNo22h3OlB4O",
            "team_497_usd_monthly": "https://polar.sh/checkout/polar_c_bT1FpxfzlShI3PcdHxTrHeJf8EVO1AFaWbFc90Z9mfC",
        },
        "playbook_29_usd_oneshot": "https://polar.sh/checkout/polar_c_rtEpLig3NXQmT8aLSh0esDlQEy43HK8wWrjS44VZaIC",
        "audit_99_usd_oneshot": "https://polar.sh/checkout/polar_c_gXO0FivhPZEULEbuWnpznkLPFdL2Koz68AvG93YoWFb",
        "landing_url": LANDING_URL,
        "cookbook_url": COOKBOOK_URL,
    }


def main() -> None:
    """Entry point — runs the stdio MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
