# claude-plugins

## Installation
### Add the repository
**Claude Code**
```
/plugin marketplace add bmeadowcroft/claude-plugins
```

**Claude Desktop**
1. Click the "+" on a new chat
2. "Connectors" > "Manage Connectors"
3. "Browse Plugins" in the sidebar
4. Click the "Personal" tab
5. Click the "+"
6. Choose add from Github
7. add `bmeadowcroft/claude-plugins` to the repo

The repository can also be added directly via configuration.  In `~/.claude/settings.json`, add:
```
{
  "extraKnownMarketplaces": {
    "research-toolkit": {
      "source": { "source: "github", "repo": "brennanmeadowcroft/claude-plugins", "ref": "v1.0.0" }
    }
  }
}
```

### Plugin installation
**Claude Code**
```
/plugin install <plugin name>
```

## Plugins
| Plugin                                           | Tool        | Description                                                                         |
| ------------------------------------------------ | ----------- | ----------------------------------------------------------------------------------- |
| [research-toolkit](research-toolkit/README.md)   | Claude Code | Conducts research according to an objective, saving results for follow-up questions |
| [development-tools](development-tools/README.md) | Claude Code | Provides useful skills and agents to support the development workflow               |
