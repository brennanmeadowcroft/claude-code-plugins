---
name: scan-dependencies
description: Scans project dependencies for known vulnerabilities using Aikido Security (preferred) or Snyk as a fallback. Indicated when the user asks to scan, audit, or check dependencies for security issues.
---

# Scan Dependencies

## Required Inputs

Before starting, collect the following from the user:

- **Project Path** - the root directory of the project to scan. Defaults to the current working directory.
- **Severity Threshold** - Optional minimum severity to fail on: `low`, `medium`, `high`, or `critical`. Defaults to `high`.
Do not proceed until the project path is confirmed.

## Prerequisites

This skill requires one of the following tools to be available:

1. **Aikido Local Scanner** (preferred) - The `aikido-local-scanner` binary or the Docker image `aikidosecurity/local-scanner`. Requires an API key configured in `.claude-plugins.json` or the `AIKIDO_API_KEY` environment variable.
2. **Snyk CLI** (fallback) - The `snyk` CLI installed via `npm install -g snyk`. Requires a token configured in `.claude-plugins.json` or the `SNYK_TOKEN` environment variable.

## Steps to follow

### 1. Detect the scanning tool

Check which scanner is available in the following priority order:

1. Run `which aikido-local-scanner` to check for the Aikido binary.
2. If not found, check if Docker is available (`which docker`) for the Aikido Docker image.
3. If neither Aikido option is available, run `which snyk` to check for Snyk.
4. If no scanner is found, inform the user and provide installation instructions for both tools:
   - **Aikido**: Download the binary from the [Aikido Local Scanner setup page](https://app.aikido.dev/settings/integrations/localscan) or use Docker: `docker pull aikidosecurity/local-scanner`
   - **Snyk**: `npm install -g snyk && snyk auth`

### 2. Identify the project

1. Read the project directory to understand the project type and identify dependency manifests (e.g. `package.json`, `requirements.txt`, `go.mod`, `pom.xml`, `Gemfile`, `Cargo.toml`, `composer.json`).
2. Confirm the project path and detected package manager(s) with the user.

### 3. Resolve the API key

API keys are never accepted as direct input. Resolve the key for the selected scanner using this hierarchy:

1. **Config file** - Look for `.claude-plugins.json` in the project root and read the appropriate field:
   ```json
   {
     "aikido_api_key": "AIK_CI_xxx",
     "snyk_token": "..."
   }
   ```
2. **Environment variable** - Check for `AIKIDO_API_KEY` (Aikido) or `SNYK_TOKEN` (Snyk).

If the key cannot be resolved from either source, **stop and notify the user**. Do not ask the user to provide the key directly. Instead, instruct them to either:

- Add the key to `.claude-plugins.json` in their project root:
  ```bash
  echo '{ "aikido_api_key": "YOUR_KEY_HERE" }' > .claude-plugins.json
  ```
  and ensure `.claude-plugins.json` is listed in `.gitignore`.
- Or set the appropriate environment variable (`AIKIDO_API_KEY` or `SNYK_TOKEN`).

### 4. Run the dependency scan

**If using Aikido Local Scanner (binary):**

```bash
aikido-local-scanner scan {project-path} \
  --apikey {aikido-api-key} \
  --repositoryname {repo-name} \
  --branchname {branch-name} \
  --scan-types dependencies \
  --fail-on {severity-threshold}
```

**If using Aikido via Docker:**

```bash
docker run --rm -v "{project-path}:/app" aikidosecurity/local-scanner scan /app \
  --apikey {aikido-api-key} \
  --repositoryname {repo-name} \
  --branchname {branch-name} \
  --scan-types dependencies \
  --fail-on {severity-threshold}
```

**If using Snyk:**

```bash
snyk test {project-path} --severity-threshold={severity-threshold}
```

For monorepos or projects with multiple manifest files, run the scan against each detected manifest location using `--file` (Snyk) or `--exclude` to skip irrelevant paths.

### 5. Analyze and report results

1. Parse the scan output and organize findings by severity (critical, high, medium, low).
2. For each vulnerability found, summarize:
   - **Package name** and installed version
   - **Vulnerability ID** (CVE or scanner-specific ID)
   - **Severity** level
   - **Fixed version** (if available)
   - **Brief description** of the vulnerability
3. Group results into:
   - **Action required** - vulnerabilities at or above the severity threshold with available fixes
   - **Review recommended** - vulnerabilities below the threshold or without available fixes
   - **Informational** - low-severity findings or advisories

### 6. Suggest remediations

For vulnerabilities with known fixes:

1. List the specific package upgrades needed (e.g. `package@current -> package@fixed`).
2. If the user agrees, apply the fixes using the appropriate package manager:
   - **npm/yarn/pnpm**: Update `package.json` and run the install command
   - **pip/poetry**: Update `requirements.txt` or `pyproject.toml`
   - **Other**: Provide the manual update instructions
3. After applying fixes, re-run the scan to verify the vulnerabilities are resolved.

### 7. Report back

Provide a summary to the user including:

- Total dependencies scanned
- Number of vulnerabilities found by severity
- Remediations applied (if any)
- Remaining vulnerabilities that require manual review
- Recommendation for integrating the scan into CI/CD if not already present
