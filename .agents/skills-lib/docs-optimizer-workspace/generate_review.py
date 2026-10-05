#!/usr/bin/env python3
"""
generate_review.py — Static HTML report generator for docs-optimizer benchmark results.

Usage:
    python generate_review.py --static --benchmark path/to/benchmark.json --output path/to/output.html
    python generate_review.py --static  # uses default paths
"""

import argparse
import json
import sys
import os
from datetime import datetime
from collections import defaultdict

# ── defaults ────────────────────────────────────────────────────────────────
DEFAULT_BENCHMARK = os.path.join(
    os.path.dirname(__file__), "iteration-1", "benchmark.json"
)
DEFAULT_OUTPUT = "D:/Downloads/docs-optimizer-review.html"


# ── helpers ──────────────────────────────────────────────────────────────────
def pct(value: float) -> str:
    return f"{value * 100:.0f}%"


def fmt_time(seconds: float) -> str:
    if seconds >= 60:
        return f"{seconds / 60:.1f} min"
    return f"{seconds:.0f}s"


def badge(passed: bool) -> str:
    if passed:
        return '<span class="grade-badge grade-pass">PASS</span>'
    return '<span class="grade-badge grade-fail">FAIL</span>'


def delta_arrow(value: str) -> str:
    """Format a delta string (+X / -X) with colour."""
    v = value.strip()
    if v.startswith("+"):
        return f'<span class="delta-pos">{v}</span>'
    if v.startswith("-"):
        return f'<span class="delta-neg">{v}</span>'
    return v


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


# ── data processing ───────────────────────────────────────────────────────────
def load_eval_metadata(workspace_root: str, eval_id: int) -> dict:
    """Load eval_metadata.json for a given eval, returns {} if not found."""
    base = os.path.join(workspace_root, "iteration-1")
    if os.path.isdir(base):
        for d in os.listdir(base):
            if d.startswith(f"eval-{eval_id}-"):
                candidate = os.path.join(base, d, "eval_metadata.json")
                if os.path.exists(candidate):
                    try:
                        with open(candidate, encoding="utf-8") as f:
                            return json.load(f)
                    except Exception:
                        pass
    return {}


def process(data: dict, workspace_root: str = "") -> dict:
    """Organise raw benchmark.json into a structure convenient for rendering."""
    meta = data.get("metadata", {})
    runs = data.get("runs", [])
    summary = data.get("run_summary", {})

    # Group runs by eval_id → configuration
    by_eval: dict[int, dict] = defaultdict(dict)
    for run in runs:
        eid = run["eval_id"]
        cfg = run["configuration"]
        by_eval[eid][cfg] = run

    evals = sorted(by_eval.items())

    # Load eval metadata (prompts + full assertion lists)
    eval_metadata: dict[int, dict] = {}
    if workspace_root:
        for eval_id, _ in evals:
            eval_metadata[eval_id] = load_eval_metadata(workspace_root, eval_id)

    return {
        "meta": meta,
        "evals": evals,
        "summary": summary,
        "raw_runs": runs,
        "eval_metadata": eval_metadata,
    }


