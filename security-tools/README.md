# Security Tools

The security tools plugin provides skills and agents to help evaluate system design and code from a security perspective. It covers code-level vulnerability detection, dependency auditing, and secure coding guidance — helping ensure your project is well-structured and secure throughout development.

The security review agent is designed to run proactively after completing significant features or code changes, while the dependency scanner can be invoked on demand to audit third-party packages for known vulnerabilities.

## Installation
1. Add the marketplace to Claude using the instructions in the project README
2. Add the plugin to claude code with `/plugin install security-tools@brennanmeadowcroft/claude-plugins`

It's also possible to install this within a codebase or repo so it's always available.  Within `.claude/settings.json`, add the following:
```
{
  "extraKnownMarketplaces": {
    "security-tools": {
      "source": { "source": "github", "repo": "brennanmeadowcroft/claude-plugins", "ref": "v1.0.0" }
    }
  },
  "enabledPlugins": {
    "security-tools@brennanmeadowcroft/claude-plugins": true
  }
}
```

## Configuration

Some skills require API keys for external scanning tools. These are resolved from a project-level config file or environment variables — keys are never passed directly to the assistant.

### Setting up `.claude-plugins.json`

Create a `.claude-plugins.json` file in your project root with the keys you need:

```json
{
  "aikido_api_key": "AIK_CI_your_key_here",
  "snyk_token": "your_snyk_token_here"
}
```

You only need to include the keys for the tools you use. For example, if you only use Aikido:

```json
{
  "aikido_api_key": "AIK_CI_your_key_here"
}
```

**Important:** This file contains secrets. Add it to your `.gitignore`:

```bash
echo '.claude-plugins.json' >> .gitignore
```

### Alternative: Environment variables

If you prefer not to use a config file, you can set the keys as environment variables instead:

- `AIKIDO_API_KEY` — for the Aikido Local Scanner
- `SNYK_TOKEN` — for the Snyk CLI

The resolution order is: config file first, then environment variable.

## Skills
| Skill                 | Description                                                                                                       |
| --------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `/scan-dependencies`  | Scans project dependencies for known vulnerabilities using Aikido (preferred) or Snyk. Suggests remediations.     |

## Agents
| Agent                  | Description                                                                                                                                   |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Security Code Reviewer | Performs static analysis style security review of code changes, focusing on hardcoded secrets, injection vulnerabilities, and OWASP patterns. Runs proactively after significant features are completed. |
