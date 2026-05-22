"""Bounty Radar MCP server v0.2.0.

Exposes the live Bounty Radar feed (battam1111.github.io/bounty-radar-data/feed.json)
as MCP tools so any MCP client (Claude Desktop, Claude Code, Cursor, Windsurf,
LibreChat, etc.) can search ZK + AI bounties from within the editor.

Free tier: top 200 open bounties refreshed every 30 min.
For real-time alerts + private API + competitor heat-map, upgrade at
https://battam1111.github.io/bounty-radar-data/

v0.2.0: + get_bounties_by_ecosystem, + get_bounty_stats, + get_recent_bounties (+3 tools)
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP


FEED_URL = "https://battam1111.github.io/bounty-radar-data/feed.json"
FREE_FEED_URL = "https://battam1111.github.io/bounty-radar-data/feed-free.json"
LANDING_URL = "https://battam1111.github.io/bounty-radar-data/"
COOKBOOK_URL = "https://battam1111.github.io/midnight-zk-cookbook/"
USER_AGENT = "bounty-radar-mcp/0.2.0"

# Per-ecosystem sub-feed base URL (Wave 2 P2.3 adds these on radar-data)
SUBFEED_URL_TEMPLATE = "https://battam1111.github.io/bounty-radar-data/{ecosystem}.json"

# Known ecosystems with per-feed coverage. Used for auto-completion + validation.
KNOWN_ECOSYSTEMS = [
    "midnight", "aleo", "noir", "aztec", "starknet", "cairo",
    "stacks", "mina", "risc0", "sp1", "plonky3",
]

# In-process cache to avoid hammering public endpoints
_cache: dict[str, Any] = {}
_CACHE_TTL_SEC = 60


def _fetch(url: str) -> dict:
    """Fetch a JSON URL with 60s cache."""
    now = time.time()
    entry = _cache.get(url)
    if entry and (now - entry["fetched_at"]) < _CACHE_TTL_SEC:
        return entry["data"]
    with httpx.Client(timeout=15.0, headers={"User-Agent": USER_AGENT}) as c:
        r = c.get(url)
        r.raise_for_status()
        data = r.json()
    _cache[url] = {"data": data, "fetched_at": now}
    return data


def _fetch_feed() -> dict:
    """Fetch the full live bounty feed."""
    return _fetch(FEED_URL)


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
        ecosystem: filter by ecosystem (e.g. "midnight", "aleo", "noir", "aztec", "starknet", "stacks", "mina", "risc0")
        min_reward_usd: minimum reward in USD
        limit: max bounties to return (1-50)

    Returns: list of matching bounties with id, title, reward, repo, issue_url, source, scoring.
    """
    feed = _fetch_feed()
    bounties = feed.get("bounties", [])
    out = []
    q_lower = query.lower() if query else None
    eco_lower = ecosystem.lower() if ecosystem else None
    for b in bounties:
        if q_lower and q_lower not in (b.get("title") or "").lower():
            continue
        if source and b.get("source") != source:
            continue
        if eco_lower:
            repo = (b.get("repo") or "").lower()
            org = (b.get("org") or "").lower()
            if eco_lower not in repo and eco_lower not in org:
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
    """Get information on paid Bounty Radar Pro tiers — real-time alerts, webhook delivery, custom filters.

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


# === v0.2.0 new tools ===


@mcp.tool()
def get_bounties_by_ecosystem(ecosystem: str, limit: int = 50) -> dict:
    """Get all open bounties for a specific ZK ecosystem from its dedicated sub-feed.

    Args:
        ecosystem: one of "midnight", "aleo", "noir", "aztec", "starknet", "cairo",
                   "stacks", "mina", "risc0", "sp1", "plonky3" (case-insensitive)
        limit: max bounties to return (1-100)

    Returns: dict with bounty_count, total_pool_usd, bounties[].

    Per-ecosystem sub-feeds are auto-refreshed every 30 minutes alongside the main feed.
    """
    eco = ecosystem.lower().strip()
    if eco not in KNOWN_ECOSYSTEMS:
        return {
            "error": f"unknown ecosystem '{ecosystem}'",
            "known_ecosystems": KNOWN_ECOSYSTEMS,
            "tip": "Use list_ecosystems() to see organizations present in the main feed.",
        }
    try:
        data = _fetch(SUBFEED_URL_TEMPLATE.format(ecosystem=eco))
    except Exception as e:
        # Fall back to filtering the main feed in-process
        feed = _fetch_feed()
        matched = [
            b for b in feed.get("bounties", [])
            if eco in (b.get("repo") or "").lower() or eco in (b.get("org") or "").lower()
        ][: max(1, min(limit, 100))]
        return {
            "ecosystem": eco,
            "bounty_count": len(matched),
            "total_pool_usd": sum((b.get("reward_usd") or 0) for b in matched),
            "bounties": matched,
            "source": "main-feed-fallback",
            "fallback_reason": f"sub-feed fetch failed: {type(e).__name__}",
        }
    bounties = data.get("bounties", [])[: max(1, min(limit, 100))]
    return {
        "ecosystem": eco,
        "bounty_count": len(bounties),
        "total_pool_usd": sum((b.get("reward_usd") or 0) for b in bounties),
        "generated_at": data.get("generated_at"),
        "source_url": SUBFEED_URL_TEMPLATE.format(ecosystem=eco),
        "bounties": bounties,
    }


@mcp.tool()
def get_bounty_stats() -> dict:
    """Compute aggregate stats over the current bounty feed.

    Returns: {
        "total_bounties": int,
        "total_pool_usd": float,
        "by_ecosystem": {org -> {count, total_usd}},
        "by_source": {source -> count},
        "by_reward_band": {"<$100": N, "$100-500": N, ...},
        "top_5_by_reward": [bounty, ...],
        "generated_at": "ISO timestamp",
    }
    """
    feed = _fetch_feed()
    bounties = feed.get("bounties", [])

    by_eco: dict[str, dict[str, float]] = {}
    by_src: dict[str, int] = {}
    by_band: dict[str, int] = {"unknown": 0, "<$100": 0, "$100-500": 0, "$500-1000": 0, "$1000-5000": 0, ">$5000": 0}
    total_pool = 0.0

    for b in bounties:
        org = b.get("org") or "unknown"
        src = b.get("source") or "unknown"
        reward = float(b.get("reward_usd") or 0)
        total_pool += reward

        eco_entry = by_eco.setdefault(org, {"count": 0, "total_usd": 0.0})
        eco_entry["count"] += 1
        eco_entry["total_usd"] += reward

        by_src[src] = by_src.get(src, 0) + 1

        if reward == 0:
            by_band["unknown"] += 1
        elif reward < 100:
            by_band["<$100"] += 1
        elif reward < 500:
            by_band["$100-500"] += 1
        elif reward < 1000:
            by_band["$500-1000"] += 1
        elif reward < 5000:
            by_band["$1000-5000"] += 1
        else:
            by_band[">$5000"] += 1

    top_5 = sorted(bounties, key=lambda b: -(b.get("reward_usd") or 0))[:5]
    top_5_compact = [
        {"id": b.get("id"), "title": b.get("title"), "reward": b.get("reward"),
         "reward_usd": b.get("reward_usd"), "issue_url": b.get("issue_url")}
        for b in top_5
    ]

    return {
        "total_bounties": len(bounties),
        "total_pool_usd": round(total_pool, 2),
        "by_ecosystem": {k: {"count": v["count"], "total_usd": round(v["total_usd"], 2)}
                         for k, v in sorted(by_eco.items(), key=lambda kv: -kv[1]["count"])},
        "by_source": dict(sorted(by_src.items(), key=lambda kv: -kv[1])),
        "by_reward_band": by_band,
        "top_5_by_reward": top_5_compact,
        "generated_at": feed.get("generated_at"),
    }


@mcp.tool()
def get_recent_bounties(hours: int = 24, min_reward_usd: int = 0, limit: int = 30) -> list[dict]:
    """Get bounties first seen within the last N hours, sorted by recency.

    Args:
        hours: lookback window (1-168, default 24)
        min_reward_usd: filter out bounties below this threshold
        limit: max results (1-100)

    Returns: list of recent bounties with id, title, reward, first_seen_at, ecosystem.

    Useful for "what's new today" alerts. Use a small hours value (1-6) for high-frequency
    polling, or 24-168 for daily/weekly digest construction.
    """
    feed = _fetch_feed()
    bounties = feed.get("bounties", [])
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max(1, min(hours, 168)))

    matched = []
    for b in bounties:
        ts_raw = b.get("first_seen_at")
        if not ts_raw:
            continue
        try:
            ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        except Exception:
            continue
        if ts < cutoff:
            continue
        if (b.get("reward_usd") or 0) < min_reward_usd:
            continue
        matched.append({
            "id": b.get("id"),
            "title": b.get("title"),
            "reward": b.get("reward"),
            "reward_usd": b.get("reward_usd"),
            "repo": b.get("repo"),
            "org": b.get("org"),
            "issue_url": b.get("issue_url"),
            "source": b.get("source"),
            "first_seen_at": ts_raw,
        })

    # Sort by recency (newest first)
    matched.sort(key=lambda b: b.get("first_seen_at", ""), reverse=True)
    return matched[: max(1, min(limit, 100))]


def main() -> None:
    """Entry point — runs the stdio MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
