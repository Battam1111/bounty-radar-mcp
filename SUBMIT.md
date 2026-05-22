# Submission templates

When ready to submit to communities, here are pre-written posts.

---

## Hacker News (`Show HN`)

**Title** (under 80 chars):
```
Show HN: Bounty-Radar MCP – search ZK+AI bounties from any MCP client
```

**Body** (paste in the comments box after submission):
```
I run a 24/7 scanner across 11 ZK + AI bounty platforms (Algora, GitHub
label-search, Drips Wave, Code4rena, Cantina, Sherlock, Immunefi,
Bountycaster, plus per-ecosystem polling for Midnight, Aleo, Noir, Aztec,
Stacks, Starknet, Mina, risc0). This MCP server exposes the live feed
as 6 tools so any MCP client (Claude Desktop, Claude Code, Cursor,
Windsurf, LibreChat) can search bounties without leaving the editor.

- pipx install bounty-radar-mcp
- Add to claude_desktop_config.json
- Ask Claude: "find open ZK bounties paying over $500 in Aleo or Noir"

Free tier covers top 200 open bounties refreshed every 30 min. Code is
MIT, the live feed is at
https://battam1111.github.io/bounty-radar-data/ , and the cookbook the
scanner originally fed is at
https://battam1111.github.io/midnight-zk-cookbook/ .

I built this because I noticed every ZK bounty hunter I know was manually
context-switching between 5+ platforms. The 24/7 polling + LLM scoring
+ competitor heat-map already runs for my own bounty work; this just
exposes the firehose so others can plug in.

Happy to talk about architecture (launchd > cron, Frontier as the
evaluator LLM, why the public free feed lives on GitHub Pages, how Polar
handles the paid tiers).
```

---

## Reddit r/programming or r/zkproofs

**Title**:
```
I built an MCP server that lets Claude/Cursor search live ZK+AI bounties (open source, MIT)
```

**Body**: same as HN but slightly more casual.

---

## Twitter/X thread (5 tweets)

1/ I built an MCP server for the live Bounty Radar feed. Now you can search ZK + AI bounties across 11 ecosystems from inside Claude Desktop, Cursor, or any MCP client.

→ https://github.com/Battam1111/bounty-radar-mcp

2/ Why? Manually monitoring Algora + Drips Wave + Code4rena + 11 ecosystem GitHub orgs is slow. I aggregate them 24/7 anyway for my own bounty work — this exposes the firehose so others can plug in.

3/ Install:
```
pipx install bounty-radar-mcp
```
Then in claude_desktop_config.json:
```json
{
  "mcpServers": {
    "bounty-radar": { "command": "bounty-radar-mcp" }
  }
}
```

4/ 6 tools:
- search_bounties (filter by query/source/ecosystem/reward)
- get_bounty (full details by ID)
- list_ecosystems
- list_sources
- radar_summary
- upgrade_info (real-time alerts on paid tiers)

5/ Free tier is top 200 open bounties refreshed every 30 min. For real-time alerts + competitor heat-map + private API, paid Bounty Radar Pro tiers from $19/mo.

Source: github.com/Battam1111/bounty-radar-mcp
Feed: battam1111.github.io/bounty-radar-data

---

## Bluesky (concise)

```
🛠️ New OSS: bounty-radar-mcp

MCP server so Claude / Cursor / Windsurf can search the live Bounty Radar feed —
11 ZK + AI ecosystems, 200 open bounties, refreshed every 30 min.

pipx install bounty-radar-mcp

Repo: github.com/Battam1111/bounty-radar-mcp
Free, MIT.
```

---

## awesome-mcp-servers PR

Title: `Add bounty-radar-mcp — ZK + AI bounty search via MCP`

Body:
```
- **[bounty-radar-mcp](https://github.com/Battam1111/bounty-radar-mcp)** — Search live ZK + AI bounties across 11 ecosystems from any MCP client. (Python, MIT)
```

Submit as PR against the popular `awesome-mcp-servers` list (e.g.,
https://github.com/punkpeye/awesome-mcp-servers).
