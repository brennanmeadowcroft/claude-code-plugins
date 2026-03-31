---
name: finish-day
description: End-of-day wrap-up — reviews completed and incomplete Todoist tasks, recaps today's calendar, reminds about transcripts (with optional n8n MCP trigger), reschedules incomplete tasks, triages the Todoist inbox, preps tomorrow's meeting notes in Obsidian with context bullets, and updates today's daily note with a day summary. Trigger when the user says "finish my day", "wrap up today", "end of day", or invokes /finish-day. Must be run from the root of the Obsidian vault.
argument-hint: "[--transcript-mcp <server-name>]"
---

# Finish Day

You are helping the user close out their workday. Review what was accomplished, handle transcripts, reschedule incomplete tasks, triage the inbox, prep tomorrow's meeting notes, and write an honest day summary.

## Vault Paths (relative to vault root)

- Daily notes: `02-AreasOfResponsibility/Daily Notes/`
- Meeting notes: `02-AreasOfResponsibility/Notes/`

## Meeting Note Templates

Use these templates when creating new meeting note files. Choose based on meeting type.

### Recurring Meeting Template

For meetings that happen on a regular cadence (standups, 1:1s, team syncs):

```markdown
---
meeting: <Meeting Name>
type: recurring
---

# <Meeting Name>

<!-- One file per recurring meeting. Each session gets a new dated section appended by /finish-day. -->
```

### One-Time Meeting Template

For ad-hoc, project kick-offs, interviews, or any meeting that won't recur:

```markdown
---
meeting: <Meeting Name>
date: <DATE>
type: one-time
attendees: []
---

# <Meeting Name>

**Date:** <DATE>
**Attendees:** 

## Objective

## Notes

## Action Items
- 

## Follow-up

```

When `/finish-day` asks "Want me to create a note?" and the user confirms, infer the type from context (recurring calendar event → recurring template, one-off → one-time template) and ask if unsure.

## Phase 0: Get Today's and Tomorrow's Dates

Run via Bash:
```bash
echo "TODAY=$(date +%Y-%m-%d)"
echo "TOMORROW=$(date -v+1d +%Y-%m-%d 2>/dev/null || date -d tomorrow +%Y-%m-%d)"
```

Store TODAY and TOMORROW.

## Phase 1: Gather Today's Data

Run in parallel:

**Completed tasks:** Call `get_completed_tasks` on the Todoist MCP server filtered to today. Capture task name and project.

**Still-open tasks:** Call `get_tasks` filtered to due today and overdue. These are tasks that weren't finished.

**Inbox tasks:** Call `get_tasks` filtered to the Inbox project (project_id for Inbox, or tasks with no project). Capture task name, priority, and any existing due date.

**Today's calendar:** Call `list-events` on the Google Calendar MCP server for today.

**Today's daily note:** Check for and read `02-AreasOfResponsibility/Daily Notes/TODAY.md` using the Read tool if it exists.

If either MCP server is unavailable, tell the user which one and continue with whatever data is accessible.

## Phase 2: Day Review

Present a brief, honest review:

---

**What You Accomplished**
- Completed Todoist tasks (with project)
- Calendar events that happened today

**Still Open**
- Incomplete tasks with their original due date

**Day Patterns** (only if notable)
A p1 task finished, a project milestone hit, or a day that ran particularly long on meetings.

---

## Phase 3: Transcript Reminder

ALWAYS present this step. Never skip it.

---

**Transcript Upload**

If you recorded any meetings or conversations today, now is the time to download and save them to your n8n pickup folder.

```
[ ] Downloaded all transcripts from your recording tool
[ ] Saved to n8n pickup folder
```

If `--transcript-mcp <server-name>` was passed and that MCP server is available:
> I see the `<server-name>` MCP server is configured. Would you like me to trigger transcript processing now? Tell me which tool to call and I'll run it. Then call whatever tool the user specifies.

If no transcript MCP is configured:
> To automate this in the future, expose your n8n webhook as an MCP server and pass `--transcript-mcp <server-name>` to this skill.

---

Options:
1. **Done** — transcripts are handled
2. **Skip** — no transcripts today
3. **Remind me later** — note it in the daily note

## Phase 4: Reschedule Incomplete Tasks

Skip this phase if there are no incomplete tasks.

