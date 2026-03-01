---
name: init-vectordb
description: Initialize the ChromaDB vector store for research content. Installs dependencies, creates .gitignore entry, and smoke-tests the database. Run this before using /ask-research or the vector store integration.
argument-hint:
allowed-tools: Bash, Read, Write
---

# Initialize Vector Store

Set up the ChromaDB vector store for persisting research content.

## Instructions

Run the init script:

```bash
python3.13 .claude/skills/init-vectordb/scripts/init_vectordb.py
```

The script will:

1. Check that python3.13 is available
2. Install `chromadb` via pip (skips if already installed)
3. Append `research-vectordb/` to `.gitignore` (creates the file if needed)
4. Initialize the ChromaDB persistent store and create the `research` collection as a smoke test
5. Report success or failure with clear next steps

## After Success

Tell the user:

- The vector store is ready at `./research-vectordb/`
- Research agents will now automatically save content to the vector store during `/deep-research`
- Use `/ask-research <question>` to query the stored research content
