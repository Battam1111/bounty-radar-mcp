"""Smoke test: the live bounty feed is reachable and non-empty.

Run via: python -m tests.test_live_feed_reachable
Or via:  pytest tests/test_live_feed_reachable.py
"""
from bounty_radar_mcp.server import _fetch_feed


def test_live_feed_reachable():
    d = _fetch_feed()
    assert "bounties" in d, f"no 'bounties' key in feed: {list(d.keys())}"
    n = len(d["bounties"])
    assert n > 0, "feed is empty"
    print(f"feed has {n} bounties")


if __name__ == "__main__":
    test_live_feed_reachable()
