#!/usr/bin/env python3
"""Read-only Unreal project, version, MCP, plugin, process, and crash inspection."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 compatibility for external Codex runtimes.
    tomllib = None  # type: ignore[assignment]


class InspectionError(RuntimeError):
    """Raised when project or engine resolution is ambiguous or unsupported."""


@dataclass(frozen=True)
class EngineVersion:
    major: int
    minor: int
    patch: int | None = None

    @property
    def target(self) -> str:
        return f"{self.major}.{self.minor}"

    @property
    def full(self) -> str:
        if self.patch is None:
            return self.target
        return f"{self.target}.{self.patch}"


def find_project(candidate: Path) -> Path:
    candidate = candidate.expanduser().resolve()
    if candidate.is_file():
        if candidate.suffix.lower() != ".uproject":
            raise InspectionError(f"Not a .uproject file: {candidate}")
        return candidate
    if not candidate.exists():
        raise InspectionError(f"Path does not exist: {candidate}")

    current = candidate
    while True:
        projects = sorted(current.glob("*.uproject"))
        if len(projects) == 1:
            return projects[0].resolve()
        if len(projects) > 1:
            names = ", ".join(project.name for project in projects)
            raise InspectionError(f"Multiple .uproject files in {current}: {names}")
        if current.parent == current:
            break
        current = current.parent
    raise InspectionError(f"No .uproject found at or above: {candidate}")


def parse_numeric_version(value: str) -> EngineVersion | None:
    match = re.fullmatch(r"\s*(\d+)\.(\d+)(?:\.(\d+))?\s*", value)
    if not match:
        return None
    patch = int(match.group(3)) if match.group(3) is not None else None
    return EngineVersion(int(match.group(1)), int(match.group(2)), patch)


def read_build_version(engine_root: Path) -> EngineVersion | None:
    build_file = engine_root / "Engine" / "Build" / "Build.version"
    if not build_file.is_file():
        return None
    try:
        data = json.loads(build_file.read_text(encoding="utf-8-sig"))
        return EngineVersion(
            int(data["MajorVersion"]),
            int(data["MinorVersion"]),
            int(data["PatchVersion"]),
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def windows_registered_engine(association: str) -> Path | None:
    if os.name != "nt":
        return None
    try:
        import winreg
    except ImportError:
        return None

    queries: list[tuple[Any, str, str]] = [
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Epic Games\Unreal Engine\Builds", association),
        (
            winreg.HKEY_LOCAL_MACHINE,
            rf"SOFTWARE\EpicGames\Unreal Engine\{association}",
            "InstalledDirectory",
        ),
    ]
    for hive, key_name, value_name in queries:
        try:
            with winreg.OpenKey(hive, key_name) as key:
                value, _ = winreg.QueryValueEx(key, value_name)
            path = Path(os.path.expandvars(str(value))).expanduser().resolve()
            if path.exists():
                return path
        except OSError:
            continue
    return None


def epic_launcher_engine(version: EngineVersion | None) -> Path | None:
    if os.name != "nt" or version is None:
        return None
    manifest_root = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "Epic" / "EpicGamesLauncher" / "Data" / "Manifests"
    if not manifest_root.is_dir():
        return None
    expected_app = f"UE_{version.target}"
    try:
        manifests = manifest_root.glob("*.item")
    except OSError:
        return None
    for manifest in manifests:
        try:
            data = json.loads(manifest.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("AppName") != expected_app:
            continue
        location = data.get("InstallLocation")
        if isinstance(location, str):
            path = Path(os.path.expandvars(location)).expanduser().resolve()
            if path.exists():
                return path
    return None


def resolve_engine(association: str, engine_override: Path | None) -> tuple[EngineVersion, Path | None]:
    if engine_override is not None:
        engine_root = engine_override.expanduser().resolve()
        version = read_build_version(engine_root)
        if version is None:
            raise InspectionError(f"Cannot read Engine/Build/Build.version under {engine_root}")
        return version, engine_root

    numeric = parse_numeric_version(association)
    registered = windows_registered_engine(association)
    if registered is not None:
        build_version = read_build_version(registered)
        if build_version is not None:
            return build_version, registered
    launcher_engine = epic_launcher_engine(numeric)
    if launcher_engine is not None:
        build_version = read_build_version(launcher_engine)
        if build_version is not None:
            return build_version, launcher_engine
    if numeric is not None:
        return numeric, launcher_engine
    raise InspectionError(
        "Cannot resolve EngineAssociation. Supply --engine-root for a custom or unregistered engine build."
    )


def plugin_states(project_data: dict[str, Any]) -> dict[str, str]:
    entries = {
        str(item.get("Name")): bool(item.get("Enabled", False))
        for item in project_data.get("Plugins", [])
        if isinstance(item, dict) and item.get("Name")
    }
    return {
        name: ("enabled" if entries[name] else "disabled") if name in entries else "not_declared"
        for name in ("ModelContextProtocol", "AllToolsets", "ToolsetRegistry", "PythonScriptPlugin")
    }


def fallback_mcp_config(config_path: Path) -> dict[str, Any] | None:
    """Parse the small generated MCP table when stdlib tomllib is unavailable."""
    try:
        lines = config_path.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return None
    section_pattern = re.compile(
        r'^\s*\[\s*(?:"mcp_servers"|mcp_servers)\s*\.\s*(?:"unreal-mcp"|unreal-mcp)\s*\]\s*$'
    )
    in_server = False
    values: dict[str, Any] = {}
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("["):
            in_server = bool(section_pattern.fullmatch(stripped))
            continue
        if not in_server or not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, raw_value = (part.strip() for part in stripped.split("=", 1))
        if key == "url" and len(raw_value) >= 2 and raw_value[0] == raw_value[-1] and raw_value[0] in "\"'":
            values["url"] = raw_value[1:-1]
        elif key == "enabled" and raw_value.lower() in ("true", "false"):
            values["enabled"] = raw_value.lower() == "true"
    return values if in_server or values else None


def inspect_mcp_config(project_root: Path) -> dict[str, Any]:
    config_path = project_root / ".codex" / "config.toml"
    result: dict[str, Any] = {"path": str(config_path), "status": "missing_file", "url": None}
    if not config_path.is_file():
        return result
    if tomllib is None:
        server = fallback_mcp_config(config_path)
    else:
        try:
            with config_path.open("rb") as handle:
                config = tomllib.load(handle)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            result.update(status="invalid", error=str(exc))
            return result
        servers = config.get("mcp_servers")
        server = servers.get("unreal-mcp") if isinstance(servers, dict) else None
    if not isinstance(server, dict):
        result["status"] = "missing_server"
        return result
    url = server.get("url")
    if not isinstance(url, str) or not re.fullmatch(r"https?://[^\s]+", url):
        result.update(status="invalid", error="mcp_servers.unreal-mcp.url is missing or invalid")
        return result
    enabled = server.get("enabled", True)
    result.update(status="configured" if enabled is not False else "disabled", url=url, enabled=enabled)
    return result


def running_editor_processes() -> list[dict[str, Any]]:
    if os.name != "nt":
        return []
    try:
        completed = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq UnrealEditor.exe", "/FO", "CSV", "/NH"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    processes: list[dict[str, Any]] = []
    for row in csv.reader(completed.stdout.splitlines()):
        if len(row) >= 2 and row[0].lower() == "unrealeditor.exe":
            try:
                pid: int | str = int(row[1])
            except ValueError:
                pid = row[1]
            processes.append({"name": row[0], "pid": pid})
    return processes


def newest_artifacts(paths: list[Path], limit: int = 5) -> list[dict[str, Any]]:
    candidates: list[Path] = []
    for path in paths:
        if path.is_file():
            candidates.append(path)
        elif path.is_dir():
            try:
                candidates.extend(item for item in path.iterdir() if item.is_file() or item.is_dir())
            except OSError:
                continue
    ranked: list[tuple[float, Path]] = []
    for item in candidates:
        try:
            ranked.append((item.stat().st_mtime, item))
        except OSError:
            continue
    ranked.sort(key=lambda entry: entry[0], reverse=True)
    return [
        {
            "path": str(path.resolve()),
            "modified_utc": datetime.fromtimestamp(timestamp, timezone.utc).isoformat(),
        }
        for timestamp, path in ranked[:limit]
    ]


def inspect(args: argparse.Namespace) -> dict[str, Any]:
    project_file = find_project(Path(args.project))
    try:
        project_data = json.loads(project_file.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InspectionError(f"Cannot read project descriptor {project_file}: {exc}") from exc

    association = str(project_data.get("EngineAssociation", "")).strip()
    if not association and args.engine_root is None:
        raise InspectionError("Project has no EngineAssociation; supply --engine-root")
    version, engine_root = resolve_engine(
        association,
        Path(args.engine_root) if args.engine_root else None,
    )

    skills_root = Path(args.skills_root).expanduser().resolve()
    version_directory = skills_root / "versions" / version.target
    local_crash_root = Path(os.environ.get("LOCALAPPDATA", "")) / "CrashReportClient" / "Saved" / "Crashes"
    project_root = project_file.parent
    artifacts = newest_artifacts(
        [
            project_root / "Saved" / "Crashes",
            project_root / "Saved" / "Logs",
            local_crash_root,
        ]
    )

    return {
        "project_file": str(project_file),
        "project_root": str(project_root),
        "engine_association": association,
        "engine_root": str(engine_root) if engine_root else None,
        "engine_version": version.full,
        "target_version": version.target,
        "version_directory": str(version_directory),
        "version_supported": version_directory.is_dir(),
        "plugins": plugin_states(project_data),
        "mcp_config": inspect_mcp_config(project_root),
        "editor_processes": running_editor_processes(),
        "recent_log_or_crash_artifacts": artifacts,
    }


def build_parser() -> argparse.ArgumentParser:
    script_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".", help=".uproject file or directory within a project")
    parser.add_argument("--engine-root", help="Explicit Unreal Engine installation/source root")
    parser.add_argument("--skills-root", default=str(script_root), help="Root directory containing versions/")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = inspect(args)
    except InspectionError as exc:
        if args.json:
            print(json.dumps({"error": str(exc)}, indent=2, ensure_ascii=False))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")
    return 0 if result["version_supported"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
