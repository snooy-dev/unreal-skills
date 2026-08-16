# Unreal Skills

Unreal Editor skills for Codex and Claude Code.

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
        └── versions/
```

The skill under `skills/unreal-skills/` is shared by both clients. The two plugin manifests contain client-specific package metadata only.

## Install for an Unreal project

Download or clone this repository, then locate the complete `skills/unreal-skills` folder. Copy that folder without changing its contents into the skill directory for the client you use.

| Client | Project skill location |
|---|---|
| Codex | `<UnrealProjectRoot>/.agents/skills/unreal-skills/` |
| Claude Code | `<UnrealProjectRoot>/.claude/skills/unreal-skills/` |

For Codex, the finished project layout should contain:

```text
<UnrealProjectRoot>/
├── <ProjectName>.uproject
└── .agents/
    └── skills/
        └── unreal-skills/
            ├── SKILL.md
            ├── agents/
            ├── references/
            └── versions/
```

For Claude Code, use the same `unreal-skills` folder under `.claude/skills/`:

```text
<UnrealProjectRoot>/
├── <ProjectName>.uproject
└── .claude/
    └── skills/
        └── unreal-skills/
            ├── SKILL.md
            ├── agents/
            ├── references/
            └── versions/
```

To support both clients in the same Unreal project, copy the folder to both locations. The contents are identical; only the client-specific parent directory differs.

Start Codex or Claude Code from the Unreal project root. If a newly created top-level skill directory is not detected in the current session, start a new session or restart the client. Do not copy the repository-level `.codex-plugin` or `.claude-plugin` folders into the project skill directory; they are package manifests for plugin distribution.

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

To configure all clients at once:

```text
ModelContextProtocol.GenerateClientConfig All
```

Codex reads `.codex/config.toml`. Claude Code reads `.mcp.json` from the project root. Launch the selected client from that project root.

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
