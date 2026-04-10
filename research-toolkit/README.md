# Research Toolkit

The research toolkit plugin provides a research assistant that does research according to an objective and provides a report.  It works best with research projects within a project that has similar research objectives because the vectordb is maintained at a project level.  If working on multiple projects, add the plugin to multiple projects.

Claude's own research flag works very well and provides a comprehensive report.  However, while those sources are cited, they are not saved and follow-up questions frequently require additional research. The research toolkit creates markdown reports that could be used by Claude Code during planning sessions.  It also saves quality content to a local vector store to answer follow-up questions.  

Research memory is saved across all research projects *within a project* so follow-up questions can expand beyond a single set of research.

**This plugin requires `yt-dlp` to be installed for YouTube transcription**

## Installation
1. Add the marketplace to Claude using the instructions in the project README
2. Add the plugin to claude code with `/plugin install research-toolkit@brennanmeadowcroft/claude-plugins`

It's also possible to install this within a codebase or repo so it's always available.  Within `.claude/settings.json`, add the following:
```
{
  "extraKnownMarketplaces": {
    "research-toolkit": {
      "source": { "source: "github", "repo": "brennanmeadowcroft/claude-plugins", "ref": "v1.0.0" }
    }
  },
  "enabledPlugins": {
    "research-toolkit@brennanmeadowcroft/claude-plugins": true
  }
}
```

## Bootstrapping
The vector store is initialized automatically on your first prompt after installing the plugin (via a `UserPromptSubmit` hook). It also performs a health check on every subsequent session start — if something is wrong, you'll see an error before any work begins.

You can also initialize manually with `/init-vectordb`, which is useful if the store gets corrupted and needs a full rebuild.

The store is created as a `.research-memory/` folder next to the `.claude/` directory in your project root.

## Cloud Sync (Nextcloud, Dropbox, iCloud, etc.)

**Do not sync `.research-memory/` with a cloud storage service.**

The vector store uses ChromaDB, which stores data as SQLite databases and binary HNSW index files. These are not safe to sync:

- **Corruption risk**: Nextcloud (or similar) can read a partially-written file mid-write, producing a silently corrupted database that still appears to open but returns wrong results or errors later
- **Binary conflicts are unrecoverable**: If two devices both modify the store and a "conflicted copy" is created, there is no merge — you just lose data
- **The store is intentionally device-local**: Research results are stored per-device. Re-run `/init-vectordb` (or just open Claude Code) on each machine to initialize a fresh store

**If your project lives inside a synced folder, exclude `.research-memory` from sync:**

- **Nextcloud**: Settings → Ignored Files → add `.research-memory`
- **Dropbox**: Add `.research-memory` to your [ignored paths](https://help.dropbox.com/sync/ignored-files)
- **iCloud Drive**: Prefix with a `.nosync` extension or move the store outside the iCloud folder (not supported natively — consider keeping your project outside iCloud)

The `.gitignore` entry for `.research-memory/` is added automatically on init.

## Usage
### Research
```
/deep-research what are emerging trends in the use of agents and skills in claude code
```
The skill with ask for any clarification needed and confirm the research objective before proceeding. All searched resources are saved in the folder under `search-results.json` or `youtube-results.json` including the URL, a quality rating, summary and key takeaways.


```
/ask-research what are the biggest obstacles to setting up agents?
```
The skill queries the vector store and returns a result with citations


## Skills
| Skill                   | Description                                                                                                                 |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `/deep-research`        | Researches according to an objective and returns a markdown report                                                          |
| `/ask-research`         | Queries the local vector store for additional questions                                                                     |
| `/init-vectordb`        | Initializes the research memory and installs ChromaDB                                                                       |
| `/save-research-result` | Used by the research analyst agents, it saves each result to the research memory. **Not intended to be called by the user** |
| `/transcribe-youtube`   | Transcribes YouTube videos using yt-dlp — no API keys needed.                                                               |

## Agents
| Agent                    | Description                                                                                    |
| ------------------------ | ---------------------------------------------------------------------------------------------- |
| Web Research Analyst     | Conducts multiple searches and evaluates the results. Will follow additional links.            |
| Youtube Research Analyst | Conducts multiple searches on Youtube, transcribes the videos and processes the transcriptions |