Present all incomplete tasks at once and ask the user what to do with each:
- **Tomorrow** — update due date to TOMORROW via `update_task`
- **Later this week** — ask for specific day
- **Next week** — update to next Monday
- **Deprioritize** — set no due date or lower priority
- **Done / Cancel** — mark complete via `complete_task`

Collect all decisions first, then execute all updates together in one batch.

## Phase 5: Inbox Triage

Skip this phase if there are no inbox tasks.

The Todoist Inbox is a holding area — tasks sitting there are unprocessed and need a home. Present all inbox tasks at once and ask the user what to do with each:

- **Schedule + move to project** — ask for a due date and which project, then call `update_task` to set both
- **Move to project (no date)** — move to a project without scheduling
- **Delete** — call `delete_task`
- **Keep in inbox** — leave as-is (use sparingly; this is the exception, not the norm)

Format the prompt clearly, e.g.:

> **Inbox Triage** (5 tasks)
>
> 1. "Research new API options" — Schedule + move? Delete? Keep?
> 2. "Call dentist" — ...
> ...

Collect all decisions first, then execute all updates together in one batch.

## Phase 6: Prep Tomorrow's Meeting Notes

This is what enables `/start-day` to find relevant meeting notes via date-string search tomorrow morning.

1. Call `list-events` for TOMORROW to get tomorrow's calendar events.
2. For each named meeting on tomorrow's calendar:
   a. Search for a matching note file using Glob: `02-AreasOfResponsibility/Notes/*.md`, then look for a filename that closely matches the meeting title.
   b. **Classify the meeting:** recurring (appears on a regular cadence) or one-time (ad-hoc, no prior note likely exists).
   c. **If a matching note is found:**
      - Read the last 60–80 lines of the file to extract context from the most recent session.
      - Look for any unresolved **Action Items** in the previous section (lines under `### Action Items` that are not checked off).
      - Also call `get_tasks` filtered to the Todoist project most closely associated with this meeting to find open tasks.
      - Append this section to the end of the file using the Edit tool:

```markdown

## TOMORROW

### Context
<!-- Carried from last session and open project tasks -->
- [action item or open task from previous meeting / related project]
- [action item or open task]

### Agenda
- 

### Notes

### Action Items
- 

```

      Replace `TOMORROW` with the actual date string (e.g., `## 2026-03-31`).
      Populate `### Context` with the actual pulled items — omit the section entirely if there's nothing relevant to carry forward.

   d. **If no matching note is found:**
      - Ask the user: "I don't see a note for '[Meeting Name]'. Want me to create one? (recurring / one-time / skip)"
      - If confirmed, use the Write tool to create `02-AreasOfResponsibility/Notes/<Meeting Name>.md` using the appropriate template from the **Meeting Note Templates** section above, then append the dated section stub.

3. Tell the user which notes were updated: "Prepped sections in: [[1:1 with Alex]], [[Team Standup]]"

## Phase 7: Tomorrow Preview (optional)

Ask: "Want a quick look at what's lined up for tomorrow?"

If yes, present:
- Tomorrow's calendar events (already fetched in Phase 6)
- Todoist tasks due tomorrow (call `get_tasks` filtered to TOMORROW)

Keep it brief — this is a preview, not a full briefing.

## Phase 8: Update Today's Daily Note

Use the Edit tool to append an "End of Day" section to `02-AreasOfResponsibility/Daily Notes/TODAY.md`. If no daily note exists, use the Write tool to create a minimal one.

Section to append:

```markdown

## End of Day
*Completed by /finish-day*

### Accomplished
[Completed tasks and notable meetings]

### Carried Forward
[Rescheduled tasks and where they went — e.g., "Fix auth bug → tomorrow", "Update docs → deprioritized"]

### Reflection
[User's response to: "Any thoughts on today to capture in your notes?" — or "—" if skipped]
```

Ask before writing: "Any thoughts on today to capture in your notes?" Include their response verbatim, or "—" if they skip.

## Quality Notes

- The day review should be honest — acknowledge what didn't happen without judgment
- Inbox triage (Phase 5) goal: zero items left in inbox. Push back gently if the user wants to "keep" many tasks there
- Meeting note prep (Phase 6) is the most important step for enabling tomorrow's start-day flow; don't skip it
- Context bullets in Phase 6 should be actual carried items, not placeholders — omit the `### Context` block if there's nothing real to put there
- The transcript reminder (Phase 3) must always be shown
- Batch all Todoist updates — don't send them one at a time while the user is still deciding