# ── prompts & tests tab ───────────────────────────────────────────────────────
def render_prompts_tab(processed: dict, workspace_root: str) -> str:
    """Render the Prompts & Tests tab: one card per eval with prompt + assertions + output."""
    eval_metadata = processed.get("eval_metadata", {})
    sections = ""

    for eval_id, configs in processed["evals"]:
        name = _eval_name(eval_id)
        meta = eval_metadata.get(eval_id, {})

        prompt = meta.get("prompt", "")
        all_assertions = meta.get("assertions", [])

        # Collect pass/fail for assertions from benchmark runs (with_skill run-1)
        assertion_results: dict[str, dict] = {}
        for cfg_key in ["with_skill", "without_skill"]:
            run = configs.get(cfg_key)
            if run:
                for exp in run.get("expectations", []):
                    text = exp.get("text", "")
                    if text not in assertion_results:
                        assertion_results[text] = {}
                    assertion_results[text][cfg_key] = exp

        # Build assertions table
        assertion_rows = ""
        for assertion_text in all_assertions:
            esc_text = escape(assertion_text)
            ws_exp = assertion_results.get(assertion_text, {}).get("with_skill")
            wos_exp = assertion_results.get(assertion_text, {}).get("without_skill")

            def result_cell(exp):
                if exp is None:
                    return '<td class="pt-cell-na">—</td>'
                ok = exp.get("passed", False)
                icon = "✓" if ok else "✗"
                cls = "pass" if ok else "fail"
                evidence = escape(exp.get("evidence", ""))
                ev_html = f'<div class="pt-evidence">{evidence}</div>' if evidence else ""
                return f'<td class="pt-cell-{cls}"><span class="assertion-status {cls}">{icon}</span>{ev_html}</td>'

            assertion_rows += f"""
          <tr>
            <td class="pt-assertion-text">{esc_text}</td>
            {result_cell(ws_exp)}
            {result_cell(wos_exp)}
          </tr>"""

        assertions_html = f"""
<table class="pt-assertions-table">
  <thead>
    <tr>
      <th>Assertion</th>
      <th style="width:80px">With Skill</th>
      <th style="width:80px">Without Skill</th>
    </tr>
  </thead>
  <tbody>{assertion_rows}
  </tbody>
</table>""" if assertion_rows else "<p class='empty-state'>No assertions found in eval_metadata.json.</p>"

        # Output sections (collapsible per config)
        output_blocks = ""
        for cfg_key in ["with_skill", "without_skill"]:
            run = configs.get(cfg_key)
            if run:
                output_html = render_output_section(run, workspace_root)
                badge_cls = "config-primary" if cfg_key == "with_skill" else "config-baseline"
                badge_label = "with skill" if cfg_key == "with_skill" else "without skill"
                uid = f"pt-out-{eval_id}-{cfg_key}"
                output_blocks += f"""
<div class="pt-output-block">
  <div class="grades-toggle" onclick="this.querySelector('.arrow').classList.toggle('open'); document.getElementById('{uid}').classList.toggle('open')">
    <span class="arrow">&#9658;</span>
    <span class="config-badge {badge_cls}" style="margin-right:0.5rem">{badge_label}</span>
    <span style="font-size:0.8rem;color:var(--text-muted)">full output</span>
  </div>
  <div id="{uid}" class="grades-content">
    {output_html}
  </div>
</div>"""

        prompt_display = f'<pre class="pt-prompt">{escape(prompt)}</pre>' if prompt else '<p class="empty-state">Prompt not available.</p>'

        sections += f"""
<div class="section">
  <div class="section-header">Eval {eval_id} — {escape(name)}</div>
  <div class="section-body">
    <div class="pt-label">User Prompt</div>
    {prompt_display}
    <div class="pt-label" style="margin-top:1rem">Assertions ({len(all_assertions)} total)</div>
    {assertions_html}
    <div class="pt-label" style="margin-top:1rem">Agent Outputs</div>
    {output_blocks}
  </div>
</div>"""

    return sections


# ── render output file section ────────────────────────────────────────────────
def render_output_section(run: dict, workspace_root: str) -> str:
    """Try to load output.md for the run and render it."""
    eval_id = run["eval_id"]
    cfg = run["configuration"]
    run_num = run["run_number"]

    output_path = os.path.join(
        workspace_root,
        f"iteration-1",
        f"eval-{eval_id}-{_eval_slug(eval_id)}",
        cfg,
        "outputs",
        "output.md",
    )

    # Also try without slug
    if not os.path.exists(output_path):
        # scan for the directory
        base = os.path.join(workspace_root, "iteration-1")
        if os.path.isdir(base):
            for d in os.listdir(base):
                if d.startswith(f"eval-{eval_id}-"):
                    candidate = os.path.join(base, d, cfg, "outputs", "output.md")
                    if os.path.exists(candidate):
                        output_path = candidate
                        break

    if os.path.exists(output_path):
        try:
            with open(output_path, encoding="utf-8") as f:
                content = escape(f.read())
            return f"""
<div class="output-file">
  <div class="output-file-header">
    <span>output.md</span>
    <span style="font-size:0.7rem;opacity:0.6">{escape(output_path)}</span>
  </div>
  <div class="output-file-content">
    <pre>{content}</pre>
  </div>
</div>"""
        except Exception:
            pass

    return '<p class="empty-state">output.md not found or not readable.</p>'


