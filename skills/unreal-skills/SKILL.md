---
name: unreal-skills
description: Safely inspect, operate, automate, start, stop, and troubleshoot Unreal Editor projects across supported engine versions. Use for Unreal Engine .uproject work involving Unreal MCP connectivity or tools, editor actors/assets/levels, official Unreal Python Editor scripting, editor lifecycle, crashes, or Unreal error logs. Resolve the project's major.minor engine version before acting and load the matching version guidance; do not use hotfix versions as separate targets.
---

# Unreal Skills

Operate Unreal Editor through the project's supported native Unreal MCP integration. Treat MCP as the default control plane and the Unreal project as the source of truth.

## Resolve the project and version

1. Locate the `.uproject` from the user-provided path or current workspace. If more than one candidate exists, identify the intended project before acting.
2. Run `python <skill-path>/scripts/inspect_unreal_project.py <project-or-directory> --json` with an available Python 3.10+ interpreter.
3. Read `target_version` and load the matching `versions/<major.minor>/GUIDE.md`. Normalize hotfix releases to major.minor: `5.8.1` selects `versions/5.8/`.
4. Stop and report an unsupported version when the matching version directory is absent. Never silently use guidance for another engine version.

The resolver is read-only. If it cannot resolve a custom/GUID engine association automatically, inspect the registered engine installation or its `Engine/Build/Build.version`, then select the exact major.minor directory.

## Establish the control plane

1. Report the resolver's MCP configuration and plugin states before attempting editor mutations.
2. Select the configuration for the active client from `mcp_configs`: Codex uses `.codex/config.toml`; Claude Code uses the project-root `.mcp.json`. Treat a missing file, missing `unreal-mcp` entry, malformed URL, or explicitly disabled MCP server as an actionable configuration state. Tell the user what is missing or disabled.
3. Connect through Unreal MCP and use its tool-search workflow. Issue MCP calls serially; Unreal executes tool invocations on the game thread.
4. Do not bypass unavailable MCP with shell edits, UI automation, commandlets, direct asset-file operations, or Python execution unless the user explicitly requests or approves that bypass.
5. If MCP is unavailable, follow the selected version guide's connection triage. Distinguish configuration, server-not-started, editor-not-running/crashed, and client reconnect/restart cases.

## Perform editor work

- Inspect the current selection, assets, actors, level, and relevant settings before mutation.
- Keep actions within the user's requested scope. Prefer small, reversible operations and verify each meaningful state change through MCP.
- Start or close the editor only when requested or when necessary for an authorized Unreal task. Follow `references/editor-lifecycle-and-incidents.md`.
- Prefer official `unreal` Python APIs for editor scripting. Never manipulate `.uasset` or `.umap` files with generic filesystem APIs.
- Execute external or newly authored custom Python inside Unreal Editor only when the user explicitly requests it. If MCP cannot perform a task, explain the proposed Python bypass and obtain approval before execution.
- Do not use editor Python as gameplay/runtime scripting; it is editor-only.

## Handle incidents and logs

Always read `references/editor-lifecycle-and-incidents.md` before launching/stopping the editor, investigating a lost editor process, or handling a crash.

- On a suspected or confirmed crash, stop all editor work immediately. Do not restart the editor or retry the failing action.
- Read the crash report and relevant project/editor logs, identify the last operation, separate evidence from inference, and report the crash location and likely cause.
- Do not analyze warnings unless the user asks. A warning that directly blocks the requested operation may be reported as a blocker without broader warning analysis.
- Track encountered errors because they may be fatal. Put an `Errors` section last in the final response whenever errors were observed.

## References

- Load `versions/5.8/GUIDE.md` only when the resolved target is UE 5.8.
- Load `references/editor-lifecycle-and-incidents.md` for editor process control, connection-loss classification, crashes, and log reporting.
