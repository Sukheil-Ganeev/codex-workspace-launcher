"""Interactive pickers: a local web page (default) and a terminal fallback.

The web picker serves a small page on 127.0.0.1 with a random token in the
URL (so other websites cannot trigger launches). The page shows projects,
tools and modes; launching is a POST that the server validates and executes.
The server shuts itself down shortly after the page is closed (heartbeat).
"""

from __future__ import annotations

import http.server
import json
import secrets
import threading
import time
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Any

from .doctor import check_workspace
from .launch import build_plan, execute, os_name
from .registry import Registry
from .tools import (MODES, MODE_DESCRIPTIONS, MODE_LABELS, mode_flags,
                    probe_all, tool_by_id, validate_mode_id)

HTML_PATH = Path(__file__).parent / "picker.html"


class _PickerServer:
    def __init__(self, registry: Registry, default_tool: str | None,
                 default_mode: str | None) -> None:
        self.registry = registry
        self.default_tool = default_tool
        self.default_mode = default_mode
        self.token = secrets.token_urlsafe(16)
        self.last_ping = time.time()
        self._lock = threading.Lock()
        self._server: http.server.ThreadingHTTPServer | None = None
        self._shutdown_requested = False

    # -- helpers ------------------------------------------------------------

    def _query(self, path: str) -> dict[str, list[str]]:
        return urllib.parse.parse_qs(urllib.parse.urlparse(path).query)

    def _authorized(self, path: str) -> bool:
        values = self._query(path).get("token", [])
        return bool(values) and secrets.compare_digest(values[0], self.token)

    def _state(self) -> dict[str, Any]:
        projects = []
        for row in self.registry.list():
            report = check_workspace(self.registry, row["path"],
                                     self.default_tool or "codex")
            projects.append({**row, "doctor": report.to_dict()})
        tools = [t.to_dict() for t in probe_all(self.registry)]
        defaults = {
            "tool": (self.default_tool
                     or self.registry.get_state("last_tool_id") or "codex"),
            "mode": (self.default_mode
                     or self.registry.get_state("last_mode_id") or "safe"),
            "project": self.registry.get_state("last_workspace_id"),
        }
        return {
            "projects": projects,
            "tools": tools,
            "modes": [{"id": m, "label": MODE_LABELS[m],
                       "description": MODE_DESCRIPTIONS[m]} for m in MODES],
            "defaults": defaults,
            "platform": os_name(),
        }

    # -- HTTP handler --------------------------------------------------------

    class _Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:  # silence
            pass

    def _handler_factory(self):
        server = self
        html = HTML_PATH.read_text(encoding="utf-8")

        class Handler(_PickerServer._Handler):
            def _json(self, obj: dict, status: int = 200) -> None:
                data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type",
                                 "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self) -> None:
                path = urllib.parse.urlparse(self.path).path
                if path == "/":
                    data = html.encode("utf-8")
                    self.send_response(200)
                    self.send_header(
                        "Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                if path == "/api/ping":
                    if not server._authorized(self.path):
                        return self._json({"error": "unauthorized"}, 403)
                    with server._lock:
                        server.last_ping = time.time()
                    return self._json({"ok": True})
                if path == "/api/state":
                    if not server._authorized(self.path):
                        return self._json({"error": "unauthorized"}, 403)
                    return self._json(server._state())
                if path == "/api/bye":
                    if not server._authorized(self.path):
                        return self._json({"error": "unauthorized"}, 403)
                    threading.Timer(0.3, server.request_shutdown).start()
                    return self._json({"ok": True})
                if path == "/api/health":
                    return self._json({"ok": True})
                self.send_error(404)

            def do_POST(self) -> None:
                path = urllib.parse.urlparse(self.path).path
                if path != "/api/launch":
                    self.send_error(404)
                    return
                if not server._authorized(self.path):
                    return self._json({"error": "unauthorized"}, 403)
                length = int(self.headers.get("Content-Length", 0))
                try:
                    payload = json.loads(self.rfile.read(length) or b"{}")
                except Exception:
                    return self._json({"error": "bad json"}, 400)
                project_id = str(payload.get("project_id", ""))
                tool_id = str(payload.get("tool_id", "codex"))
                mode = str(payload.get("mode", "safe"))
                row = server.registry.get(project_id)
                if row is None:
                    return self._json({"error": "unknown project"}, 404)
                try:
                    validate_mode_id(mode)
                    tool = tool_by_id(tool_id, server.registry)
                    if tool is None:
                        return self._json({"error": "unknown tool"}, 400)
                    report = check_workspace(server.registry, row["path"],
                                             tool_id)
                    if not report.ready:
                        return self._json({"error": report.message}, 400)
                    plan = build_plan(row["path"], tool, mode,
                                      mode_flags(tool_id, mode))
                except (ValueError, OSError) as error:
                    return self._json({"error": str(error)}, 400)
                execute(plan)
                server.registry.mark_opened(row["id"], tool_id, mode)
                return self._json({
                    "ok": True,
                    "project": row.get("label"),
                    "path": row["path"],
                    "tool_id": tool_id,
                    "tool_label": tool.label,
                    "mode": mode,
                    "target": plan.target,
                })

        return Handler

    # -- lifecycle -----------------------------------------------------------

    def request_shutdown(self) -> None:
        with self._lock:
            self._shutdown_requested = True
        if self._server is not None:
            threading.Thread(target=self._server.shutdown, daemon=True).start()

    def _watchdog(self) -> None:
        # Shut down after the page stops pinging (tab closed) or on request.
        while True:
            time.sleep(5)
            with self._lock:
                stale = time.time() - self.last_ping > 45
                if stale or self._shutdown_requested:
                    if self._server is not None:
                        threading.Thread(target=self._server.shutdown,
                                         daemon=True).start()
                    return

    def serve(self) -> None:
        self._server = http.server.ThreadingHTTPServer(
            ("127.0.0.1", 0), self._handler_factory())
        self._server.daemon_threads = True
        port = self._server.server_address[1]
        url = f"http://127.0.0.1:{port}/?token={self.token}"
        threading.Thread(target=self._watchdog, daemon=True).start()
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
        print(f"Picker opened in your browser: {url}")
        try:
            self._server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self._server.server_close()


def run_web_picker(registry: Registry, default_tool: str | None = None,
                   default_mode: str | None = None) -> int:
    _PickerServer(registry, default_tool, default_mode).serve()
    return 0


# ---------------------------------------------------------------------------
# Terminal fallback picker (no browser needed)
# ---------------------------------------------------------------------------

def _choose(items: list[str], prompt: str) -> int | None:
    for index, text in enumerate(items, start=1):
        print(f"  {index}. {text}")
    try:
        choice = input(f"{prompt}: ").strip()
        index = int(choice) - 1
    except (ValueError, EOFError):
        return None
    return index if 0 <= index < len(items) else None


def run_cli_picker(registry: Registry, default_tool: str | None = None,
                   default_mode: str | None = None) -> int:
    projects = registry.list()
    if not projects:
        print("No projects yet.")
        print("Add one:   codex-workspace add /path/to/project --label \"Name\"")
        print("Or set:    CODEX_WORKSPACE_ROOTS=/parent/folder")
        return 1
    print("== Projects ==")
    project_index = _choose(
        [f"{p.get('label')}  ({p['path']})" for p in projects],
        "Project number")
    if project_index is None:
        return 1
    project = projects[project_index]

    tools = probe_all(registry)
    ready_tools = [t for t in tools if t.ready]
    print("== Tool ==")
    tool_index = _choose(
        [t.display_label() + (f" · {t.version}" if t.version else "")
         for t in tools], "Tool number")
    if tool_index is None:
        return 1
    tool = tools[tool_index]

    print("== Mode ==")
    mode_index = _choose(
        [f"{m} — {MODE_LABELS[m]}: {MODE_DESCRIPTIONS[m]}" for m in MODES],
        "Mode number")
    if mode_index is None:
        return 1
    mode = MODES[mode_index]

    report = check_workspace(registry, project["path"], tool.id)
    if not report.ready:
        print(f"Cannot launch: {report.message}")
        return 2
    plan = build_plan(project["path"], tool, mode, mode_flags(tool.id, mode))
    execute(plan)
    registry.mark_opened(project["id"], tool.id, mode)
    print(f"Opened {tool.label} in {project.get('label')} "
          f"({plan.target}, mode={mode})")
    return 0