def _eval_slug(eval_id: int) -> str:
    slugs = {
        1: "analyze",
        2: "tiered",
        3: "audit",
        4: "optimize",
        5: "duplication",
        6: "freshness",
        7: "tokens",
        8: "crossref",
        9: "stale-issues",
        10: "orphan-docs",
    }
    return slugs.get(eval_id, str(eval_id))


def _eval_name(eval_id: int) -> str:
    names = {
        1: "Analyze & Score",
        2: "Tiered Classification",
        3: "Full Audit",
        4: "CLAUDE.md Optimize",
        5: "Duplication Detection",
        6: "Freshness Check",
        7: "Token Budget",
        8: "Cross-Reference Validation",
        9: "Stale Issues",
        10: "Orphan Docs",
    }
    return names.get(eval_id, f"Eval {eval_id}")


# ── benchmark summary table ───────────────────────────────────────────────────
def render_summary_table(processed: dict) -> str:
    summary = processed["summary"]
    ws = summary.get("with_skill", {})
    wos = summary.get("without_skill", {})
    delta = summary.get("delta", {})

    rows = ""
    metrics = [
        ("pass_rate", "Pass Rate", lambda v: pct(v["mean"])),
        ("time_seconds", "Avg Time", lambda v: fmt_time(v["mean"])),
        ("tokens", "Avg Tokens", lambda v: f"{v['mean']:.0f}"),
    ]
    for key, label, fmt in metrics:
        ws_val = fmt(ws[key]) if key in ws else "—"
        wos_val = fmt(wos[key]) if key in wos else "—"
        d = delta.get(key, "—")
        rows += f"""
      <tr>
        <td>{label}</td>
        <td><strong>{ws_val}</strong></td>
        <td>{wos_val}</td>
        <td>{delta_arrow(str(d))}</td>
      </tr>"""

    return f"""
<table class="benchmark-table">
  <thead>
    <tr>
      <th>Metric</th>
      <th>With Skill</th>
      <th>Without Skill</th>
      <th>Delta</th>
    </tr>
  </thead>
  <tbody>{rows}
  </tbody>
</table>"""


# ── per-eval table ────────────────────────────────────────────────────────────
def render_eval_table(processed: dict) -> str:
    rows = ""
    for eval_id, configs in processed["evals"]:
        name = _eval_name(eval_id)
        ws = configs.get("with_skill", {})
        wos = configs.get("without_skill", {})

        def cell(run: dict) -> str:
            if not run:
                return "<td>—</td>"
            r = run.get("result", {})
            pr = r.get("pass_rate", 0)
            color = "var(--green)" if pr >= 1.0 else ("var(--accent)" if pr >= 0.5 else "var(--red)")
            return f'<td style="color:{color};font-weight:600">{pct(pr)}</td>'

        rows += f"""
    <tr>
      <td>Eval {eval_id}</td>
      <td>{escape(name)}</td>
      {cell(ws)}
      {cell(wos)}
    </tr>"""

    return f"""
<table class="benchmark-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Eval Name</th>
      <th>With Skill</th>
      <th>Without Skill</th>
    </tr>
  </thead>
  <tbody>{rows}
  </tbody>
</table>"""


