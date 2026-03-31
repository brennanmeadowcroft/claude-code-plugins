---
name: start-day
description: Morning briefing — pulls today's Google Calendar events, Todoist tasks, weekly goals, and priority emails, finds relevant meeting notes by searching for today's date, and synthesizes a prioritized daily plan. Optionally creates today's daily note. Trigger when the user says "start my day", "morning briefing", or invokes /start-day. Must be run from the root of the Obsidian vault.
argument-hint: "[--skip-daily-note]"
---

# Start Day

You are helping the user plan their day. Pull data from their calendar, task manager, weekly goals, and priority emails, find relevant meeting notes in the vault, and synthesize a clear morning briefing.

## Vault Paths (relative to vault root)

- Daily notes: `02-AreasOfResponsibility/Daily Notes/`
- Meeting notes: `02-AreasOfResponsibility/Notes/`

## Phase 0: Get Today's Date

Run via Bash:
```bash
date "+%Y-%m-%d %A"
```

Store TODAY as the date string (e.g., `2026-03-30`) and DAY_NAME (e.g., `Monday`).

Also compute the Monday of the current week:
```bash
# Get Monday of current week (works on both Linux and macOS)
python3 -c "from datetime import date, timedelta; today=date.today(); monday=today - timedelta(days=today.weekday()); print(monday.strftime('%Y-%m-%d'))"
```

Store WEEK_MONDAY as that date string (e.g., `2026-03-30`).

## Phase 1: Gather Today's Data

Run these in parallel where possible:

**Calendar:** Call `list-events` on the Google Calendar MCP server for today (midnight to midnight). For each event capture: title, start/end time, attendees, video call link if present. If the Google Calendar MCP server is unavailable, tell the user and ask them to describe their day's schedule manually.

**Todoist — due today:** Call `get_tasks` filtered to tasks due today. For each task capture: name, project, priority (p1–p4), any due time. If Todoist MCP is unavailable, tell the user and continue without task data.

**Todoist — overdue:** Call `get_tasks` filtered to overdue tasks. Note how many days overdue each task is.

**Todoist — weekly goals:** Call `get_projects` to find the project named `Priorities`. Then call `get_tasks` filtered to that project to find the task named `Week of WEEK_MONDAY` (e.g., `Week of 2026-03-30`). If found, fetch its subtasks — these are the weekly goals. If the task is not found, note that no weekly goals are set for this week.

**Priority emails:** Call `list-messages` (or the equivalent tool) on the Gmail MCP server, fetching messages with each of the following labels in parallel:
- `Priority/p1`
- `Priority/p2`
- `Priority/p3`

For each email capture: subject, sender, date received, a one-sentence summary of the content. If the Gmail MCP server is unavailable, tell the user and continue without email data.

**Meeting notes for today:** Use Grep to search for notes containing today's date string:
```bash
grep -rl "TODAY" "02-AreasOfResponsibility/Notes/"
```
Replace TODAY with the actual date (e.g., `2026-03-30`). These are long-running meeting notes that have a section for today, added by `/finish-day` the previous evening. Read each matching file to get the section content.

**Existing daily note:** Check if today's daily note exists:
```bash
ls "02-AreasOfResponsibility/Daily Notes/TODAY.md" 2>/dev/null
```
If it exists, read it with the Read tool.

## Phase 2: Synthesize Morning Briefing

Present the briefing in this structure:

---

### Good [morning/afternoon] — [DAY_NAME], [Full Date]

**At a Glance**
[X] calendar events · [Y] tasks due today · [Z] overdue · [N] priority emails

**Calendar**
List events chronologically with start and end times. Flag any day with more than 4 hours of back-to-back meetings. Note if a meeting note was found for any event (e.g., `→ [[1:1 with Alex]]`).

**Priority Emails**
List emails grouped by priority label (p1 first, then p2, then p3). For each email show: sender, subject, and one-sentence summary. Flag any p1 emails prominently. If no priority emails were found, omit this section.

**Daily Priorities**
Synthesize a ranked list of 3–5 focus areas for the day. Base the ranking on all available signals:
- **Weekly goals** (from the Todoist "Week of WEEK_MONDAY" task subtasks) — surface any goals that should have progress made today
- **Todoist p1 and p2 tasks** — include due today and overdue items
- **Priority emails** — if any p1/p2 emails require action, include them

For each suggested priority briefly explain the source signal (e.g., "weekly goal: ship auth PR", "p1 task, overdue 2 days", "p1 email from Alex re: contract"). Keep it scannable.

If no weekly goals are set, note it: "No weekly goals found for this week — consider running /wrap-week or setting them in Todoist."

**Overdue Items**
List overdue tasks grouped by how long they've been overdue. Flag anything overdue more than 3 days.

**Suggested Focus Blocks** (only if there are clear calendar gaps)
Based on gaps between events, suggest 1–3 windows for deep work. Example: "9:00–11:00 — clear before standup, good for [top priority]."

**Today's Meeting Notes**
If meeting notes were found for today, list the note title and any relevant content from the today section.

---

## Phase 3: Create Daily Note (optional)

Ask: "Would you like me to create today's daily note?"

If yes (and one doesn't already exist), use the Write tool to create `02-AreasOfResponsibility/Daily Notes/TODAY.md`:

```markdown
---
date: TODAY
tags: [daily-note]
---

# DAY_NAME, Full Date

## Daily Priorities

[Top 3 suggested priorities from Phase 2, with source signals]

## Schedule

[Calendar events, one per line with times]

## Meeting Notes

[Wiki-links to today's relevant meeting notes, e.g., [[1:1 with Alex]], [[Team Standup]]]

## Notes

## End of Day
<!-- Filled in by /finish-day -->
```

If a daily note already exists, use the Edit tool to add or update only the "Daily Priorities" section.

## Quality Notes

- Always use the date from Bash, never infer it
- Priorities should reflect urgency (due dates, overdue status), importance (Todoist priority levels), weekly goals alignment, and email urgency
- Weekly goals provide the strategic lens — prefer tasks that advance a weekly goal over pure urgency when both are present
- Keep the briefing scannable — headers and bullets, not paragraphs
- Meeting note wiki-links use Obsidian format: `[[Note Name]]`
- If no meeting notes are found for today, omit that section — it means `/finish-day` wasn't run last night
- If the Gmail MCP server tool name differs from `list-messages`, use whatever list/search tool is available on that server
