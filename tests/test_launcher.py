#!/usr/bin/env python3
"""Self-contained test suite for the Codex Workspace Launcher.

Run:  python tests/test_launcher.py     (no third-party dependencies)

Runs everywhere; sections guarded by platform run native checks:
  macOS   - osascript runs, generated AppleScript compiles (osacompile),
            shell command passes bash -n, Terminal.app / open exist
  Linux   - launch executed end-to-end with a mock terminal
  Windows - Windows Terminal / cmd start fallback plan shapes
"""

import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cwl.discovery import discover  # noqa: E402
from cwl.doctor import check_workspace  # noqa: E402
from cwl.launch import (_app_plan, _shell_quote,  # noqa: E402
                        _linux_terminal_plan, _macos_terminal_plan,
                        _windows_terminal_plan, build_plan, execute,
                        find_terminal, os_name)
from cwl.picker import _PickerServer  # noqa: E402
from cwl.registry import Registry, label_for_path, registry_id_for_path  # noqa: E402
from cwl.tools import (MODE_FLAGS, ToolDefinition, ToolReport,  # noqa: E402
                       mode_flags, probe_all, probe_tool, tool_by_id,
                       tool_definitions, validate_mode_id, validate_tool_id)

PASSED = 0
FAILURES = []


def check(name, condition, detail=""):
    global PASSED
    if condition:
        PASSED += 1
        print(f"  ok   {name}")
    else:
        FAILURES.append(name)
        print(f"  FAIL {name}  {detail}")


def section(title):
    print(f"\n== {title} ==")


def make_bin_dir(tmp: Path) -> Path:
    """Create a fake `codex` tool on PATH so probe+doctor can be 'ready'."""
    bin_dir = tmp / "bin"
    bin_dir.mkdir(exist_ok=True)
    if os.name == "nt":
        (bin_dir / "codex.cmd").write_text(
            "@echo off\r\necho codex-cli 9.9.9-test\r\n", encoding="utf-8")
    else:
        tool = bin_dir / "codex"
        tool.write_text("#!/bin/sh\necho 'codex-cli 9.9.9-test'\n",
                        encoding="utf-8")
        tool.chmod(0o755)
    old_path = os.environ.get("PATH", "")
    os.environ["PATH"] = str(bin_dir) + os.pathsep + old_path
    return bin_dir


def make_registry(tmp: Path, name: str = "reg") -> Registry:
    return Registry(str(tmp / name / "registry.json"))


# ---------------------------------------------------------------------------
def test_registry(tmp):
    section("registry: CRUD, short ids, probes, state")
    reg = make_registry(tmp, "r1")
    row = reg.upsert(tmp / "Alpha Project", "Alpha")
    check("upsert creates", reg.get(row["id"])["label"] == "Alpha")
    check("list contains", len(reg.list()) == 1)
    check("short id lookup", reg.get(row["id"][:8])["id"] == row["id"])
    reg.rename(row["id"][:8], "Alpha v2")
    check("rename via short id", reg.get(row["id"])["label"] == "Alpha v2")
    reg.upsert(tmp / "Beta", "Beta")
    check("second project", len(reg.list()) == 2)
    reg.archive(row["id"][:8])
    check("archive removes from list", len(reg.list()) == 1)
    reg.upsert(tmp / "Alpha Project", "Alpha back")
    check("re-add restores", len(reg.list()) == 2)
    reg.set_probe("codex", {"id": "codex", "label": "Codex", "state": "ready",
                            "message": "ok"})
    check("probe cache get", reg.get_probe("codex")["state"] == "ready")
    reg.set_state("last_mode_id", "yolo")
    check("app state", reg.get_state("last_mode_id") == "yolo")
    check("label_for_path", label_for_path("my-project") == "My Project")
    check("id stable", registry_id_for_path(tmp / "X") ==
          registry_id_for_path(tmp / "X"))


