# bounty-radar-mcp

> MCP server for the live [Bounty Radar feed](https://battam1111.github.io/bounty-radar-data/) — query ZK + AI bounties across 11 ecosystems from inside Claude Desktop, Claude Code, Cursor, Windsurf, LibreChat, or any [MCP](https://modelcontextprotocol.io/) client.

## Why

There are 11+ ZK / AI bounty platforms (Algora, Drips Wave, Code4rena, Cantina, Sherlock, Immunefi, Bountycaster, plus per-ecosystem GitHub label-search). Manually monitoring them is slow. We aggregate them 24/7 and expose the firehose as MCP tools so an LLM can search, filter, and summarize directly from your editor.

## Install

```bash
# Recommended: uvx (no install, runs from GitHub):
uvx --from git+https://github.com/Battam1111/bounty-radar-mcp.git bounty-radar-mcp

# Or with pipx:
pipx install git+https://github.com/Battam1111/bounty-radar-mcp.git
```

## Configure in Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "bounty-radar": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/Battam1111/bounty-radar-mcp.git", "bounty-radar-mcp"]
    }
  }
}
```

(Or, if you already ran `pipx install` above, just `"command": "bounty-radar-mcp"`.)

Restart Claude Desktop. Type `/` to see the new tools.

## Configure in Claude Code

```bash
claude mcp add bounty-radar -- uvx --from git+https://github.com/Battam1111/bounty-radar-mcp.git bounty-radar-mcp
```

## Configure in Cursor

`~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "bounty-radar": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/Battam1111/bounty-radar-mcp.git", "bounty-radar-mcp"]
    }
  }
}
```

(Or, if you already ran `pipx install` above, just `"command": "bounty-radar-mcp"`.)

## Tools exposed

| Tool | What it does |
|---|---|
| `search_bounties` | Search the live feed by query / source / ecosystem / minimum reward |
| `get_bounty` | Get full details of one bounty by ID |
| `list_ecosystems` | Which ecosystems are currently represented |
| `list_sources` | Which source platforms feed the radar |
| `radar_summary` | Top-level status: total open bounties, last refresh time |
| `upgrade_info` | Pricing for real-time alerts / private API / competitor heat-map tiers |

## Example LLM prompts

> "Use bounty-radar to find any open ZK bounty paying over \$500 in the Aleo ecosystem."

> "Search for Noir tutorials I could write — sort by merge_probability."

> "What's the latest from Midnight Network bounty board?"

> "Get the full details for bounty `gh-midnightntwrk-contributor-hub-312`."

## Free tier vs paid tier

Free: top 200 open bounties, refreshed every 30 min.

For:
- Real-time alerts (Telegram bot or webhook delivery, sub-30-second latency)
- Private API with full eval scoring + competitor heat-map
- Merge-probability scoring per bounty
- White-label & team seats

→ [Subscribe at $19 / $97 / $497 monthly tiers](https://battam1111.github.io/bounty-radar-data/)

The free MCP server is more than enough for casual bounty hunting; the paid tiers are for full-time hunters, audit firms, and dev shops.

## Architecture

- Pure stdio MCP, no DB, no auth
- Caches feed locally for 60 seconds to avoid hammering the public endpoint
- Public feed: <https://battam1111.github.io/bounty-radar-data/feed.json>
- Updated every 30 minutes by a 24/7 scanner that aggregates 5 sources + 11 ecosystems

## Sibling projects

- [Midnight ZK Cookbook](https://battam1111.github.io/midnight-zk-cookbook/) — 11 tutorials across Midnight, Aleo, Noir
- [zk-pipeline-doctor](https://github.com/Battam1111/zk-pipeline-doctor) — OSS CLI that diagnoses ZK circuit projects

## License

MIT.

## Author

Yanjun Chen ([@Battam1111](https://github.com/Battam1111)). PRs and detector suggestions welcome.

---

<!-- related-projects:start -->

## Related projects

- [**bounty-radar-data**](https://github.com/Battam1111/bounty-radar-data) — Source-of-truth feed this server queries
- [**midnight-zk-cookbook**](https://github.com/Battam1111/midnight-zk-cookbook) — currently in rollback; see DISCLOSURE there
- [**zk-pipeline-doctor**](https://github.com/Battam1111/zk-pipeline-doctor) — OSS CLI for auditing ZK projects

<!-- related-projects:end -->
