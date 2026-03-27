---
name: codebase-cartographer
description: Automated parallel scan of a codebase that produces CODEBASE_MAP.md and ORIENTATION.md reference documents. Explores structure, domain concepts, and git history to create a comprehensive orientation package. Use when first encountering an unfamiliar codebase.
argument-hint: "[--path <dir>]"
---

# Codebase Cartographer

You are mapping an unfamiliar codebase to produce reference documentation that helps a developer orient quickly and start contributing.

## Step 1: Determine scope

If the user passed `--path <dir>`, scope ALL analysis to that directory. Otherwise, use the current working directory.

Store the target path — all file references in output docs should be relative to this path.

## Step 2: Quick detection

Before launching parallel exploration, do a fast scan to identify the tech stack. Check for:

- `package.json`, `tsconfig.json` → Node.js/TypeScript
- `Cargo.toml` → Rust
- `go.mod` → Go
- `pyproject.toml`, `setup.py`, `requirements.txt` → Python
- `pom.xml`, `build.gradle` → Java/Kotlin
- `Gemfile` → Ruby
- `Dockerfile`, `docker-compose.yml` → Containerized
- `README.md`, `CLAUDE.md` → Existing documentation
- `.github/`, `.gitlab-ci.yml` → CI/CD

Note what you find — this informs the parallel exploration.

## Step 3: Parallel exploration

Launch **3 Explore agents in parallel** (use the Agent tool with subagent_type "Explore"), each with a specific focus. Provide each agent with the target path and tech stack context from Step 2.

### Agent 1 — Structure & Stack

Prompt: "Explore the codebase at [target path] to map its structure. This is a [tech stack] project. Find and report:
1. The complete directory tree (top 2-3 levels, noting purpose of each directory)
2. Entry points (main files, route definitions, event handlers, CLI entry points)
3. Build system and configuration (how to build, run, and test)
4. CI/CD configuration
5. Key configuration files and what they control
6. Test setup (framework, test file locations, how to run tests)
7. External dependencies that reveal what the app does (scan dependency manifest files)
Be thorough — read key files, not just filenames."

### Agent 2 — Domain & Patterns

Prompt: "Explore the codebase at [target path] to understand its domain and design patterns. This is a [tech stack] project. Find and report:
1. Data models, types, schemas, and interfaces — what are the core domain objects?
2. API routes or endpoints — what operations does the system expose?
3. Business logic location — where do the 'rules' live?
4. **Design patterns** — Identify specific, named patterns at two levels:

   **GoF / code-level patterns** (how individual classes/modules are structured):
   Factory, Builder, Singleton, Observer/Event Emitter, Strategy, Decorator, Adapter, Facade, Command, State Machine, Iterator, Proxy, Chain of Responsibility

   **Application architecture patterns** (how the app is organized internally):
   - Fowler's PoEAA: Repository, Unit of Work, Active Record, Data Mapper, Service Layer, Gateway
   - DDD: Aggregates, Bounded Contexts, Value Objects, Entities, Domain Events, Domain Services
   - Structural: MVC/MVVM/MVP, Clean Architecture, Hexagonal/Ports & Adapters, CQRS, Event Sourcing, Middleware/Pipeline, Dependency Injection

   For each pattern found, report:
   - The pattern name and which category it belongs to (GoF or application architecture)
   - The file(s) where it's implemented
   - A concrete example (function name, class name, or code snippet)
   - How to extend it (e.g., 'add a new case to the switch' or 'implement the interface')
   Only report patterns you can point to in the code — don't guess or force-fit.
5. Naming conventions and code organization style
6. Key abstractions — what are the main classes/modules/functions and how do they relate?
7. Domain glossary — business terms used in the code and what they mean
Read the actual code in key files, not just filenames. Look at models, services, handlers, and types."

### Agent 3 — History & Hotspots