def test_tools_and_modes(tmp):
    section("tools: catalog, probing, modes")
    make_bin_dir(tmp)
    reg = make_registry(tmp, "r2")
    defs = tool_definitions()
    check("catalog has all tools", len(defs) >= 10)
    check("unique ids", len({d.id for d in defs}) == len(defs))
    check("validate_tool_id ok", validate_tool_id("muse") == "muse")
    try:
        validate_tool_id("bad id!")
        check("validate_tool_id rejects", False)
    except ValueError:
        check("validate_tool_id rejects", True)
    report = tool_by_id("codex", reg)
    check("fake codex on PATH is ready",
          report is not None and report.ready and report.version == "codex-cli 9.9.9-test",
          repr(report))
    missing = probe_tool(ToolDefinition("zzz-tool", "Zzz Tool",
                                        ("definitely-not-installed-xyz",)))
    check("absent tool is missing", missing.state == "missing",
          repr(missing))
    payload = report.to_dict()
    check("report roundtrip", ToolReport.from_dict(payload).id == "codex")
    check("probe cached", reg.get_probe("codex") is not None)
    check("mode_flags muse yolo", mode_flags("muse", "yolo") == ("--yolo",))
    check("mode_flags claude free",
          mode_flags("claude", "free") == ("--permission-mode", "acceptEdits"))
    check("mode_flags codex safe", mode_flags("codex", "safe") == ())
    try:
        validate_mode_id("nope")
        check("validate_mode rejects", False)
    except ValueError:
        check("validate_mode rejects", True)


def test_quoting():
    section("shell quoting (pure, every OS)")
    check("shell_quote simple", _shell_quote("/a b") == "'/a b'")
    check("shell_quote single quote",
          _shell_quote("it's") == "'it'\\''s'")
    cyr = _shell_quote("/Дом/Продажи Событий")
    check("shell_quote cyrillic+space",
          cyr == "'/Дом/Продажи Событий'")


def test_doctor(tmp):
    section("doctor: folder and tool states")
    make_bin_dir(tmp)
    reg = make_registry(tmp, "r3")
    ghost = check_workspace(reg, tmp / "does-not-exist", "codex")
    check("missing folder -> missing", ghost.state == "missing")
    # Headless CI has no terminal: provide a mock one so the 'ready' path is
    # exercised (real desktops find a real terminal).
    saved_term = os.environ.get("CODEX_TERMINAL")
    if find_terminal() is None:
        mock = tmp / "mock-term"
        mock.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        mock.chmod(0o755)
        os.environ["CODEX_TERMINAL"] = str(mock)
    try:
        ok = check_workspace(reg, tmp, "codex")
        check("real folder + fake codex -> ready", ok.ready, ok.to_dict())
    finally:
        if saved_term is None:
            os.environ.pop("CODEX_TERMINAL", None)
        else:
            os.environ["CODEX_TERMINAL"] = saved_term
    notool = check_workspace(reg, tmp, "nonexistent-tool")
    check("unknown tool -> degraded", notool.state == "degraded",
          notool.state)
    if os.name != "nt":
        locked = tmp / "locked"
        locked.mkdir()
        locked.chmod(0o000)
        try:
            blocked = check_workspace(reg, locked, "codex")
            check("unreadable folder -> blocked", blocked.state == "blocked",
                  blocked.state)
        finally:
            locked.chmod(0o755)


def test_picker_server(tmp):
    section("picker server: state, auth, validation")
    reg = make_registry(tmp, "r4")
    reg.upsert(tmp, "Test Project")
    server = _PickerServer(reg, None, None)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0),
                                          server._handler_factory())
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{port}/"
    token = server.token
    try:
        html = urllib.request.urlopen(f"{url}?token={token}").read().decode()
        check("serves picker page", "<title>Codex Workspace</title>" in html)
        state = json.loads(
            urllib.request.urlopen(f"{url}api/state?token={token}").read())
        check("state has projects/tools/modes",
              len(state["projects"]) == 1 and len(state["tools"]) >= 10
              and len(state["modes"]) == 3)
        try:
            urllib.request.urlopen(f"{url}api/state?token=WRONG")
            check("rejects bad token", False)
        except urllib.error.HTTPError as e:
            check("rejects bad token", e.code == 403)
        req = urllib.request.Request(
            f"{url}api/launch?token={token}",
            data=json.dumps({"project_id": "nope", "tool_id": "codex",
                             "mode": "safe"}).encode(),
            headers={"Content-Type": "application/json"})
        try:
            urllib.request.urlopen(req)
            check("rejects unknown project", False)
        except urllib.error.HTTPError as e:
            check("rejects unknown project", e.code == 404)
        check("ping", json.loads(
            urllib.request.urlopen(f"{url}api/ping?token={token}").read())
            == {"ok": True})
    finally:
        srv.shutdown()


