---
name: save-research-result
description: Save a single evaluated source to the research results JSON file and vector store. Use this immediately after evaluating each source URL — do not wait until the end of the session. Routes to web-results.json (source_type=web) or youtube-results.json (source_type=youtube) and saves full content to ChromaDB in the same call.
argument-hint: <research-folder-path>
allowed-tools: Bash
---

# Save Research Result

## Usage

Read the research folder path from `$ARGUMENTS`. Construct the JSON record from the source you just evaluated, then pipe it to the save script:

```bash
python3.13 .claude/skills/save-research-result/scripts/save_research_result.py <research-folder> <<'RESULT'
{
  "url": "<source URL>",
  "title": "<page or video title>",
  "source_type": "<web or youtube>",
  "content": "<full page content or transcript — for vector store only, not stored in JSON>",
  "confidence": <1-10>,
  "snippet": "<one-sentence summary>",
  "source_evaluation": {
    "authority": <1-10>,
    "recency": <1-10>,
    "accuracy": <1-10>,
    "bias": <1-10>,
    "relevance": <1-10>
  },
  "key_findings": "<key findings in markdown>",
  "analysis": "<analysis in markdown>",
  "gaps": "<gaps and recommendations in markdown>"
}
RESULT
```

## What the Script Does

- Routes to `web-results.json` (`source_type: web`) or `youtube-results.json` (`source_type: youtube`) within the research folder
- Uses file locking to safely handle concurrent writes from parallel agents
- Saves `content` + analysis to ChromaDB for `/ask-research` follow-up queries
- `content` is passed to the vector store only — it is NOT stored in the JSON results file

## Important Notes

- Vector store errors are non-fatal warnings and will NOT block the JSON write
- If the script exits with an error about missing fields, check that all required fields are present
