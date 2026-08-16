# Unreal Skills

Version-aware Unreal Editor automation for Codex and Claude Code. The repository contains one shared Agent Skill plus native plugin manifests for both clients.

The initial release targets Unreal Engine 5.8.x. Hotfix versions share the same guide, so UE 5.8.1 resolves to `versions/5.8`.

## Features

- Uses Epic's native Unreal MCP integration as the default editor control plane.
- Supports Codex `.codex/config.toml` and Claude Code `.mcp.json` project configurations.
- Inspects the project engine version, plugin declarations, editor process, and recent crash or log artifacts without modifying the project.
- Prefers official Unreal Python Editor APIs when an approved MCP fallback is required.
- Stops editor work on a suspected crash and requires crash-report and log inspection before recovery.

## Repository layout

```text
unreal-skills/
├── .codex-plugin/
│   └── plugin.json
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── unreal-skills/
        ├── SKILL.md
        ├── agents/
        ├── references/
        ├── scripts/
        └── versions/
```

The skill under `skills/unreal-skills/` is shared by both clients. The two plugin manifests contain client-specific package metadata only.

## Install the skill

Clone the repository first:

```powershell
git clone https://github.com/snooy-dev/unreal-skills.git
Set-Location unreal-skills
```

### Codex

Install for the current user:

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills\unreal-skills" | Out-Null
Copy-Item -Recurse -Force ".\skills\unreal-skills\*" "$HOME\.agents\skills\unreal-skills"
```

Install for one project:

```powershell
$ProjectRoot = "D:\path\to\your-unreal-project"
New-Item -ItemType Directory -Force "$ProjectRoot\.agents\skills\unreal-skills" | Out-Null
Copy-Item -Recurse -Force ".\skills\unreal-skills\*" "$ProjectRoot\.agents\skills\unreal-skills"
```

Start a new Codex session after installation if the skill does not appear immediately.

### Claude Code

Install for the current user:

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills\unreal-skills" | Out-Null
Copy-Item -Recurse -Force ".\skills\unreal-skills\*" "$HOME\.claude\skills\unreal-skills"
```

Install for one project:

```powershell
$ProjectRoot = "D:\path\to\your-unreal-project"
New-Item -ItemType Directory -Force "$ProjectRoot\.claude\skills\unreal-skills" | Out-Null
Copy-Item -Recurse -Force ".\skills\unreal-skills\*" "$ProjectRoot\.claude\skills\unreal-skills"
```

For local plugin development, load the repository directly:

```powershell
claude --plugin-dir "D:\path\to\unreal-skills"
```

Plugin marketplace installation is not published yet. The included manifests are ready for local validation and future marketplace packaging.

## Configure Unreal MCP

In Unreal Editor 5.8, enable these plugins:

- Unreal MCP (`ModelContextProtocol`)
- All Toolsets (`AllToolsets`)
- Toolset Registry (`ToolsetRegistry`, enabled as a dependency)

Generate the project configuration from the editor console:

```text
ModelContextProtocol.GenerateClientConfig Codex
ModelContextProtocol.GenerateClientConfig ClaudeCode
```

To configure both clients at once:

```text
ModelContextProtocol.GenerateClientConfig All
```

Codex reads `.codex/config.toml`. Claude Code reads `.mcp.json` from the project root. Launch the selected client from that project root.

## Inspect a project

The bundled inspector is read-only and requires Python 3.10 or newer:

```powershell
python .\skills\unreal-skills\scripts\inspect_unreal_project.py "D:\path\to\Project.uproject" --json
```

Its output includes the resolved engine version, selected guide, Unreal plugin declarations, both client MCP configurations, running editor processes, and recent crash or log artifacts.

## Validate

Validate the Claude Code plugin:

```powershell
claude plugin validate .
```

The Codex plugin and shared skill follow the official plugin and Agent Skills layouts. This repository is also checked with the validators bundled with Codex's `plugin-creator` and `skill-creator` skills before release.

## References

- [Unreal MCP in Unreal Editor](https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor)
- [Unreal Python Editor scripting](https://dev.epicgames.com/documentation/unreal-engine/scripting-the-unreal-editor-using-python)
- [Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Codex plugins](https://developers.openai.com/plugins/build/plugins)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Claude Code plugins](https://code.claude.com/docs/en/plugins)
