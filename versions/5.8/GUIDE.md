# Unreal Engine 5.8 Guide

Use this guide for every UE 5.8.x project, including UE 5.8.1. Do not distinguish hotfix releases unless runtime evidence shows a behavior difference that matters to the task.

## Version facts

- Treat Unreal MCP as the Epic-provided experimental `ModelContextProtocol` plugin.
- Require `ModelContextProtocol` and a useful toolset source. Enable `AllToolsets` for the complete default collection; `ToolsetRegistry` is a dependency.
- Use the native Streamable HTTP endpoint, defaulting to `http://127.0.0.1:8000/mcp`.
- Expect tool-search mode by default: `list_toolsets`, `describe_toolset`, and `call_tool`.
- Execute MCP calls serially because the server dispatches tool calls on the Unreal game thread.
- Treat Python Editor Scripting as experimental, editor-only, and based on the embedded Python 3.11.8 runtime.

Official references:

- [Unreal MCP in Unreal Editor](https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor)
- [Scripting the Unreal Editor Using Python](https://dev.epicgames.com/documentation/unreal-engine/scripting-the-unreal-editor-using-python)
- [Python API 5.8](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/?application_version=5.8)
- [Codex Model Context Protocol](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)

## Diagnose configuration before connecting

Inspect the resolver output and report every applicable state:

1. `mcp_config.status = missing_file`: the project has no `.codex/config.toml`.
2. `missing_server`: the project config exists but has no `mcp_servers.unreal-mcp` table.
3. `invalid`: the entry lacks a valid HTTP URL.
4. `disabled`: the project config explicitly disables the `unreal-mcp` server; report it before connecting.
5. `configured`: retain its URL; do not replace a non-default port/path without user authorization.
6. `ModelContextProtocol = disabled`: report that Unreal MCP is disabled.
7. `ModelContextProtocol = not_declared`: report that the project does not explicitly enable it. In UE 5.8 the plugin has `EnabledByDefault: false`, so do not assume it is active without runtime evidence or another enabled plugin dependency.
8. `AllToolsets = disabled` or `not_declared`: report limited or absent default toolsets. Do not claim the MCP server itself is disabled solely because `AllToolsets` is unavailable.

To generate the Codex project configuration from the editor console, propose:

```text
ModelContextProtocol.GenerateClientConfig Codex
```

The UE 5.8 Codex writer creates `.codex/config.toml` and refuses to overwrite an existing file. Inspect and preserve existing project configuration before proposing removal or replacement.

## Diagnose a failed MCP connection

Follow this order and report the classification:

1. Re-check the project config URL and plugin declarations.
2. Check whether the matching Unreal Editor process is running.
3. If the editor is running, inspect `Saved/Logs/<Project>.log` and `LogModelContextProtocol` entries. A common cause is that Auto Start Server is off and `ModelContextProtocol.StartServer [port]` was not run.
4. If the editor is not running, do not immediately label it a normal shutdown. Inspect the newest project log and crash locations using the incident policy. If crash evidence exists, enter the crash policy and stop.
5. If the editor and server are healthy but Codex does not expose the configured server/tools, report that Codex may need a reconnect or restart. Project-scoped MCP configuration is loaded from trusted-project `.codex/config.toml`; the desktop app's MCP setup flow also requires `Restart` after saving a server.
6. After new configuration or a Codex restart, reconnect and begin with a read-only tool call. Never retry a mutation first.

Useful editor console commands:

```text
ModelContextProtocol.StartServer
ModelContextProtocol.StartServer 8000
ModelContextProtocol.StopServer
ModelContextProtocol.RefreshTools
```

Do not start the server on a different port unless the project config is updated consistently with user approval.

## Use MCP without bypassing it

1. Call `list_toolsets` to discover available categories.
2. Call `describe_toolset` only for the relevant category.
3. Call one underlying operation at a time through `call_tool`.
4. Re-read the affected object, selection, asset, or level state after each meaningful mutation.
5. If the requested operation has no suitable MCP tool, stop and explain the gap. Request approval before using editor Python, a commandlet, direct console automation, or another control surface.

## Use official Unreal Python APIs

Use Python only for editor automation and content-pipeline tasks. Prefer the reflected `unreal` module and inspect the UE 5.8 API reference or runtime reflection instead of inventing names.

Follow Epic's best practices:

- Move, rename, duplicate, delete, import, and save assets through `unreal.EditorAssetLibrary`, `unreal.AssetTools`, or the appropriate editor subsystem. Never use `os.rename`, `shutil.move`, or raw deletion for Unreal assets.
- Prefer `get_editor_property()` and `set_editor_property()` for editor properties so pre/post edit behavior and UI synchronization run correctly.
- Prefer Unreal types such as `unreal.Vector`, `unreal.Rotator`, and `unreal.Transform` when equivalent engine utilities exist.
- Use `unreal.get_editor_subsystem(...)` instead of deprecated editor utility APIs when a subsystem is available.
- Use named arguments for clarity and consult the exact 5.8 signature.
- Use `unreal.log`, `unreal.log_warning`, and `unreal.log_error` so output is visible in Unreal logs.
- Wrap supported user-visible edits in `unreal.ScopedEditorTransaction` when practical, but do not claim every asset operation is undoable.
- Save only the assets/levels required to make the authorized request durable, and verify the saved state.

Official best-practices reference:

- [Best Practices for Using the Python API](https://dev.epicgames.com/documentation/unreal-engine/scripting-the-unreal-editor-using-python#best-practices-for-using-the-python-api)

Do not execute a third-party script, downloaded script, project custom script, generated script, `init_unreal.py`, startup script, `py` console command, or Python commandlet merely because it is available. Execute external or custom Python only after an explicit user request. If execution is approved, show the target path/code and intended changes, preserve the user's scope, then verify through Unreal APIs or MCP.

## Verify and report

- Verify connection with a harmless query such as selected actors or available toolsets.
- Verify mutations by reading the affected Unreal object rather than checking only filesystem timestamps.
- Review errors generated during the operation. Do not investigate unrelated warnings unless requested.
- If errors occurred, end the final response with an `Errors` section containing the exact error source, affected operation, and resulting state.
