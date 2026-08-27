# UnrealBuildTool

## Target selection

Use each Target, Platform, or Configuration value explicitly provided by the user. Fill only missing values with the Development Editor defaults:

1. Inspect `.Target.cs` files for `TargetType.Editor`.
2. Prefer `<uproject stem>Editor`; otherwise use the only Editor target.
3. If multiple Editor targets remain, ask the user to choose.
4. Default Platform to `Win64`.
5. Default Configuration to `Development`.

Development Editor maps to `<EditorTarget> Win64 Development` on Windows.

## Command

```text
<Engine>\Build\BatchFiles\Build.bat <Target> <Platform> <Configuration> -Project="<Project>.uproject" -WaitMutex
```

## Sandbox compatibility

Reuse existing compatibility evidence for the same engine root, host, and sandbox policy. If none exists, try UBT in the sandbox once. If .NET runtime, toolchain, ACL, or sandbox access prevents startup, request approval to rerun the exact command outside the sandbox and reuse that result for later commands.

C++, Unreal Header Tool, compiler, or linker diagnostics are build failures, not sandbox incompatibility. Reassess compatibility when the engine root, host, or sandbox policy changes.

## Hot Reload

Do not use Hot Reload when the affected binary does not support `bAllowHotReload`.

Verify the current Unreal Editor log shows the rebuilt module loaded and a current `HotReload took` result or failure. Report this separately from the UnrealBuildTool result; a successful build alone does not prove Hot Reload succeeded.

## Closed-editor build

Run the command after Unreal Editor is closed.

## Results

For either UBT route, let UnrealBuildTool run Unreal Header Tool when generated code is out of date; do not invoke Unreal Header Tool directly. Report success only when the command exits with code zero and UnrealBuildTool reports `Result: Succeeded`.
