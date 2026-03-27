---
name: codebase-orientation
description: Entry point for codebase orientation. Assesses your familiarity and goals, then routes to the right exploration skill (cartographer, layers, or mikado). Use when you want help understanding a new or unfamiliar codebase.
argument-hint: "[--path <dir>]"
---

# Codebase Orientation — Dispatcher

You are helping the user orient to an unfamiliar codebase. Your job is to assess their situation and route them to the right exploration skill.

## Step 1: Determine the target path

If the user passed `--path <dir>`, use that as the target directory for all analysis.
Otherwise, use the current working directory.

## Step 2: Check for prior orientation work

Look for `CODEBASE_MAP.md` in the target path root. If it exists, the user has already run the cartographer — note this context.

## Step 3: Assess the user's situation

Ask the user **two questions** (use AskUserQuestion):

**Question 1:** "How familiar are you with this codebase?"
- **New** — I've never worked in this codebase before
- **Somewhat familiar** — I've looked around or made a few changes
- **Familiar** — I know the codebase but need help with a specific area

**Question 2:** "Do you have a specific change or task you need to make?"
- **Yes** — I have a specific goal in mind
- **No** — I just want to understand the codebase
- **Sort of** — I have a general area but not a specific task

## Step 4: Route to the appropriate skill

Based on the answers, recommend and invoke the appropriate skill:

| Familiarity | Has Task? | Recommendation |
|------------|-----------|----------------|
| New | No | `/codebase-cartographer` — Start with the big picture. Produces reference docs you can come back to. |
| New | Yes | `/codebase-cartographer` first, then suggest `/codebase-mikado` for the specific task |
| New | Sort of | `/codebase-cartographer` — Map the territory first, then you'll know where to dig in |
| Somewhat | No | `/codebase-layers` — Interactive guided tour to deepen your understanding |
| Somewhat | Yes | `/codebase-mikado` — Trace the dependencies for your specific change |
| Somewhat | Sort of | `/codebase-layers` — Explore interactively, focusing on your area of interest |
| Familiar | No | `/codebase-layers` — Focus on the areas you know least |
| Familiar | Yes | `/codebase-mikado` — Jump straight to tracing your change |
| Familiar | Sort of | `/codebase-layers` — Explore the specific area you're interested in |

**If `CODEBASE_MAP.md` already exists:**
- Mention that prior orientation docs exist
- Bias toward `/codebase-layers` or `/codebase-mikado` since the mapping is already done
- Only suggest re-running cartographer if the user thinks the map may be outdated

Tell the user which skill you recommend and why, then invoke it using the Skill tool. Pass through the `--path` argument if one was provided.
