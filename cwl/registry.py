"""Project registry: a small JSON file with workspaces, tool probes and state.

Stored per user (never in the repository):
  Linux/macOS: ~/.local/state/codex-workspace-launcher/registry.json
  Windows:     %LOCALAPPDATA%/codex-workspace-launcher/registry.json
"""

from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

APP_NAME = "codex-workspace-launcher"
PROBE_TTL_SECONDS = 300.0


def state_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home())
        return Path(base) / APP_NAME
    base = os.environ.get(
        "XDG_STATE_HOME", str(Path.home() / ".local" / "state"))
    return Path(base) / APP_NAME


def registry_path() -> Path:
    return state_dir() / "registry.json"


def canonical_path(value: str | Path) -> str:
    return str(Path(value).expanduser().resolve(strict=False))


def registry_id_for_path(path: str | Path) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL,
                          "codex-workspace:" + canonical_path(path)))


def label_for_path(path: str | Path) -> str:
    name = Path(path).name
    words = name.replace("_", " ").replace("-", " ").strip()
    return words.title() or "Untitled project"


class Registry:
    """JSON registry: workspaces, cached tool probes, app state."""

    def __init__(self, path: str | None = None) -> None:
        self.path = Path(path) if path else registry_path()
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self.data: dict[str, Any] = {
                "schema": 1,
                "workspaces": {},
                "probes": {},
                "app_state": {},
            }
            return
        try:
            self.data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self.data = {"schema": 1, "workspaces": {}, "probes": {},
                         "app_state": {}}
        self.data.setdefault("workspaces", {})
        self.data.setdefault("probes", {})
        self.data.setdefault("app_state", {})

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2),
                       encoding="utf-8")
        os.replace(tmp, self.path)

    # -- workspaces ---------------------------------------------------------

    def list(self) -> list[dict]:
        rows = [w for w in self.data["workspaces"].values()
                if not w.get("archived")]
        rows.sort(key=lambda w: w.get("last_opened_at") or 0, reverse=True)
        return rows

    def get(self, wid: str) -> dict | None:
        row = self.data["workspaces"].get(wid)
        if row is not None:
            return row
        # Git-style short ids: a unique prefix of a workspace id works too.
        matches = [w for k, w in self.data["workspaces"].items()
                   if k.startswith(wid) and not w.get("archived")]
        return matches[0] if len(matches) == 1 else None

    def get_by_path(self, path: str | Path) -> dict | None:
        wid = registry_id_for_path(path)
        row = self.data["workspaces"].get(wid)
        if row is not None and not row.get("archived"):
            return row
        return None

    def upsert(self, path: str | Path, label: str | None = None) -> dict:
        p = canonical_path(path)
        wid = registry_id_for_path(p)
        row = self.data["workspaces"].get(wid)
        if row is None:
            row = {"id": wid, "path": p, "label": label or label_for_path(p),
                   "created_at": time.time(), "last_opened_at": None,
                   "last_tool_id": None, "last_mode_id": None,
                   "archived": False}
        else:
            row["path"] = p
            row["archived"] = False
            if label:
                row["label"] = label
        self.data["workspaces"][wid] = row
        self.save()
        return dict(row)

    def rename(self, wid: str, label: str) -> dict:
        row = self.get(wid)
        if row is None:
            raise KeyError(wid)
        row["label"] = label
        self.save()
        return dict(row)

    def archive(self, wid: str) -> None:
        row = self.get(wid)
        if row is None:
            raise KeyError(wid)
        row["archived"] = True
        self.save()

    def mark_opened(self, wid: str, tool_id: str, mode_id: str) -> None:
        row = self.data["workspaces"].get(wid)
        if row is None:
            return
        row["last_opened_at"] = time.time()
        row["last_tool_id"] = tool_id
        row["last_mode_id"] = mode_id
        self.data["app_state"]["last_workspace_id"] = wid
        self.data["app_state"]["last_tool_id"] = tool_id
        self.data["app_state"]["last_mode_id"] = mode_id
        self.save()

    # -- probe cache ---------------------------------------------------------

    def get_probe(self, tool_id: str) -> dict | None:
        hit = self.data["probes"].get(tool_id)
        if not hit:
            return None
        if time.time() - float(hit.get("checked_at", 0)) > PROBE_TTL_SECONDS:
            return None
        payload = hit.get("payload")
        if not isinstance(payload, dict):
            return None
        return payload

    def set_probe(self, tool_id: str, payload: dict) -> None:
        self.data["probes"][tool_id] = {
            "payload": payload, "checked_at": time.time()}
        self.save()

    # -- app state ------------------------------------------------------------

    def get_state(self, key: str, default: Any = None) -> Any:
        return self.data["app_state"].get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        self.data["app_state"][key] = value
        self.save()