Prompt: "Analyze the git history of the codebase at [target path] to understand its evolution. Run these git commands and report findings:
1. `git log --oneline -30` — recent commit messages (what's been worked on lately?)
2. `git log --format='%aN' | sort | uniq -c | sort -rn | head -10` — top contributors
3. `git log --since='3 months ago' --format='' --name-only | sort | uniq -c | sort -rn | head -20` — most-changed files in last 3 months (hotspots)
4. `git log --since='1 month ago' --oneline` — last month's activity summary
5. `git log --diff-filter=A --format='' --name-only | wc -l` vs `git ls-files | wc -l` — rough sense of codebase growth
6. Look at recent merge commits or PR-style messages to understand current workstreams
Scope all git commands to [target path] using `-- [target path]` where applicable.
Summarize: What areas are actively evolving? What areas are stable? Who works on what?"

## Step 4: Synthesize into CODEBASE_MAP.md

Combine findings from all three agents into a structured reference document. Write it to `[target path]/CODEBASE_MAP.md`.

Use this template:

```markdown
# Codebase Map

> Auto-generated by `/codebase-cartographer` on [date]. This is a reference document — not a substitute for reading the code.

## Tech Stack

[Language, framework, key libraries — 2-3 lines max]

## Directory Structure

[Annotated directory tree, 2-3 levels deep. Each directory gets a one-line purpose annotation.]

```
src/
├── api/          — REST API route handlers
├── models/       — Database models and domain types
├── services/     — Business logic layer
├── utils/        — Shared utilities
└── index.ts      — Application entry point
```

## Key Entry Points

[List the main entry points with file paths and what they do]

## Core Domain Concepts

[Table mapping business terms to code locations]

| Concept | Code Location | Description |
|---------|--------------|-------------|
| ... | ... | ... |

## Data Flow

[How a typical request/operation flows through the system. Use a simple text diagram or numbered steps.]

## Internal Dependencies

[Which modules depend on which. Focus on the major groupings, not every import.]

## Design Patterns Identified

### GoF / Code-Level Patterns

[Patterns found in how individual classes, modules, and functions are structured]

| Pattern | Where Used | Example | How to Extend |
|---------|-----------|---------|---------------|
| Factory | `src/services/factory.ts` | `createHandler(type)` returns typed handler instances | Add a new case to the factory switch |
| Observer | `src/events/emitter.ts` | Components subscribe to domain events via `on()` | Register a new event listener |
| ... | ... | ... | ... |

### Application Architecture Patterns

[Patterns found in how the application is organized — its layers, boundaries, and data flow]

| Pattern | Where Used | Example | How to Extend |
|---------|-----------|---------|---------------|
| Repository | `src/data/userRepo.ts` | Data access behind `find()`, `save()` interfaces | Create a new repo implementing the base interface |
| Service Layer | `src/services/` | Business logic separated from handlers/controllers | Add a new service class for new domain operations |
| ... | ... | ... | ... |

Only list patterns actually found in the code — don't force-fit. For each pattern, note:
- The **canonical example** (best file to read to understand how it's used here)
- **How to extend it** (what you'd do to add new behavior following this pattern)

## Naming Conventions & Code Style

[Naming conventions, file organization style, code style patterns observed]

## Git Hotspots

[Most-changed files, active development areas, recent workstreams]

## Key Files Quick Reference

[Table of the most important files someone new should read]

| File | Why It Matters |
|------|---------------|
| ... | ... |
```

## Step 5: Synthesize into ORIENTATION.md

Write a narrative guide to `[target path]/ORIENTATION.md`.

Use this template:

```markdown
# Orientation Guide

> Auto-generated by `/codebase-cartographer` on [date].

## What This Project Does

[2-3 sentence summary of the project's purpose, based on what you found in code, docs, and domain analysis]

## Architecture at a Glance

[Architecture style (monolith, microservices, serverless, etc.), key layers, how they connect. Keep it to one paragraph.]

## How to Build and Run

[Commands to install dependencies, build, run locally, and run tests. Be specific.]

## Where to Find Things

| I want to... | Look in... |
|--------------|-----------|
| Add a new API endpoint | ... |
| Modify business logic | ... |
| Add a new data model | ... |
| Write a test | ... |
| Change configuration | ... |

## Patterns to Follow

[Key patterns that a new contributor should follow for consistency. Include brief code examples if helpful.]

## Gotchas and Non-Obvious Things

[Anything surprising, unusual, or easy to get wrong. Things that aren't obvious from the code structure alone.]

## Active Development Areas

[What's being worked on recently, based on git history. Helps avoid stepping on toes or picking up stale work.]

## Suggested Next Steps

- Run `/codebase-layers` for an interactive guided tour of specific areas
- Run `/codebase-mikado --goal "your task"` when you're ready to trace a specific change
```

## Step 6: Present summary

After writing both documents, present a brief summary to the user:

1. **One-paragraph overview** of what you found
2. **2-3 things that stand out** (unusual patterns, surprising complexity, notable design choices)
3. **Suggest next steps**: which areas to explore deeper via `/codebase-layers`, or if they have a task, suggest `/codebase-mikado`

Keep the summary concise — the detailed information is in the docs.
