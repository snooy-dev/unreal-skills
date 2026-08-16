# Editor Lifecycle and Incident Policy

## Start the editor safely

1. Resolve the `.uproject` and its registered engine installation before launching.
2. Check running `UnrealEditor` processes and their command lines. Reuse the process that already hosts the same project; do not launch a duplicate.
3. Check the latest project log for an unresolved crash from the preceding session. If crash evidence exists, follow the crash policy before launching.
4. Launch the matching engine's `UnrealEditor` with the explicit `.uproject` path. Keep the window visible for user interaction.
5. Wait for the project log to show editor initialization completion, then confirm the MCP server log and perform a read-only MCP query before any mutation.
6. If startup fails, stop and report the process exit code plus the relevant fatal/error log lines.

Starting the editor is allowed only when the user requested it or it is a necessary, normal step of an already authorized Unreal task. Announce the launch when it is performed implicitly for that task.

## Close the editor safely

1. Stop issuing MCP mutations and wait for the current serial call to finish.
2. Determine whether the requested work has unsaved assets or levels. Save only when authorized by the task or explicitly requested; otherwise tell the user what remains unsaved.
3. Request a normal editor exit through the available editor/MCP control surface.
4. Wait for the process to exit and inspect the tail of the project log for shutdown errors.
5. Never force-terminate `UnrealEditor` merely because normal exit is slow. If it is unresponsive, report the state and obtain explicit approval before force termination because unsaved work and recovery state may be lost.

## Classify connection loss

When a working MCP connection disappears:

1. Stop mutations.
2. Check whether the editor process still exists.
3. If it exists, inspect `LogModelContextProtocol` for a stopped server, bind failure, invalid path, or port conflict.
4. If it does not exist, compare process disappearance time with project log and crash-report timestamps.
5. Treat `Fatal error`, `Unhandled Exception`, an ensure promoted to fatal, a crash folder, or CrashReportClient activity as crash evidence.
6. If no crash evidence exists and the log shows orderly shutdown, report that the editor was closed.
7. If the editor/server is healthy but the active client lacks tools after config changes, report that a client reconnect or restart may be required.

## Crash policy

On suspected or confirmed crash:

1. Immediately stop all editor, MCP, Python, build, and retry actions associated with the task.
2. Do not relaunch the editor, restore a session, modify recovery files, submit a crash report, or repeat the last operation.
3. Record the last requested operation and the last successful verification.
4. Inspect the newest relevant artifacts:
   - `<Project>/Saved/Crashes/`
   - `%LOCALAPPDATA%/CrashReportClient/Saved/Crashes/`
   - `<Project>/Saved/Logs/<Project>.log`
   - Crash context XML, minidump metadata, and call stack text when present
5. Extract the crash time, exception/fatal message, top relevant call-stack frames, involved module/plugin, and log events immediately before the failure.
6. Distinguish direct evidence from inference. State `unknown` when artifacts are insufficient.
7. Report the likely crash location and cause to the user, along with what was and was not saved. Ask for direction before any restart or remediation.

Do not delete or alter crash artifacts.

## Warning and error policy

- Do not analyze, summarize, or chase warnings unless the user asks. Ignore unrelated warning noise.
- If a warning directly prevents the requested operation, report only that blocker and its immediate effect.
- Treat `Error`, `Fatal`, assertion failures, failed saves, package corruption, and failed MCP mutations as errors that require tracking.
- Stop immediately for fatal errors, crashes, corrupted-state indications, or errors that make continued mutation unsafe. For recoverable operation errors, preserve state, verify the result, and avoid unrelated retries.
- Whenever any error was observed, make `Errors` the final section of the final response. Include the source, exact affected operation, whether the operation committed, and current editor/project state.