# ── assertions section ────────────────────────────────────────────────────────
def render_assertions(run: dict) -> str:
    exps = run.get("expectations", [])
    if not exps:
        return "<p class='empty-state'>No expectations recorded.</p>"

    result = run.get("result", {})
    passed = result.get("passed", 0)
    total = result.get("total", len(exps))
    pr = result.get("pass_rate", 0)

    items = ""
    for exp in exps:
        ok = exp.get("passed", False)
        status_cls = "pass" if ok else "fail"
        icon = "✓" if ok else "✗"
        evidence = escape(exp.get("evidence", ""))
        text = escape(exp.get("text", ""))
        items += f"""
      <li class="assertion-item">
        <span class="assertion-status {status_cls}">{icon}</span>{text}
        {"<div class='assertion-evidence'>" + evidence + "</div>" if evidence else ""}
      </li>"""

    color = "var(--green)" if pr >= 1.0 else ("var(--accent)" if pr >= 0.5 else "var(--red)")
    return f"""
    <div class="grades-summary">
      <span style="color:{color};font-weight:700">{pct(pr)}</span>
      <span style="color:var(--text-muted);font-size:0.8rem">({passed}/{total} passed)</span>
    </div>
    <ul class="assertion-list">{items}
    </ul>"""


# ── run card ──────────────────────────────────────────────────────────────────
def render_run_card(run: dict, workspace_root: str) -> str:
    cfg = run.get("configuration", "")
    r = run.get("result", {})
    pr = r.get("pass_rate", 0)
    time_s = r.get("time_seconds", 0)
    tokens = r.get("tokens", 0)
    tool_calls = r.get("tool_calls", 0)

    badge_cls = "config-primary" if cfg == "with_skill" else "config-baseline"
    badge_label = "with skill" if cfg == "with_skill" else "without skill"
    color = "var(--green)" if pr >= 1.0 else ("var(--accent)" if pr >= 0.5 else "var(--red)")

    stats = f"""
      <div class="run-stats">
        <span class="stat"><b style="color:{color}">{pct(pr)}</b> pass rate</span>
        <span class="stat">{fmt_time(time_s)}</span>
        {"<span class='stat'>" + str(tokens) + " tok</span>" if tokens else ""}
        {"<span class='stat'>" + str(tool_calls) + " calls</span>" if tool_calls else ""}
      </div>"""

    assertions_html = render_assertions(run)
    # output_html = render_output_section(run, workspace_root)  # omit for static; too large

    return f"""
<div class="run-card">
  <div class="run-card-header">
    <span class="config-badge {badge_cls}">{badge_label}</span>
    {stats}
  </div>
  <div class="run-card-body">
    <div class="grades-toggle" onclick="this.querySelector('.arrow').classList.toggle('open'); this.nextElementSibling.classList.toggle('open')">
      <span class="arrow">▶</span>
      <span style="font-size:0.8125rem;font-weight:500">Assertions</span>
    </div>
    <div class="grades-content">
      {assertions_html}
    </div>
  </div>
</div>"""


# ── eval section ─────────────────────────────────────────────────────────────
def render_eval_section(eval_id: int, configs: dict, workspace_root: str) -> str:
    name = _eval_name(eval_id)
    cards = ""
    for cfg_key in ["with_skill", "without_skill"]:
        run = configs.get(cfg_key)
        if run:
            cards += render_run_card(run, workspace_root)

    return f"""
<div class="section">
  <div class="section-header">Eval {eval_id} — {escape(name)}</div>
  <div class="section-body eval-grid">
    {cards}
  </div>
</div>"""


