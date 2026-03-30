# Day Manager

Personal productivity assistant for daily and weekly planning. Three skills that work together to help you start your day with clarity, close it out intentionally, and reflect meaningfully at the end of each week.

**Skills:**
- `/start-day` — Morning briefing: calendar, priorities, and today's meeting notes
- `/finish-day` — End-of-day: review, transcript reminder, reschedule, prep tomorrow's notes
- `/wrap-week` — Weekly narrative recap saved to Obsidian

---

## How the Skills Work Together

The skills form a virtuous cycle:

1. **`/finish-day`** preps tomorrow's meeting notes by appending a date-stamped section to each recurring meeting note in Obsidian.
2. **`/start-day`** the next morning finds those sections by searching Obsidian for today's date string — no tags or manual setup needed.
3. **`/wrap-week`** reads the daily notes built up through the week to synthesize a narrative recap.

Run `/finish-day` each evening and `/start-day` each morning for best results. After 2–3 weeks, `/wrap-week` becomes significantly richer.

---

## Prerequisites

All three skills require three MCP servers. Set them up once and they persist in your Claude Code user config.

### 1. Todoist (Official Hosted MCP)

```bash
claude mcp add --transport http todoist https://ai.todoist.net/mcp --scope user
```

Then authenticate inside Claude Code:
```
/mcp
```
Select "todoist" and complete the OAuth flow in your browser.

### 2. Google Calendar

**Step 1:** Create a Google Cloud project and enable the Google Calendar API.
Follow the authentication guide at: https://github.com/nspady/google-calendar-mcp#authentication

Download your OAuth credentials JSON file (e.g., to `~/gcp-oauth.keys.json`).

**Step 2:** Register the MCP server:
```bash
claude mcp add --transport stdio \
  --env GOOGLE_OAUTH_CREDENTIALS=$HOME/gcp-oauth.keys.json \
  google-calendar --scope user \
  -- npx -y @cocal/google-calendar-mcp
```

The first time Claude Code uses this server it will open a browser for OAuth consent.

### 3. Obsidian (mcpvault — filesystem direct)

No Obsidian plugins required. Works even when Obsidian is closed.

```bash
claude mcp add --transport stdio \
  --env VAULT_PATH=/path/to/your/vault \
  obsidian --scope user \
  -- npx -y mcpvault
```

Replace `/path/to/your/vault` with the absolute path to your Obsidian vault (e.g., `/Users/yourname/Documents/MyVault`).

---

## Obsidian Vault Setup

Enable the **Daily Notes** core plugin in Obsidian (Settings → Core Plugins → Daily Notes):
- Folder: `Daily Notes`
- Date format: `YYYY-MM-DD`
- Template: optional — `/start-day` will create notes with its own template

The skills assume this folder structure in your vault:

```
vault/
├── Notes/              ← your existing meeting notes (untouched)
│   ├── 1:1 with Alex.md
│   ├── Team Standup.md
│   └── ...
├── Daily Notes/        ← lightweight day hubs (created by /start-day)
│   ├── 2026-03-30.md
│   └── ...
└── Weekly Recaps/      ← narrative weekly summaries (created by /wrap-week)
    ├── 2026-W13.md
    └── ...
```

Your existing `Notes/` folder is never modified except to append new date sections by `/finish-day`. No content is moved or duplicated.

Override the default paths with arguments if your vault uses different folder names:
```
/start-day --daily-notes-path "Journal/Daily" --notes-path "Meetings"
/wrap-week --weekly-recaps-path "Reviews/Weekly"
```

---

## Transcript Workflow

By default, `/finish-day` shows a checklist reminder to download transcripts and drop them in your n8n pickup folder.

To automate the trigger, expose your n8n webhook as a single-tool MCP server. A minimal implementation using the MCP SDK:

```javascript
// n8n-mcp/index.js
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new McpServer({ name: "n8n", version: "1.0.0" });

server.tool("trigger_transcript_processing", "Trigger n8n transcript workflow", {}, async () => {
  await fetch(process.env.N8N_WEBHOOK_URL, { method: "POST" });
  return { content: [{ type: "text", text: "Transcript processing triggered." }] };
});

await server.connect(new StdioServerTransport());
```

Register it:
```bash
claude mcp add --transport stdio \
  --env N8N_WEBHOOK_URL=https://your-n8n-instance/webhook/transcripts \
  n8n --scope user \
  -- node /path/to/n8n-mcp/index.js
```

Then pass the server name to finish-day:
```
/finish-day --transcript-mcp n8n
```

---

## Tips

**Daily note as a hub.** Keep meeting content in your long-running `Notes/` files. Daily notes link to those notes and capture your intentions and reflections — no duplication.

**Todoist priority discipline.** The morning briefing ranks tasks by p1/p2. If everything is p1, the ranking loses meaning. Consider a personal rule: max 2–3 p1 tasks at any time.

**Calendar blocking.** Block deep-work time as private Google Calendar events. `/start-day` will include those blocks when suggesting focus windows, making the suggestion more useful.

**Weekly recap as a personal changelog.** ISO week filenames (`2026-W13.md`) sort naturally and are easy to review during quarterly or annual reflections.

**Run `/finish-day` before leaving for the day** — not after. The meeting note prep for tomorrow works best when done while context is fresh.

---

## Skills Reference

| Skill | Description | When to use |
|---|---|---|
| `/start-day` | Morning briefing with calendar, tasks, and meeting note links | Each morning before starting work |
| `/finish-day` | Day close-out: review, reschedule, transcript reminder, tomorrow prep | Each evening before logging off |
| `/wrap-week` | Mon–Sun narrative recap saved to Obsidian | Friday afternoon or Sunday evening |

### Arguments

**`/start-day`**
- `--daily-notes-path <path>` — Override default daily notes folder (default: `Daily Notes`)
- `--notes-path <path>` — Override meeting notes folder (default: `Notes`)

**`/finish-day`**
- `--daily-notes-path <path>` — Override default daily notes folder
- `--notes-path <path>` — Override meeting notes folder
- `--transcript-mcp <server-name>` — Name of an MCP server to trigger for transcript processing

**`/wrap-week`**
- `--daily-notes-path <path>` — Override default daily notes folder
- `--weekly-recaps-path <path>` — Override weekly recaps folder (default: `Weekly Recaps`)
