# Secretary

Meeting lifecycle plugin for Claude Code. Five skills that handle everything from pre-meeting context gathering to transcript processing and searchable meeting memory — so every meeting produces structured notes, captured action items, and a queryable history.

The secretary plugin is a domain plugin. It owns the meeting memory vector store and the meeting note lifecycle. The `chief-of-staff` plugin calls into it automatically during `/finish-day` (transcripts + tomorrow's prep) but all skills can be run independently.

---

## Prerequisites

### personal-context (required)

The secretary plugin uses personal-context to resolve attendee names, look up contact details, and access your communication preferences. Install the `personal-context` plugin first.

### Google Calendar (required for meeting-prep and process-transcripts)

```bash
claude mcp add --transport stdio \
  --env GOOGLE_OAUTH_CREDENTIALS=$HOME/gcp-oauth.keys.json \
  google-calendar --scope user \
  -- npx -y @cocal/google-calendar-mcp
```

### Todoist (required for process-transcripts)

```bash
claude mcp add --transport http --scope global todoist https://ai.todoist.net/mcp
```

### Obsidian vault

Meeting notes are read from and written to your Obsidian vault. All path defaults can be overridden via `CLAUDE.md` config or per-invocation arguments — see the chief-of-staff README for the full configuration reference.

### Meeting memory (first-time setup)

The `/ask-meetings` and `/process-transcripts` skills use a ChromaDB vector store for semantic search over past meetings. Initialize it once from your vault root before first use:

```
/secretary:init-meeting-memory
```

The store is created at `.meeting-memory/` in your vault root and is excluded from git and Nextcloud sync automatically.

---

## Skills Reference

| Skill | Description | When to use |
|-------|-------------|-------------|
| `/secretary:meeting-prep` | Gathers context from calendar, Todoist, project plans, prior notes, Slack, and Gmail — writes a structured meeting note with agenda | Before any meeting |
| `/secretary:process-transcripts` | Processes raw transcripts into structured notes, creates Todoist action items, indexes notes into meeting memory | After meetings with transcripts |
| `/secretary:ask-meetings` | Queries meeting memory with a natural language question — surfaces decisions, themes, and history across all past meetings | Anytime you need meeting history |
| `/secretary:index-meeting-note` | Manually indexes a meeting note into ChromaDB — for re-indexing or backfilling historical notes | On demand |
| `/secretary:init-meeting-memory` | One-time setup — installs ChromaDB, creates the vector store, runs a smoke test | Once, before first use |

### Arguments

**`/secretary:meeting-prep`**
- `--notes-path <path>` — Override meeting notes folder (default: `02-AreasOfResponsibility/Notes`)
- `--projects-path <path>` — Override projects folder (default: `01-Projects`)

**`/secretary:process-transcripts`**
- `--notes-path <path>` — Override meeting notes folder (default: `02-AreasOfResponsibility/Notes`)
- `--date <YYYY-MM-DD>` — Process transcripts for a specific date (default: today)
- `--meeting <name>` — Process only a single named meeting
- `--note-file <path>` — Explicit path to the Obsidian meeting note (bypasses auto-detection)
- `--transcript-file <path>` — Explicit path to the transcript file (bypasses auto-detection)

**`/secretary:ask-meetings`**
- Pass your question as free-form text after the skill name: `/secretary:ask-meetings what did we decide about the API redesign?`

**`/secretary:index-meeting-note`**
- `--reindex-file <path>` — Path to a specific meeting note file to index or re-index

---

## Transcript Workflow

Transcripts are expected at `~/Nextcloud/Meeting Uploads/{YYYY-MM-DD}/{derived_filename}_transcript.txt`. The filename is derived from the calendar event title: lowercase, non-alphanumeric characters replaced with underscores.

Examples:
- `"Brennan / Alice"` → `brennan___alice_transcript.txt`
- `"Team Sync"` → `team_sync_transcript.txt`

`/process-transcripts` auto-detects transcripts for today's meetings by matching against the calendar. Use `--meeting` or `--transcript-file` to process a specific file directly.

After each transcript is processed, the note is automatically indexed into meeting memory via `/secretary:index-meeting-note`.

---

## Tips

**Run `/secretary:meeting-prep` the night before.** `/chief-of-staff:finish-day` does this automatically for tomorrow's calendar — but you can run it manually for any meeting at any time.

**Meeting memory persists across sessions.** The ChromaDB store lives in your vault, not in Claude Code's context. Ask it anything: `"what was the status of the API migration last month?"`, `"when did we last talk about team structure with Alice?"`.

**`process-transcripts` validates before writing.** It shows you all action items for approval before creating any Todoist tasks — you decide what gets added and can exclude individual items.

**Recurring vs. ad-hoc notes.** Recurring meeting notes follow the pattern `{Name} - {Year}.md` and accumulate date sections over time. Ad-hoc notes are single-file. The skill auto-detects which pattern applies based on the calendar event.