# ── full HTML ─────────────────────────────────────────────────────────────────
HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>docs-optimizer — Benchmark Review</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600&family=Lora:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #faf9f5;
      --surface: #ffffff;
      --border: #e8e6dc;
      --text: #141413;
      --text-muted: #b0aea5;
      --accent: #d97757;
      --accent-hover: #c4613f;
      --green: #788c5d;
      --green-bg: #eef2e8;
      --red: #c44;
      --red-bg: #fceaea;
      --header-bg: #141413;
      --header-text: #faf9f5;
      --radius: 6px;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Lora', Georgia, serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
    }}
    .header {{
      background: var(--header-bg);
      color: var(--header-text);
      padding: 1.25rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }}
    .header h1 {{
      font-family: 'Poppins', sans-serif;
      font-size: 1.25rem;
      font-weight: 600;
    }}
    .header .subtitle {{
      font-size: 0.8rem;
      opacity: 0.6;
      margin-top: 0.25rem;
    }}
    .header .meta-right {{
      font-size: 0.8rem;
      opacity: 0.7;
      text-align: right;
      line-height: 1.7;
    }}

    .view-tabs {{
      display: flex;
      padding: 0 2rem;
      background: var(--bg);
      border-bottom: 1px solid var(--border);
    }}
    .view-tab {{
      font-family: 'Poppins', sans-serif;
      padding: 0.625rem 1.25rem;
      font-size: 0.8125rem;
      font-weight: 500;
      cursor: pointer;
      border: none;
      background: none;
      color: var(--text-muted);
      border-bottom: 2px solid transparent;
      transition: all 0.15s;
    }}
    .view-tab:hover {{ color: var(--text); }}
    .view-tab.active {{
      color: var(--accent);
      border-bottom-color: var(--accent);
    }}
    .view-panel {{ display: none; padding: 1.5rem 2rem; }}
    .view-panel.active {{ display: block; }}

    .section {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      margin-bottom: 1.25rem;
    }}
    .section-header {{
      font-family: 'Poppins', sans-serif;
      padding: 0.75rem 1rem;
      font-size: 0.75rem;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border);
      background: var(--bg);
      border-radius: var(--radius) var(--radius) 0 0;
    }}
    .section-body {{ padding: 1rem; }}

    .benchmark-table {{
      border-collapse: collapse;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      font-size: 0.8125rem;
      width: 100%;
      margin-bottom: 1.5rem;
    }}
    .benchmark-table th, .benchmark-table td {{
      padding: 0.625rem 0.75rem;
      text-align: left;
      border: 1px solid var(--border);
    }}
    .benchmark-table th {{
      font-family: 'Poppins', sans-serif;
      background: var(--header-bg);
      color: var(--header-text);
      font-weight: 500;
    }}
    .benchmark-table tr:hover td {{ background: #f5f4ef; }}

    .delta-pos {{ color: var(--green); font-weight: 600; }}
    .delta-neg {{ color: var(--red); font-weight: 600; }}

    .eval-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
    }}
    @media (max-width: 900px) {{ .eval-grid {{ grid-template-columns: 1fr; }} }}

    .run-card {{
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
    }}
    .run-card-header {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.625rem 0.75rem;
      background: var(--bg);
      border-bottom: 1px solid var(--border);
      flex-wrap: wrap;
    }}
    .run-card-body {{ padding: 0.75rem; }}

    .config-badge {{
      display: inline-block;
      padding: 0.2rem 0.625rem;
      border-radius: 9999px;
      font-family: 'Poppins', sans-serif;
      font-size: 0.6875rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    .config-primary {{ background: rgba(33,150,243,0.12); color: #1976d2; }}
    .config-baseline {{ background: rgba(255,193,7,0.15); color: #f57f17; }}

    .run-stats {{ display: flex; gap: 1rem; flex-wrap: wrap; }}
    .stat {{ font-size: 0.8rem; color: var(--text-muted); }}

    .grade-badge {{
      display: inline-block;
      padding: 0.125rem 0.5rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
    }}
    .grade-pass {{ background: var(--green-bg); color: var(--green); }}
    .grade-fail {{ background: var(--red-bg); color: var(--red); }}

    .grades-toggle {{
      display: flex;
      align-items: center;
      cursor: pointer;
      user-select: none;
      font-size: 0.8125rem;
    }}
    .grades-toggle:hover {{ color: var(--accent); }}
    .grades-toggle .arrow {{
      margin-right: 0.5rem;
      transition: transform 0.15s;
      font-size: 0.75rem;
      display: inline-block;
    }}
    .grades-toggle .arrow.open {{ transform: rotate(90deg); }}
    .grades-content {{ display: none; margin-top: 0.75rem; }}
    .grades-content.open {{ display: block; }}
    .grades-summary {{
      font-size: 0.875rem;
      margin-bottom: 0.75rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .assertion-list {{ list-style: none; }}
    .assertion-item {{
      padding: 0.5rem 0;
      border-bottom: 1px solid var(--border);
      font-size: 0.8rem;
      line-height: 1.5;
    }}
    .assertion-item:last-child {{ border-bottom: none; }}
    .assertion-status {{ font-weight: 600; margin-right: 0.375rem; }}
    .assertion-status.pass {{ color: var(--green); }}
    .assertion-status.fail {{ color: var(--red); }}
    .assertion-evidence {{
      color: var(--text-muted);
      font-size: 0.75rem;
      margin-top: 0.25rem;
      padding-left: 1.25rem;
    }}
    .empty-state {{
      color: var(--text-muted);
      font-style: italic;
      padding: 1rem;
      text-align: center;
    }}
    .chip-row {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; }}
    .chip {{
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 9999px;
      padding: 0.25rem 0.75rem;
      font-size: 0.75rem;
      font-family: 'Poppins', sans-serif;
      color: var(--text-muted);
    }}
    .chip strong {{ color: var(--text); }}

    /* Prompts & Tests tab */
    .pt-label {{
      font-family: 'Poppins', sans-serif;
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-muted);
      margin-bottom: 0.5rem;
    }}
    .pt-prompt {{
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 0.75rem 1rem;
      font-family: 'Lora', Georgia, serif;
      font-size: 0.875rem;
      white-space: pre-wrap;
      word-break: break-word;
      color: var(--text);
    }}
    .pt-assertions-table {{
      border-collapse: collapse;
      width: 100%;
      font-size: 0.8rem;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
    }}
    .pt-assertions-table th {{
      font-family: 'Poppins', sans-serif;
      background: var(--header-bg);
      color: var(--header-text);
      font-weight: 500;
      padding: 0.5rem 0.75rem;
      text-align: left;
      border: 1px solid var(--border);
    }}
    .pt-assertions-table td {{
      padding: 0.5rem 0.75rem;
      border: 1px solid var(--border);
      vertical-align: top;
    }}
    .pt-assertions-table tr:hover td {{ background: #f5f4ef; }}
    .pt-assertion-text {{ color: var(--text); line-height: 1.5; }}
    .pt-cell-pass {{ color: var(--green); font-weight: 600; vertical-align: top; }}
    .pt-cell-fail {{ color: var(--red); font-weight: 600; vertical-align: top; }}
    .pt-cell-na {{ color: var(--text-muted); text-align: center; }}
    .pt-evidence {{
      font-size: 0.72rem;
      color: var(--text-muted);
      margin-top: 0.25rem;
      font-weight: 400;
      line-height: 1.4;
      word-break: break-word;
    }}
    .pt-output-block {{ margin-bottom: 0.75rem; }}
    .output-file {{
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
      margin-top: 0.5rem;
    }}
    .output-file-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.375rem 0.75rem;
      background: var(--bg);
      border-bottom: 1px solid var(--border);
      font-family: 'Poppins', sans-serif;
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--text-muted);
    }}
    .output-file-content {{
      max-height: 500px;
      overflow-y: auto;
      background: var(--surface);
    }}
    .output-file-content pre {{
      padding: 1rem;
      font-size: 0.78rem;
      line-height: 1.55;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: 'Courier New', monospace;
      color: var(--text);
    }}
  </style>
</head>
<body>

<div class="header">
  <div>
    <h1>docs-optimizer — Benchmark Review</h1>
    <div class="subtitle">Iteration 1 · Static report</div>
  </div>
  <div class="meta-right">
    {META_RIGHT}
  </div>
</div>

<div class="view-tabs">
  <button class="view-tab active" onclick="switchTab(this,'overview')">Overview</button>
  <button class="view-tab" onclick="switchTab(this,'evals')">Per-Eval Results</button>
  <button class="view-tab" onclick="switchTab(this,'prompts')">Prompts &amp; Tests</button>
</div>

<!-- OVERVIEW TAB -->
<div id="tab-overview" class="view-panel active">
  <div class="chip-row">
    {CHIPS}
  </div>
  <div class="section">
    <div class="section-header">Summary — with skill vs without skill</div>
    <div class="section-body">
      {SUMMARY_TABLE}
    </div>
  </div>
  <div class="section">
    <div class="section-header">Pass Rate per Eval</div>
    <div class="section-body">
      {EVAL_TABLE}
    </div>
  </div>
</div>

<!-- EVALS TAB -->
<div id="tab-evals" class="view-panel">
  {EVAL_SECTIONS}
</div>

<!-- PROMPTS & TESTS TAB -->
<div id="tab-prompts" class="view-panel">
  {PROMPTS_SECTIONS}
</div>

<script>
function switchTab(btn, tabId) {{
  document.querySelectorAll('.view-tab').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('tab-' + tabId).classList.add('active');
}}
</script>
</body>
</html>
"""


# ── main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Generate static HTML review for docs-optimizer benchmark.")
    parser.add_argument("--static", action="store_true", help="Generate static HTML (required)")
    parser.add_argument("--benchmark", default=DEFAULT_BENCHMARK, help="Path to benchmark.json")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output HTML file path")
    args = parser.parse_args()

    benchmark_path = args.benchmark
    output_path = args.output

    print(f"Reading benchmark: {benchmark_path}")
    if not os.path.exists(benchmark_path):
        print(f"ERROR: benchmark.json not found at {benchmark_path}", file=sys.stderr)
        sys.exit(1)

    with open(benchmark_path, encoding="utf-8") as f:
        data = json.load(f)

    workspace_root = os.path.dirname(os.path.abspath(benchmark_path))
    if workspace_root.endswith("iteration-1"):
        workspace_root = os.path.dirname(workspace_root)

    processed = process(data, workspace_root)
    meta = processed["meta"]

    # chips
    evals_run = meta.get("evals_run", [])
    chips = f"""
    <div class="chip">Skill: <strong>{escape(meta.get('skill_name', ''))}</strong></div>
    <div class="chip">Evals: <strong>{len(evals_run)}</strong></div>
    <div class="chip">Runs/config: <strong>{meta.get('runs_per_configuration', 1)}</strong></div>
    <div class="chip">Timestamp: <strong>{escape(meta.get('timestamp', ''))}</strong></div>
    """

    meta_right = f"""
      Skill: {escape(meta.get('skill_name', ''))}<br>
      Evals: {len(evals_run)} &nbsp;|&nbsp; Runs/config: {meta.get('runs_per_configuration', 1)}<br>
      Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    """

    summary_table = render_summary_table(processed)
    eval_table = render_eval_table(processed)

    eval_sections = ""
    for eval_id, configs in processed["evals"]:
        eval_sections += render_eval_section(eval_id, configs, workspace_root)

    prompts_sections = render_prompts_tab(processed, workspace_root)

    html = HTML_TEMPLATE.format(
        META_RIGHT=meta_right,
        CHIPS=chips,
        SUMMARY_TABLE=summary_table,
        EVAL_TABLE=eval_table,
        EVAL_SECTIONS=eval_sections,
        PROMPTS_SECTIONS=prompts_sections,
    )

    # ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML report written to: {output_path}")


if __name__ == "__main__":
    main()