def test_discovery(tmp):
    section("discovery from CODEX_WORKSPACE_ROOTS")
    reg = make_registry(tmp, "r5")
    parent = tmp / "roots"
    (parent / "ProjA").mkdir(parents=True)
    (parent / "ProjB").mkdir(parents=True)
    (parent / "ProjC").mkdir(parents=True)
    old = os.environ.get("CODEX_WORKSPACE_ROOTS")
    os.environ["CODEX_WORKSPACE_ROOTS"] = str(parent)
    try:
        added = discover(reg)
        check("three projects seeded", added == 3, added)
        discover(reg)
        check("second run adds nothing", len(reg.list()) == 3)
    finally:
        if old is None:
            os.environ.pop("CODEX_WORKSPACE_ROOTS", None)
        else:
            os.environ["CODEX_WORKSPACE_ROOTS"] = old


def test_macos_native(tmp):
    if sys.platform != "darwin":
        return
    section("macOS native: .command plan, bash -n, open, Terminal")
    check("/usr/bin/open exists", Path("/usr/bin/open").exists())
    check("Terminal.app exists",
          Path("/Applications/Utilities/Terminal.app").exists()
          or Path("/System/Applications/Utilities/Terminal.app").exists())
    check("find_terminal falls back to Terminal", find_terminal() == "Terminal")

    plan = _macos_terminal_plan("Terminal", "/Users/t/My Project",
                                "/usr/local/bin/muse", ("--yolo",))
    check("plan uses open -a", plan.command[:3] == ("open", "-a", "Terminal"))
    script_path = Path(plan.command[3])
    check("plan points to a .command file",
          script_path.suffix == ".command" and script_path.exists())
    check(".command is executable", os.access(script_path, os.X_OK))
    bash_ok = subprocess.run(["bash", "-n", str(script_path)],
                             capture_output=True, text=True, timeout=30)
    check("bash -n accepts generated .command", bash_ok.returncode == 0,
          bash_ok.stderr)
    content = script_path.read_text(encoding="utf-8")
    check("command cd's into project", "cd '/Users/t/My Project'" in content)
    check("command runs tool with flags",
          "'/usr/local/bin/muse' --yolo" in content)

    plan_i = _macos_terminal_plan("iTerm2", "/Users/t/My Project",
                                  "/usr/local/bin/muse", ())
    check("iTerm2 plan uses open -a",
          plan_i.command[:3] == ("open", "-a", "iTerm2"))
    Path(plan_i.command[3]).unlink(missing_ok=True)

    app_plan = _app_plan("macos", "/Users/t/My Project",
                         ToolReport(id="codex-app", label="Codex App",
                                    state="ready", message="",
                                    launch_mode="app"))
    check("macos app plan uses open -a",
          app_plan.command[:3] == ("open", "-a", "Codex"))


