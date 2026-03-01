---
name: platform-build-feature-from-plan
description: The development workflow for building a feature based on a plan document. It should only be used when building a feature for the platform server, and not for other applications. Indicated when the user asks to build a platform feature and references a plan document.
---

# Platform Build Feature From Plan

## Required Inputs

Before starting, collect the following from the user:

- **Plan Folder** - the folder containing the PLAN.md file for the feature to build (e.g. `plans/mvp`).
- **Phase Number** - Optional phase number to target within the plan (e.g. `1`), or "all" to build all phases. If not specified, assume "all".

Do not proceed until all required inputs are confirmed.

## Steps to follow

The user will provide a plan folder and optional phase number. The plan will be documented at `plans/{plan-folder}/PLAN.md`. The plan will include a list of features to build, possibly organized by phase. For each feature, the plan will specify the files to create or modify, along with any relevant code snippets or instructions.

**If the user specifies a phase number**, only build the features listed under that phase in the plan. **If the user specifies "all" or does not specify a phase**, build all features across all phases in the plan.

For each feature to build, follow these steps:

1. Unless otherwise specified by the user, create a new branch named `feature/{feature-name}` based on `main` (e.g. `feature/auth-middleware`).
2. Review the plan details for the feature including additional files within the plan folder. Any files besides `PLAN.md`, `phase-status.md`, and `memory.md` provide additional context such as design documents, notes or code snippets to assist with the implementation.
3. Identify the changes to be made based on the plan.
4. Write the task list to `plans/{plan-folder}/{phase number}/phase-status.md`.
5. Proceed with the work from the task list. As tasks are completed, update the list in the relevant `phase-status.md` file.
6. Once all tasks are complete, update `plans/{plan-folder}/m{phase number}/memory.md` with implementation notes, challenges faced and solutions found. You do not need to document the routine changes; focus on the non-obvious work and decisions that were made. This memory file will serve as a reference for future phases and for other engineers (or you) working on the codebase, so include any details that would be helpful for understanding the implementation and reasoning behind it.
7. Report back to the user with a summary of the work done as well as details about how to test the changes.
