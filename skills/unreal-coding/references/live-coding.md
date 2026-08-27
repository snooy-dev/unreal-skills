# Live Coding

## Prerequisites

Both prerequisites are required:

- **Enable Live Coding** is enabled for the current Unreal Editor session.
- Unreal MCP is connected and exposes `CompileLiveCoding` from `LiveCodingToolset`.

If `CompileLiveCoding` is unavailable, ask the user to do one of the following:

- Start Unreal MCP or enable `LiveCodingToolset` until `CompileLiveCoding` is exposed.
- Disable **Enable Live Coding**, which enables the Hot Reload route.
- Press `Ctrl+Alt+F11` and provide the compile result and current Live Coding output.

Treat a manually run compile as user-reported unless its current result is independently verified.

## Compile

1. For changes requiring Object Reinstancing, confirm **Enable Reinstancing** is enabled and use `ReloadReinstancingCompleteDelegate` or `ReloadCompleteDelegate` to update retained pointers or invalidate caches. Otherwise use an Editor target build with Unreal Editor closed.
2. Invoke MCP `CompileLiveCoding` and wait for completion.
3. Report the returned `ELiveCodingCompileResult` and current compiler output. Count only `Success` or `NoChanges` with current output as success.

## Limitations

Constructor defaults defined in `.cpp` files do not update existing object instances. Recreate the affected instances or use a closed-editor build and restart when that runtime state must be validated.