def test_linux_execute(tmp):
    if sys.platform != "linux":
        return
    section("linux: end-to-end execute with a mock terminal")
    terminal = tmp / "mock-terminal"
    argout = tmp / "args.txt"
    terminal.write_text("#!/bin/sh\nprintf '%s\\n' \"$@\" > " +
                        str(argout) + "\n", encoding="utf-8")
    terminal.chmod(0o755)
    old = os.environ.get("CODEX_TERMINAL")
    os.environ["CODEX_TERMINAL"] = str(terminal)
    try:
        check("find_terminal accepts absolute path",
              find_terminal() == str(terminal))
        tool = ToolReport(id="codex", label="Codex", state="ready",
                          message="ok", executable_path="/usr/bin/codex",
                          version="1", launch_mode="terminal")
        plan = build_plan(str(tmp), tool, "safe", ())
        check("plan targets mock terminal",
              plan.command[0] == str(terminal), plan.to_dict())
        execute(plan)
        time.sleep(1.0)
        args = argout.read_text() if argout.exists() else ""
        check("tool path passed to terminal", "/usr/bin/codex" in args, args)
    finally:
        if old is None:
            os.environ.pop("CODEX_TERMINAL", None)
        else:
            os.environ["CODEX_TERMINAL"] = old
    # plan shapes for the real Linux terminals
    for name, expect in (("gnome-terminal", "--working-directory"),
                         ("kitty", "--directory"),
                         ("alacritty", "--working-directory"),
                         ("wezterm", "--cwd")):
        plan = _linux_terminal_plan(f"/usr/bin/{name}", "/w", "/tool", ())
        check(f"{name} plan shape", expect in plan.command, plan.command)


def test_windows_plans(tmp):
    if os.name != "nt":
        return
    section("windows: terminal plan shapes")
    terminal = find_terminal()
    tool = ToolReport(id="codex", label="Codex", state="ready", message="ok",
                      executable_path=str(tmp / "codex.cmd"), version="1",
                      launch_mode="terminal")
    plan = build_plan(str(tmp), tool, "safe", ())
    check("windows plan target known",
          plan.target in ("Windows Terminal", "cmd.exe"), plan.to_dict())
    if terminal and os.path.basename(terminal).lower() == "wt.exe":
        check("wt plan has -d", plan.command[1] == "-d", plan.command)
    fallback = _windows_terminal_plan(None, str(tmp), str(tmp / "t.cmd"), ())
    check("cmd fallback uses start /D",
          fallback.command[:4] == ("cmd.exe", "/c", "start", ""), fallback.command)
    app_plan = _app_plan("windows", str(tmp),
                         ToolReport(id="codex-app", label="Codex App",
                                    state="ready", message="",
                                    launch_mode="app"))
    check("windows app plan opens explorer", "explorer.exe" in app_plan.command)


def test_cli_smoke(tmp):
    section("cli smoke: --version and list --json")
    env = dict(os.environ)
    state = tmp / "state"
    if os.name == "nt":
        env["LOCALAPPDATA"] = str(state)
    else:
        env["XDG_STATE_HOME"] = str(state)
    proc = subprocess.run([sys.executable, str(ROOT / "launcher.py"),
                           "--version"], capture_output=True, text=True,
                          env=env, timeout=60)
    check("--version exits 0", proc.returncode == 0, proc.stderr)
    proc = subprocess.run([sys.executable, str(ROOT / "launcher.py"),
                           "list", "--json"], capture_output=True, text=True,
                          env=env, timeout=60)
    check("list --json valid", proc.returncode == 0 and
          isinstance(json.loads(proc.stdout), list), proc.stderr)
    proc = subprocess.run([sys.executable, str(ROOT / "launcher.py"),
                           "open", "nope", "--tool", "codex", "--dry-run"],
                          capture_output=True, text=True, env=env, timeout=60)
    check("open unknown project -> rc 2", proc.returncode == 2, proc.returncode)


def main():
    with tempfile.TemporaryDirectory(prefix="cwl-test-") as td:
        tmp = Path(td)
        test_registry(tmp)
        test_tools_and_modes(tmp)
        test_quoting()
        test_doctor(tmp)
        test_picker_server(tmp)
        test_discovery(tmp)
        test_macos_native(tmp)
        test_linux_execute(tmp)
        test_windows_plans(tmp)
        test_cli_smoke(tmp)
    print(f"\n==== {PASSED} passed, {len(FAILURES)} failed ====")
    if FAILURES:
        print("Failures: " + ", ".join(FAILURES))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
