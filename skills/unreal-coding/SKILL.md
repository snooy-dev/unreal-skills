---
name: unreal-coding
description: Validate Unreal Engine C++ changes on Windows through Live Coding, Hot Reload, or a closed-editor UnrealBuildTool build.
---

# Unreal Coding

After changing Unreal Engine C++ code, inspect the target Unreal Editor process and its current compilation method before choosing one validation path.

## Select a path

1. If the change requires a closed-editor build, or Unreal Editor is not running, read the **Closed-editor build** section of [references/unreal-build-tool.md](references/unreal-build-tool.md).
2. If Unreal Editor is running and **Enable Live Coding** is enabled:
   - Read [references/live-coding.md](references/live-coding.md), which enforces the Unreal MCP prerequisite.
3. If Unreal Editor is running and **Enable Live Coding** is disabled, read the **Hot Reload** section of [references/unreal-build-tool.md](references/unreal-build-tool.md). Unreal MCP is not required.

Missing Unreal MCP while **Enable Live Coding** remains enabled is a blocked in-editor iteration state, not a reason to select a closed-editor build.

Do not choose a closed-editor build solely because a `.Build.cs` file changed or a C++ class was added. UnrealBuildTool invalidates its makefile when `ModuleRules` files or source files change, and Live Coding officially supports newly added C++ classes.

### Closed-editor conditions

Build the Editor target with Unreal Editor closed when process startup state must be rebuilt:

- Adding or removing a module or plugin, or changing its `Type`, `LoadingPhase`, enablement, or target membership.
- `TargetRules` changes that alter target composition, `LinkType`, or `BuildEnvironment`.
- Any change for which UnrealBuildTool, Live Coding, or Hot Reload explicitly requires an editor restart.

## Shared boundaries

- Do not close the editor or change its Live Coding setting without user approval.
- Compilation success does not prove that existing objects or modules reflect new startup state.
