"""Generate a static HTML report from a Velaris run report."""

from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path

from velaris_core.report_loader import RunReport, TestReport, load_jsonl, build_run_report


def generate_report(jsonl_path: Path | str, output_path: Path | str = "report.html") -> Path:
    """Load a JSON-lines log and write a single static HTML report."""
    events = load_jsonl(jsonl_path)
    report = build_run_report(events)
    out = Path(output_path)
    out.write_text(render_html(report), encoding="utf-8")
    return out


def render_html(report: RunReport) -> str:
    """Render a complete self-contained HTML document."""
    tests_json = json.dumps([_test_to_dict(t) for t in report.tests])
    duration = f"{report.duration_seconds:.2f}s"
    pass_rate = round((report.passed / report.total) * 100) if report.total else 0
    passed_pct = (report.passed / report.total * 100) if report.total else 0
    failed_pct = (report.failed / report.total * 100) if report.total else 0
    all_passed = report.failed == 0
    status_text = "All passed" if all_passed else f"{report.failed} failed"
    status_class = "ok" if all_passed else "bad"
    generated_at = datetime.now().strftime("%b %d, %Y at %I:%M %p")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Velaris Test Report</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root, [data-theme="dark"] {{
      --bg: #07090d;
      --bg-2: #0b0e14;
      --topbar-bg: rgba(8, 11, 16, 0.82);
      --glow-1: rgba(62, 207, 142, 0.07);
      --glow-2: rgba(86, 200, 255, 0.06);
      --surface: rgba(18, 24, 33, 0.85);
      --surface-2: rgba(33, 43, 58, 0.55);
      --surface-3: rgba(255, 255, 255, 0.04);
      --border: rgba(255, 255, 255, 0.08);
      --border-strong: rgba(255, 255, 255, 0.15);
      --text: #eef2f8;
      --muted: #93a3ba;
      --faint: #5d6b80;
      --green: #3ddc84;
      --green-dim: rgba(61, 220, 132, 0.13);
      --red: #ff6b73;
      --red-dim: rgba(255, 107, 115, 0.13);
      --error-text: #ffb4b8;
      --cyan: #56c8ff;
      --violet: #b794f6;
      --logo-fg: #07090d;
      --backdrop: rgba(4, 6, 9, 0.55);
      --seg-count-bg: rgba(255, 255, 255, 0.08);
      --shadow: 0 16px 50px -16px rgba(0, 0, 0, 0.7);
    }}
    [data-theme="light"] {{
      --bg: #f0f3f8;
      --bg-2: #ffffff;
      --topbar-bg: rgba(255, 255, 255, 0.92);
      --glow-1: rgba(46, 184, 115, 0.12);
      --glow-2: rgba(37, 140, 220, 0.1);
      --surface: rgba(255, 255, 255, 0.95);
      --surface-2: rgba(240, 244, 250, 0.9);
      --surface-3: rgba(0, 0, 0, 0.04);
      --border: rgba(15, 23, 42, 0.1);
      --border-strong: rgba(15, 23, 42, 0.16);
      --text: #0f172a;
      --muted: #64748b;
      --faint: #94a3b8;
      --green: #16a34a;
      --green-dim: rgba(22, 163, 74, 0.12);
      --red: #dc2626;
      --red-dim: rgba(220, 38, 38, 0.1);
      --error-text: #991b1b;
      --cyan: #0284c7;
      --violet: #7c3aed;
      --logo-fg: #ffffff;
      --backdrop: rgba(15, 23, 42, 0.25);
      --seg-count-bg: rgba(15, 23, 42, 0.06);
      --shadow: 0 12px 40px -12px rgba(15, 23, 42, 0.12);
    }}
    :root {{
      --radius: 14px;
      --radius-sm: 10px;
      --topbar-h: 60px;
      --font: "Inter", ui-sans-serif, system-ui, -apple-system, sans-serif;
      --mono: "JetBrains Mono", ui-monospace, "SF Mono", monospace;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      font-family: var(--font);
      background: var(--bg);
      color: var(--text);
      line-height: 1.55;
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
      background-image:
        radial-gradient(900px circle at 8% -10%, var(--glow-1), transparent 42%),
        radial-gradient(900px circle at 100% -5%, var(--glow-2), transparent 42%);
      background-attachment: fixed;
    }}

    /* Top app bar */
    .topbar {{
      position: sticky; top: 0; z-index: 50;
      height: var(--topbar-h);
      display: flex; align-items: center; gap: 1rem;
      padding: 0 1.5rem;
      background: var(--topbar-bg);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--border);
    }}
    .brand {{ display: flex; align-items: center; gap: 0.7rem; }}
    .logo {{
      width: 34px; height: 34px; border-radius: 9px;
      background: linear-gradient(135deg, var(--green), var(--cyan));
      display: grid; place-items: center;
      font-weight: 800; font-size: 1.05rem; color: var(--logo-fg);
      box-shadow: 0 6px 18px -5px rgba(62, 207, 142, 0.5);
    }}
    .brand-title {{ font-size: 1rem; font-weight: 700; letter-spacing: -0.01em; }}
    .topbar-spacer {{ flex: 1; }}
    .topbar-meta {{ display: flex; align-items: center; gap: 1.1rem; font-size: 0.82rem; color: var(--muted); }}
    .topbar-meta .mv {{ color: var(--text); font-weight: 600; font-variant-numeric: tabular-nums; }}
    .topbar-meta .sep {{ width: 1px; height: 18px; background: var(--border-strong); }}
    .status-pill {{
      display: inline-flex; align-items: center; gap: 0.45rem;
      font-size: 0.78rem; font-weight: 700;
      padding: 0.35rem 0.8rem; border-radius: 999px;
      letter-spacing: 0.02em;
    }}
    .status-pill .pulse {{ width: 8px; height: 8px; border-radius: 50%; }}
    .status-pill.ok {{ background: var(--green-dim); color: var(--green); }}
    .status-pill.ok .pulse {{ background: var(--green); box-shadow: 0 0 0 4px rgba(61,220,132,0.18); }}
    .status-pill.bad {{ background: var(--red-dim); color: var(--red); }}
    .status-pill.bad .pulse {{ background: var(--red); box-shadow: 0 0 0 4px rgba(255,107,115,0.18); }}
    @media (max-width: 640px) {{ .topbar-meta .hide-sm {{ display: none; }} }}
    .theme-toggle {{
      display: inline-flex; align-items: center; gap: 0.35rem;
      padding: 0.35rem 0.65rem; border-radius: 999px;
      border: 1px solid var(--border); background: var(--surface-2);
      color: var(--muted); font-family: var(--font); font-size: 0.75rem; font-weight: 600;
      cursor: pointer; transition: color 0.15s, border-color 0.15s, background 0.15s;
    }}
    .theme-toggle:hover {{ color: var(--text); border-color: var(--border-strong); }}
    .theme-toggle svg {{ width: 15px; height: 15px; flex-shrink: 0; }}

    .wrap {{ max-width: 1080px; margin: 0 auto; padding: 1.75rem 1.5rem 2rem; }}

    /* Stats */
    .stats {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 0.9rem;
      margin-bottom: 1rem;
    }}
    @media (max-width: 640px) {{ .stats {{ grid-template-columns: repeat(2, 1fr); }} }}
    .stat {{
      position: relative;
      background: var(--surface);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.1rem 1.2rem;
      overflow: hidden;
      transition: transform 0.18s ease, border-color 0.18s ease;
    }}
    .stat::before {{ content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: var(--accent, var(--cyan)); }}
    .stat:hover {{ transform: translateY(-2px); border-color: var(--border-strong); }}
    .stat.total {{ --accent: var(--cyan); }}
    .stat.passed {{ --accent: var(--green); }}
    .stat.failed {{ --accent: var(--red); }}
    .stat.duration {{ --accent: var(--violet); }}
    .stat-label {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 0.45rem; }}
    .stat-value {{ font-size: 1.85rem; font-weight: 700; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }}
    .stat.passed .stat-value {{ color: var(--green); }}
    .stat.failed .stat-value {{ color: var(--red); }}
    .stat.duration .stat-value {{ color: var(--violet); }}

    /* Proportion bar */
    .ratebar-wrap {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1rem 1.2rem;
      margin-bottom: 1.75rem;
    }}
    .ratebar-top {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.6rem; font-size: 0.8rem; }}
    .ratebar-top .label {{ color: var(--muted); }}
    .ratebar-top .pct {{ font-weight: 700; font-size: 0.95rem; color: {('var(--green)' if all_passed else 'var(--text)')}; font-variant-numeric: tabular-nums; }}
    .ratebar {{ display: flex; height: 10px; border-radius: 999px; overflow: hidden; background: var(--surface-2); }}
    .ratebar .seg-pass {{ background: linear-gradient(90deg, var(--green), #2fb872); width: {passed_pct:.2f}%; transition: width 0.8s cubic-bezier(0.4,0,0.2,1); }}
    .ratebar .seg-fail {{ background: linear-gradient(90deg, #ff5a63, var(--red)); width: {failed_pct:.2f}%; transition: width 0.8s cubic-bezier(0.4,0,0.2,1); }}
    .ratebar-legend {{ display: flex; gap: 1.2rem; margin-top: 0.7rem; font-size: 0.75rem; color: var(--muted); }}
    .ratebar-legend .dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 0.4rem; }}
    .ratebar-legend .dot.pass {{ background: var(--green); }}
    .ratebar-legend .dot.fail {{ background: var(--red); }}

    /* Results panel */
    .panel {{
      display: flex; flex-direction: column;
      background: var(--surface);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow: hidden;
    }}
    .toolbar {{
      display: grid;
      grid-template-columns: auto auto 1fr auto;
      align-items: center;
      gap: 0.65rem 0.85rem;
      padding: 0.7rem 1.1rem;
      background: var(--bg-2);
      border-bottom: 1px solid var(--border);
    }}
    .toolbar-title {{
      font-size: 0.78rem; font-weight: 700;
      text-transform: uppercase; letter-spacing: 0.07em;
      color: var(--muted);
      white-space: nowrap;
    }}
    @media (max-width: 720px) {{
      .toolbar {{
        grid-template-columns: 1fr auto;
        grid-template-areas:
          "title count"
          "filters filters"
          "search search";
      }}
      .toolbar-title {{ grid-area: title; }}
      .segmented {{ grid-area: filters; justify-self: start; }}
      .search-box {{ grid-area: search; }}
      .toolbar .count {{ grid-area: count; justify-self: end; }}
    }}
    .segmented {{ display: inline-flex; background: var(--surface-2); border: 1px solid var(--border); border-radius: 999px; padding: 3px; gap: 2px; }}
    .seg {{
      display: inline-flex; align-items: center; gap: 0.4rem;
      border: none; background: transparent; cursor: pointer;
      color: var(--muted); font-family: var(--font); font-size: 0.78rem; font-weight: 600;
      padding: 0.35rem 0.8rem; border-radius: 999px; transition: color 0.15s, background 0.15s;
    }}
    .seg:hover {{ color: var(--text); }}
    .seg .seg-count {{ font-size: 0.7rem; background: var(--seg-count-bg); border-radius: 999px; padding: 0.02rem 0.42rem; font-variant-numeric: tabular-nums; }}
    .seg.active[data-filter="all"] {{ background: var(--surface-3); color: var(--text); }}
    .seg.active[data-filter="failed"] {{ background: var(--red-dim); color: var(--red); }}
    .seg.active[data-filter="passed"] {{ background: var(--green-dim); color: var(--green); }}
    .search-box {{ position: relative; min-width: 0; display: flex; align-items: center; }}
    .search-box svg {{ position: absolute; left: 0.7rem; color: var(--faint); pointer-events: none; }}
    .search {{
      width: 100%;
      background: var(--surface-2);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 0.5rem 0.85rem 0.5rem 2.1rem;
      color: var(--text); font-family: var(--font); font-size: 0.85rem; outline: none;
      transition: border-color 0.15s, box-shadow 0.15s;
    }}
    .search::placeholder {{ color: var(--faint); }}
    .search:focus {{ border-color: var(--cyan); box-shadow: 0 0 0 3px rgba(86,200,255,0.12); }}
    .toolbar .count {{ font-size: 0.75rem; color: var(--faint); white-space: nowrap; font-variant-numeric: tabular-nums; }}

    /* List */
    .list {{
      list-style: none;
      max-height: min(520px, calc(100vh - 340px));
      overflow-y: auto;
    }}
    .row {{
      display: grid;
      grid-template-columns: 14px 1fr auto 16px;
      align-items: center;
      gap: 0.9rem;
      padding: 0.85rem 1.25rem;
      border-bottom: 1px solid var(--border);
      cursor: pointer;
      border-left: 3px solid transparent;
      transition: background 0.13s, border-color 0.13s;
    }}
    .row:last-child {{ border-bottom: none; }}
    .row:hover {{ background: var(--surface-2); }}
    .row.active {{ background: var(--surface-2); border-left-color: var(--cyan); }}
    .dot {{ width: 9px; height: 9px; border-radius: 50%; }}
    .dot.passed {{ background: var(--green); box-shadow: 0 0 0 4px var(--green-dim); }}
    .dot.failed {{ background: var(--red); box-shadow: 0 0 0 4px var(--red-dim); }}
    .dot.unknown {{ background: var(--muted); }}
    .row-name {{ font-family: var(--mono); font-size: 0.86rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .row-meta {{ font-size: 0.74rem; color: var(--faint); font-family: var(--mono); white-space: nowrap; }}
    .row-meta.err {{ color: var(--red); }}
    .row-chevron {{ color: var(--faint); display: flex; }}
    .empty {{ padding: 3rem 1rem; text-align: center; color: var(--faint); font-size: 0.9rem; }}

    /* Drawer */
    .backdrop {{
      position: fixed; inset: 0; z-index: 60;
      background: var(--backdrop);
      backdrop-filter: blur(2px);
      opacity: 0; pointer-events: none;
      transition: opacity 0.25s ease;
    }}
    .backdrop.open {{ opacity: 1; pointer-events: auto; }}
    .drawer {{
      position: fixed; top: 0; right: 0; z-index: 70;
      width: min(520px, 94vw); height: 100vh;
      background: var(--bg-2);
      border-left: 1px solid var(--border-strong);
      box-shadow: -20px 0 60px -20px rgba(0,0,0,0.7);
      transform: translateX(100%);
      transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      display: flex; flex-direction: column;
    }}
    .drawer.open {{ transform: translateX(0); }}
    .drawer-head {{
      display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem;
      padding: 1.4rem 1.5rem 1.2rem;
      border-bottom: 1px solid var(--border);
    }}
    .drawer-title {{ font-family: var(--mono); font-size: 1.02rem; font-weight: 600; word-break: break-word; line-height: 1.4; }}
    .drawer-status {{
      display: inline-flex; align-items: center; gap: 0.4rem; margin-top: 0.6rem;
      font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700;
      padding: 0.25rem 0.65rem; border-radius: 999px;
    }}
    .drawer-status.passed {{ background: var(--green-dim); color: var(--green); }}
    .drawer-status.failed {{ background: var(--red-dim); color: var(--red); }}
    .drawer-status.unknown {{ background: var(--surface-2); color: var(--muted); }}
    .drawer-close {{
      flex-shrink: 0;
      width: 34px; height: 34px; border-radius: 9px;
      display: grid; place-items: center; cursor: pointer;
      background: var(--surface-2); border: 1px solid var(--border); color: var(--muted);
      transition: color 0.15s, border-color 0.15s;
    }}
    .drawer-close:hover {{ color: var(--text); border-color: var(--border-strong); }}
    .drawer-body {{ padding: 1.5rem; overflow-y: auto; flex: 1; }}
    .section-label {{ font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.09em; color: var(--faint); margin-bottom: 0.8rem; font-weight: 700; }}
    .error-box {{
      background: var(--red-dim);
      border: 1px solid rgba(255, 107, 115, 0.28);
      border-radius: var(--radius-sm);
      padding: 1rem 1.1rem;
      margin-bottom: 1.6rem;
      font-family: var(--mono); font-size: 0.82rem; white-space: pre-wrap; color: var(--error-text);
    }}
    .error-type {{ font-weight: 700; margin-bottom: 0.35rem; color: var(--red); }}
    .timeline {{ list-style: none; position: relative; padding-left: 0; }}
    .timeline::before {{ content: ""; position: absolute; left: 4px; top: 10px; bottom: 10px; width: 2px; background: linear-gradient(var(--border-strong), transparent); }}
    .tl-item {{ display: flex; gap: 1rem; padding: 0.55rem 0; font-size: 0.85rem; position: relative; animation: fadeUp 0.3s ease both; }}
    .tl-marker {{ width: 10px; height: 10px; border-radius: 50%; background: var(--violet); margin-top: 0.4rem; flex-shrink: 0; z-index: 1; box-shadow: 0 0 0 3px var(--bg-2); }}
    .tl-marker.resolve {{ background: var(--cyan); }}
    .tl-marker.teardown {{ background: var(--faint); }}
    .tl-marker.observed {{ background: var(--green); }}
    .tl-label {{ font-family: var(--mono); font-weight: 500; font-size: 0.82rem; }}
    .tl-detail {{ color: var(--muted); font-size: 0.78rem; margin-top: 0.1rem; font-family: var(--mono); }}
    @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}

    .report-footer {{
      margin-top: 1.5rem;
      text-align: center;
      font-size: 0.76rem;
      color: var(--faint);
    }}

    .list-scroll {{ scrollbar-width: thin; }}
    .list::-webkit-scrollbar {{ width: 8px; }}
    .list::-webkit-scrollbar-thumb {{ background: var(--border-strong); border-radius: 8px; }}
    .drawer-body::-webkit-scrollbar {{ width: 8px; }}
    .drawer-body::-webkit-scrollbar-thumb {{ background: var(--border-strong); border-radius: 8px; }}
  </style>
</head>
<body data-theme="dark">
  <div class="topbar">
    <div class="brand">
      <div class="logo">N</div>
      <span class="brand-title">Velaris Test Report</span>
    </div>
    <div class="topbar-spacer"></div>
    <div class="topbar-meta">
      <span class="hide-sm"><span class="mv">{report.total}</span> tests</span>
      <span class="sep hide-sm"></span>
      <span class="hide-sm"><span class="mv">{html.escape(duration)}</span></span>
      <span class="sep hide-sm"></span>
      <span class="status-pill {status_class}"><span class="pulse"></span>{html.escape(status_text)}</span>
      <button type="button" class="theme-toggle" id="theme-toggle" aria-label="Toggle theme">
        <svg id="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
        <span id="theme-label">Light</span>
      </button>
    </div>
  </div>

  <div class="wrap">
    <div class="stats">
      <div class="stat total">
        <div class="stat-label">Total</div>
        <div class="stat-value">{report.total}</div>
      </div>
      <div class="stat passed">
        <div class="stat-label">Passed</div>
        <div class="stat-value">{report.passed}</div>
      </div>
      <div class="stat failed">
        <div class="stat-label">Failed</div>
        <div class="stat-value">{report.failed}</div>
      </div>
      <div class="stat duration">
        <div class="stat-label">Duration</div>
        <div class="stat-value">{html.escape(duration)}</div>
      </div>
    </div>

    <div class="ratebar-wrap">
      <div class="ratebar-top">
        <span class="label">Pass rate</span>
        <span class="pct">{pass_rate}%</span>
      </div>
      <div class="ratebar">
        <div class="seg-pass"></div>
        <div class="seg-fail"></div>
      </div>
      <div class="ratebar-legend">
        <span><span class="dot pass"></span>{report.passed} passed</span>
        <span><span class="dot fail"></span>{report.failed} failed</span>
      </div>
    </div>

    <div class="panel">
      <div class="toolbar">
        <span class="toolbar-title">Results</span>
        <div class="segmented" id="filters">
          <button class="seg active" data-filter="all">All <span class="seg-count">{report.total}</span></button>
          <button class="seg" data-filter="failed">Failed <span class="seg-count">{report.failed}</span></button>
          <button class="seg" data-filter="passed">Passed <span class="seg-count">{report.passed}</span></button>
        </div>
        <div class="search-box">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"></circle><path d="m21 21-4.3-4.3"></path></svg>
          <input class="search" id="search" type="text" placeholder="Search tests…" autocomplete="off">
        </div>
        <span class="count" id="count"></span>
      </div>
      <ul class="list list-scroll" id="list"></ul>
    </div>

  </div>

  <footer class="report-footer">Report generated {html.escape(generated_at)}</footer>

  <div class="backdrop" id="backdrop"></div>
  <aside class="drawer" id="drawer" aria-hidden="true">
    <div class="drawer-head">
      <div>
        <div class="drawer-title" id="drawer-title"></div>
        <div id="drawer-status-wrap"></div>
      </div>
      <button class="drawer-close" id="drawer-close" aria-label="Close">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"></path></svg>
      </button>
    </div>
    <div class="drawer-body" id="drawer-body"></div>
  </aside>

  <script>
    (function initTheme() {{
      const stored = localStorage.getItem("velaris-report-theme");
      const theme = stored === "light" ? "light" : "dark";
      document.body.dataset.theme = theme;
      function syncLabels() {{
        const light = document.body.dataset.theme === "light";
        const el = document.getElementById("theme-label");
        if (el) el.textContent = light ? "Dark" : "Light";
      }}
      function toggle() {{
        const next = document.body.dataset.theme === "dark" ? "light" : "dark";
        document.body.dataset.theme = next;
        localStorage.setItem("velaris-report-theme", next);
        syncLabels();
      }}
      syncLabels();
      document.getElementById("theme-toggle")?.addEventListener("click", toggle);
    }})();

    const tests = {tests_json};

    const listEl = document.getElementById("list");
    const countEl = document.getElementById("count");
    const filtersEl = document.getElementById("filters");
    const searchEl = document.getElementById("search");
    const drawer = document.getElementById("drawer");
    const backdrop = document.getElementById("backdrop");

    function escapeHtml(text) {{
      const div = document.createElement("div");
      div.textContent = text == null ? "" : text;
      return div.innerHTML;
    }}
    function markerClass(type) {{
      if (type === "CapabilityResolved") return "resolve";
      if (type === "CapabilityTeardown") return "teardown";
      return "observed";
    }}

    // Failures-first ordering keeps the important rows at the top of large runs.
    const statusRank = {{ failed: 0, unknown: 1, passed: 2 }};
    const ordered = tests
      .map((t, i) => ({{ t, i }}))
      .sort((a, b) => (statusRank[a.t.status] ?? 1) - (statusRank[b.t.status] ?? 1) || a.i - b.i)
      .map(x => x.t);

    let activeName = null;
    let activeFilter = "all";
    let searchTerm = "";

    // Build each row node once; filtering re-appends existing nodes (no re-creation).
    const nodes = ordered.map((test) => {{
      const li = document.createElement("li");
      li.className = "row";
      li.dataset.status = test.status;
      li.dataset.name = test.name.toLowerCase();
      const meta = test.status === "failed"
        ? `<span class="row-meta err">${{escapeHtml(test.error_type || "failed")}}</span>`
        : `<span class="row-meta">${{test.timeline.length}} events</span>`;
      li.innerHTML = `
        <span class="dot ${{test.status}}"></span>
        <span class="row-name">${{escapeHtml(test.name)}}</span>
        ${{meta}}
        <span class="row-chevron"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="m9 18 6-6-6-6"></path></svg></span>
      `;
      li.addEventListener("click", () => openDetail(test));
      return {{ test, li }};
    }});

    function applyView() {{
      const frag = document.createDocumentFragment();
      let shown = 0;
      for (const {{ test, li }} of nodes) {{
        const matchFilter = activeFilter === "all" || test.status === activeFilter;
        const matchSearch = !searchTerm || li.dataset.name.includes(searchTerm);
        if (!(matchFilter && matchSearch)) continue;
        li.classList.toggle("active", test.name === activeName);
        frag.appendChild(li);
        shown++;
      }}
      listEl.innerHTML = "";
      if (shown === 0) {{
        listEl.innerHTML = `<li class="empty">No matching tests</li>`;
      }} else {{
        listEl.appendChild(frag);
      }}
      countEl.textContent = `Showing ${{shown}} of ${{tests.length}}`;
    }}

    function openDetail(test) {{
      activeName = test.name;
      nodes.forEach(n => n.li.classList.toggle("active", n.test.name === test.name));
      document.getElementById("drawer-title").textContent = test.name;
      document.getElementById("drawer-status-wrap").innerHTML =
        `<span class="drawer-status ${{test.status}}">${{escapeHtml(test.status)}}</span>`;

      let body = "";
      if (test.status === "failed" && (test.message || test.error_type)) {{
        body += `<div class="section-label">Failure</div><div class="error-box">`;
        if (test.error_type) body += `<div class="error-type">${{escapeHtml(test.error_type)}}</div>`;
        if (test.message) body += escapeHtml(test.message);
        body += `</div>`;
      }}
      body += `<div class="section-label">Capability timeline</div>`;
      if (test.timeline.length === 0) {{
        body += `<p class="empty" style="padding:1.5rem 0">No capability events recorded</p>`;
      }} else {{
        body += `<ul class="timeline">`;
        test.timeline.forEach((ev, i) => {{
          body += `<li class="tl-item" style="animation-delay:${{i * 0.03}}s">
            <span class="tl-marker ${{markerClass(ev.type)}}"></span>
            <div>
              <div class="tl-label">${{escapeHtml(ev.label)}}</div>
              ${{ev.detail ? `<div class="tl-detail">${{escapeHtml(ev.detail)}}</div>` : ""}}
            </div>
          </li>`;
        }});
        body += `</ul>`;
      }}
      document.getElementById("drawer-body").innerHTML = body;
      drawer.classList.add("open");
      backdrop.classList.add("open");
      drawer.setAttribute("aria-hidden", "false");
    }}

    function closeDetail() {{
      drawer.classList.remove("open");
      backdrop.classList.remove("open");
      drawer.setAttribute("aria-hidden", "true");
      activeName = null;
      nodes.forEach(n => n.li.classList.remove("active"));
    }}

    let searchTimer = null;
    searchEl && searchEl.addEventListener("input", (e) => {{
      clearTimeout(searchTimer);
      const val = e.target.value;
      searchTimer = setTimeout(() => {{ searchTerm = val.toLowerCase(); applyView(); }}, 110);
    }});

    filtersEl && filtersEl.addEventListener("click", (e) => {{
      const seg = e.target.closest(".seg");
      if (!seg) return;
      activeFilter = seg.dataset.filter;
      filtersEl.querySelectorAll(".seg").forEach(s => s.classList.toggle("active", s === seg));
      applyView();
    }});

    document.getElementById("drawer-close").addEventListener("click", closeDetail);
    backdrop.addEventListener("click", closeDetail);
    document.addEventListener("keydown", (e) => {{ if (e.key === "Escape") closeDetail(); }});

    if (tests.length === 0) {{
      listEl.innerHTML = `<li class="empty">No tests found in event log</li>`;
      countEl.textContent = "";
    }} else {{
      applyView();
    }}
  </script>
</body>
</html>"""


def _test_to_dict(test: TestReport) -> dict:
    return {
        "name": test.name,
        "status": test.status,
        "message": test.message,
        "error_type": test.error_type,
        "timeline": [
            {"type": e.type, "label": e.label, "detail": e.detail}
            for e in test.timeline
        ],
    }
