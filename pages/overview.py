"""Illustrative cybersecurity dashboard; all preview metrics are synthetic."""

from __future__ import annotations

from datetime import date

import streamlit as st


from core.config import Settings
from core.dashboard_demo import (
    DEMO_CATEGORIES,
    DEMO_INVESTIGATIONS,
    DEMO_METRICS,
    dashboard_demo_allowed,
)


def get_page_link(name: str):
    """Resolve page references at render time to avoid navigation import cycles."""
    from components.navigation import get_page_link as resolve_page_link

    return resolve_page_link(name)


def _render_metric_cards() -> None:
    columns = st.columns(4, gap="medium")
    for column, metric in zip(columns, DEMO_METRICS):
        with column:
            st.markdown(
                f'<div class="ss-kpi-card" style="--ss-kpi-accent:{metric["accent"]}">'
                f'<div class="ss-kpi-head"><span>{metric["label"]}</span>'
                f'<span class="ss-kpi-icon">{metric["icon"]}</span></div>'
                f'<div class="ss-kpi-value-row"><span class="ss-kpi-value">{metric["value"]}</span>'
                f'<span class="ss-kpi-change">{metric["change"]}</span></div>'
                f'<div class="ss-kpi-foot">{metric["foot"]}</div></div>',
                unsafe_allow_html=True,
            )


def _render_activity_chart() -> None:
    st.markdown(
        '<div class="ss-viz-card">'
        '<div class="ss-viz-head"><div><div class="ss-viz-title">Investigation activity</div>'
        '<div class="ss-viz-subtitle">Sample volume over the last seven days</div></div>'
        '<span class="ss-viz-tag">DEMO TREND</span></div>'
        '<svg class="ss-trend-svg" viewBox="0 0 640 220" role="img" aria-label="Illustrative activity trend rising from Monday through Sunday">'
        '<defs><linearGradient id="ssTrendFill" x1="0" x2="0" y1="0" y2="1">'
        '<stop offset="0%" stop-color="var(--ss-primary)" stop-opacity=".30"/>'
        '<stop offset="100%" stop-color="var(--ss-primary)" stop-opacity=".015"/>'
        '</linearGradient></defs>'
        '<line class="ss-trend-grid" x1="24" y1="34" x2="620" y2="34"/>'
        '<line class="ss-trend-grid" x1="24" y1="82" x2="620" y2="82"/>'
        '<line class="ss-trend-grid" x1="24" y1="130" x2="620" y2="130"/>'
        '<line class="ss-trend-grid" x1="24" y1="178" x2="620" y2="178"/>'
        '<path class="ss-trend-area" d="M24 151 L123 126 L222 139 L321 91 L420 108 L519 49 L618 70 L618 178 L24 178 Z"/>'
        '<polyline class="ss-trend-line" points="24,151 123,126 222,139 321,91 420,108 519,49 618,70"/>'
        '<circle class="ss-trend-point" cx="24" cy="151" r="4"/><circle class="ss-trend-point" cx="123" cy="126" r="4"/>'
        '<circle class="ss-trend-point" cx="222" cy="139" r="4"/><circle class="ss-trend-point" cx="321" cy="91" r="4"/>'
        '<circle class="ss-trend-point" cx="420" cy="108" r="4"/><circle class="ss-trend-point" cx="519" cy="49" r="4"/>'
        '<circle class="ss-trend-point" cx="618" cy="70" r="4"/></svg>'
        '<div class="ss-chart-labels"><span>MON</span><span>TUE</span><span>WED</span><span>THU</span><span>FRI</span><span>SAT</span><span>SUN</span></div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _render_risk_distribution() -> None:
    st.markdown(
        '<div class="ss-viz-card">'
        '<div class="ss-viz-head"><div><div class="ss-viz-title">Risk distribution</div>'
        '<div class="ss-viz-subtitle">Illustrative assessment mix</div></div>'
        '<span class="ss-viz-tag">DEMO</span></div>'
        '<div class="ss-risk-layout"><div class="ss-donut"><div class="ss-donut-center">'
        '<b>1,284</b><span>SAMPLE ITEMS</span></div></div><div class="ss-legend">'
        '<div class="ss-legend-row"><i class="ss-legend-dot" style="background:var(--ss-danger)"></i><span>Critical</span><b>17%</b></div>'
        '<div class="ss-legend-row"><i class="ss-legend-dot" style="background:var(--ss-warning)"></i><span>High</span><b>30%</b></div>'
        '<div class="ss-legend-row"><i class="ss-legend-dot" style="background:var(--ss-primary)"></i><span>Moderate</span><b>29%</b></div>'
        '<div class="ss-legend-row"><i class="ss-legend-dot" style="background:var(--ss-success)"></i><span>Low</span><b>24%</b></div>'
        '</div></div></div>',
        unsafe_allow_html=True,
    )


def _render_pattern_categories() -> None:
    rows = []
    for label, percentage, color in DEMO_CATEGORIES:
        rows.append(
            f'<div><div class="ss-category-top"><span>{label}</span><b>{percentage}%</b></div>'
            f'<div class="ss-category-track"><div class="ss-category-fill" '
            f'style="width:{percentage}%;background:{color}"></div></div></div>'
        )
    st.markdown(
        '<div class="ss-viz-card"><div class="ss-viz-head"><div>'
        '<div class="ss-viz-title">Frequently observed patterns</div>'
        '<div class="ss-viz-subtitle">Synthetic category illustration</div></div>'
        '<span class="ss-viz-tag">DEMO</span></div>'
        f'<div class="ss-category-list">{"".join(rows)}</div></div>',
        unsafe_allow_html=True,
    )


def _render_risk_score() -> None:
    st.markdown(
        '<div class="ss-viz-card"><div class="ss-viz-head"><div>'
        '<div class="ss-viz-title">Sample risk index</div>'
        '<div class="ss-viz-subtitle">Visual example of a future assessment widget</div></div>'
        '<span class="ss-viz-tag">NOT LIVE</span></div>'
        '<div class="ss-score-layout"><div class="ss-score-ring"><div class="ss-score-value">72<small>/100</small></div></div>'
        '<div class="ss-score-copy"><b>Elevated · illustrative</b>'
        '<p>This is a synthetic design example, not a score calculated from your messages, cases or threat intelligence.</p>'
        '</div></div></div>',
        unsafe_allow_html=True,
    )


def _render_recent_activity() -> None:
    rows = []
    for title, kind, risk, when in DEMO_INVESTIGATIONS:
        risk_class = {"High": "high", "Medium": "medium", "Low": "low"}[risk]
        rows.append(
            f'<tr><td>{title}</td><td>{kind}</td>'
            f'<td><span class="ss-risk-badge ss-risk-{risk_class}">{risk}</span></td>'
            f'<td>{when}</td></tr>'
        )
    st.markdown(
        '<div class="ss-viz-card"><div class="ss-viz-head"><div>'
        '<div class="ss-viz-title">Recent investigation examples</div>'
        '<div class="ss-viz-subtitle">Fictional records to preview the future activity table</div></div>'
        '<span class="ss-viz-tag">SAMPLE RECORDS</span></div>'
        '<div style="overflow-x:auto"><table class="ss-sample-table"><thead><tr>'
        '<th>SUBJECT</th><th>TYPE</th><th>RISK</th><th>WHEN</th></tr></thead><tbody>'
        f'{"".join(rows)}</tbody></table></div></div>',
        unsafe_allow_html=True,
    )


def _render_empty_dashboard() -> None:
    st.markdown(
        '<div class="ss-panel"><div class="ss-panel-title">Your workspace is ready</div>'
        '<div class="ss-panel-copy">There are no saved investigations or analysis records yet. '
        'Once the analysis and persistence milestones are complete, this dashboard will show '
        'your own results here.</div></div>',
        unsafe_allow_html=True,
    )
    st.page_link(
        get_page_link("new_investigation"),
        label="Start your first investigation",
        icon=":material/arrow_forward:",
    )


def render() -> None:
    """Render SOC-inspired DEMONSTRATION DATA; these are not real investigations."""
    settings = Settings.from_env()
    st.markdown("""
    <style>
    .matrix-shell{background:linear-gradient(135deg,#07110b,#050907 65%,#0a1b10);border:1px solid #1b5630;border-radius:22px;padding:1.15rem;box-shadow:0 0 35px #39ff1410,inset 0 0 30px #39ff1408}
    .matrix-head{display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap;border-bottom:1px solid #183a25;padding:.25rem .2rem 1rem;margin-bottom:1rem}
    .matrix-kicker{color:#39ff14;font-size:.68rem;letter-spacing:.18em;font-weight:800}.matrix-title{font-size:1.65rem;font-weight:760;color:#e0ffe8;margin:.25rem 0}.matrix-sub{color:#8db99a;font-size:.8rem}
    .matrix-badge{border:1px solid #246b3b;border-radius:99px;padding:.35rem .7rem;color:#39ff14;font-size:.68rem;letter-spacing:.08em;background:#39ff140b}
    .matrix-grid{display:grid;grid-template-columns:minmax(220px,.85fr) minmax(320px,1.7fr) minmax(220px,.9fr);gap:.8rem;align-items:stretch}
    .matrix-card{background:linear-gradient(160deg,#0d1b11,#09120c);border:1px solid #19452a;border-radius:14px;padding:1rem;min-width:0;box-shadow:inset 0 1px #39ff1409}
    .matrix-card h4{font-size:.85rem;margin:0 0 .25rem;color:#e0ffe8}.matrix-caption{color:#72977d;font-size:.68rem;margin-bottom:.8rem}
    .matrix-gauge{width:100%;max-width:245px;display:block;margin:.2rem auto}.matrix-score{text-align:center;margin-top:-2.1rem;font-size:1.8rem;color:#e0ffe8;font-weight:750}.matrix-score small{font-size:.7rem;color:#81a98b}.matrix-status{text-align:center;color:#39ff14;font-size:.73rem;margin:.2rem 0 .9rem}
    .matrix-stat{display:flex;justify-content:space-between;gap:.5rem;padding:.45rem 0;border-top:1px solid #183421;color:#91b59b;font-size:.72rem}.matrix-stat b{color:#dfffe5}
    .matrix-topology{width:100%;height:auto;min-height:210px}.matrix-node{fill:#102b19;stroke:#39ff14;stroke-width:1.5}.matrix-link{stroke:#2a8e48;stroke-width:2;fill:none;opacity:.9}.matrix-node-text{fill:#dfffe5;font-size:11px;text-anchor:middle}
    .matrix-attrib{display:flex;align-items:center;gap:.6rem;margin:.8rem 0;color:#a5c9ae;font-size:.72rem}.matrix-attrib-bar{height:7px;background:#172d1d;border-radius:99px;overflow:hidden;flex:1}.matrix-attrib-bar i{height:100%;display:block;background:linear-gradient(90deg,#16803a,#39ff14);border-radius:99px}
    .matrix-incident{display:flex;gap:.6rem;align-items:flex-start;border-top:1px solid #183421;padding:.65rem 0;font-size:.7rem;color:#b4d3bc}.matrix-dot{width:7px;height:7px;flex:none;border-radius:50%;background:#39ff14;box-shadow:0 0 8px #39ff1480;margin-top:.3rem}.matrix-tag{margin-left:auto;color:#39ff14;border:1px solid #246b3b;padding:.15rem .35rem;border-radius:5px;font-size:.6rem;white-space:nowrap}
    .matrix-lower{display:grid;grid-template-columns:1.2fr 1fr;gap:.8rem;margin-top:.8rem}.matrix-kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:.6rem;margin:.8rem 0}.matrix-kpi{background:#0a170e;border:1px solid #19452a;border-radius:12px;padding:.8rem}.matrix-kpi strong{display:block;color:#e0ffe8;font-size:1.45rem}.matrix-kpi span{color:#7fa98a;font-size:.66rem}
    @media(max-width:900px){.matrix-grid{grid-template-columns:1fr}.matrix-lower{grid-template-columns:1fr}.matrix-kpis{grid-template-columns:repeat(2,1fr)}}
    </style>
    <div class="matrix-shell">
      <div class="matrix-head"><div><div class="matrix-kicker">SCAMSHIELD / SECURITY OPERATIONS</div><div class="matrix-title">Incidents Management</div><div class="matrix-sub">Monitor, investigate, prioritize and resolve suspicious activity.</div></div><span class="matrix-badge">● MATRIX GREEN THEME</span></div>
      <div class="matrix-grid">
        <section class="matrix-card"><h4>Investigation Health Score</h4><div class="matrix-caption">Illustrative gauge · not a live score</div>
          <svg class="matrix-gauge" viewBox="0 0 240 135" role="img" aria-label="Illustrative score gauge"><path d="M25 115 A95 95 0 0 1 215 115" stroke="#183421" stroke-width="12" fill="none" stroke-linecap="round"/><path d="M25 115 A95 95 0 0 1 191 45" stroke="#39ff14" stroke-width="12" fill="none" stroke-linecap="round"/><path d="M25 115 A95 95 0 0 1 55 48" stroke="#a3e635" stroke-width="3" fill="none"/><circle cx="191" cy="45" r="5" fill="#e0ffe8"/></svg>
          <div class="matrix-score">72<small>/100</small></div><div class="matrix-status">ELEVATED · SAMPLE ONLY</div>
          <div class="matrix-stat"><span>Open cases</span><b>38</b></div><div class="matrix-stat"><span>Critical examples</span><b>5</b></div><div class="matrix-stat"><span>Avg. resolution</span><b>18m</b></div><div class="matrix-stat"><span>SLA compliance</span><b>97%</b></div>
        </section>
        <section class="matrix-card"><h4>Network Topology</h4><div class="matrix-caption">Illustrative relationship map · synthetic nodes</div>
          <svg class="matrix-topology" viewBox="0 0 520 245" role="img" aria-label="Illustrative network topology diagram"><path class="matrix-link" d="M55 120 Q105 75 155 120 T255 120 T355 65 T455 110"/><path class="matrix-link" d="M155 120 Q210 190 255 120 T355 175 T455 110"/><path class="matrix-link" d="M255 120 L255 205"/>
          <circle class="matrix-node" cx="55" cy="120" r="20"/><circle class="matrix-node" cx="155" cy="120" r="20"/><circle class="matrix-node" cx="255" cy="120" r="20"/><circle class="matrix-node" cx="355" cy="65" r="20"/><circle class="matrix-node" cx="355" cy="175" r="20"/><circle class="matrix-node" cx="455" cy="110" r="20"/><circle class="matrix-node" cx="255" cy="205" r="17"/>
          <g class="matrix-node-text"><text x="55" y="124">SRC</text><text x="155" y="124">DNS</text><text x="255" y="124">GW</text><text x="355" y="69">WS-01</text><text x="355" y="179">WS-03</text><text x="455" y="114">EXT</text><text x="255" y="209">IOC</text></g></svg>
          <div class="matrix-caption">Green connections indicate illustrative relationships, not verified network telemetry.</div>
          <div class="matrix-attrib"><span>Credential phishing</span><div class="matrix-attrib-bar"><i style="width:72%"></i></div><b>72%</b></div><div class="matrix-attrib"><span>Suspicious redirects</span><div class="matrix-attrib-bar"><i style="width:48%"></i></div><b>48%</b></div><div class="matrix-attrib"><span>Impersonation patterns</span><div class="matrix-attrib-bar"><i style="width:31%"></i></div><b>31%</b></div>
        </section>
        <section class="matrix-card"><h4>Incident Timeline</h4><div class="matrix-caption">Sample workflow events · fictional</div>
          <div class="matrix-incident"><i class="matrix-dot"></i><span>Detection<br><small>Suspicious URL submitted</small></span><b class="matrix-tag">REVIEW</b></div><div class="matrix-incident"><i class="matrix-dot"></i><span>Investigation started<br><small>Structural analysis</small></span><b class="matrix-tag">ACTIVE</b></div><div class="matrix-incident"><i class="matrix-dot"></i><span>Indicators reviewed<br><small>Evidence pending</small></span><b class="matrix-tag">PENDING</b></div><div class="matrix-incident"><i class="matrix-dot"></i><span>Resolution<br><small>No live verdict generated</small></span><b class="matrix-tag">OPEN</b></div>
          <div class="matrix-caption" style="margin-top:1rem">Threat attribution</div><div class="matrix-attrib"><span>Phishing</span><div class="matrix-attrib-bar"><i style="width:68%"></i></div></div><div class="matrix-attrib"><span>Malware delivery</span><div class="matrix-attrib-bar"><i style="width:42%"></i></div></div><div class="matrix-attrib"><span>Account abuse</span><div class="matrix-attrib-bar"><i style="width:25%"></i></div></div>
        </section>
      </div>
      <div class="matrix-kpis"><div class="matrix-kpi"><strong>38</strong><span>ACTIVE CASES · SAMPLE</span></div><div class="matrix-kpi"><strong>05</strong><span>PRIORITY REVIEWS · SAMPLE</span></div><div class="matrix-kpi"><strong>127</strong><span>CLOSED EXAMPLES · SAMPLE</span></div><div class="matrix-kpi"><strong>12m</strong><span>MEAN RESPONSE · SAMPLE</span></div></div>
      <div class="matrix-lower"><section class="matrix-card"><h4>Threat Attribution</h4><div class="matrix-caption">Illustrative pattern categories, not actor attribution</div><div class="matrix-attrib"><span>Phishing / credential theft</span><div class="matrix-attrib-bar"><i style="width:76%"></i></div><b>76%</b></div><div class="matrix-attrib"><span>Brand impersonation</span><div class="matrix-attrib-bar"><i style="width:58%"></i></div><b>58%</b></div><div class="matrix-attrib"><span>Suspicious redirect</span><div class="matrix-attrib-bar"><i style="width:43%"></i></div><b>43%</b></div><div class="matrix-attrib"><span>Unusual hostname</span><div class="matrix-attrib-bar"><i style="width:27%"></i></div><b>27%</b></div></section><section class="matrix-card"><h4>Threat Radar</h4><div class="matrix-caption">Use the tools to create real records; this preview contains no live intelligence.</div><div class="matrix-incident"><i class="matrix-dot"></i><span>URL Analyzer<br><small>Inspect links without opening them</small></span></div><div class="matrix-incident"><i class="matrix-dot"></i><span>Message Analyzer<br><small>Review suspicious text locally</small></span></div></section></div>
      <div style="color:#6f9b7b;font-size:.65rem;margin-top:1rem">DEVELOPMENT PREVIEW — all gauges, metrics, topology and attribution percentages above are synthetic UI examples, not real cases or verified threat intelligence.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div style="height:.7rem"></div>', unsafe_allow_html=True)
    actions = st.columns(3, gap="medium")
    for col, label, page, icon in [
        (actions[0], "New investigation", "new_investigation", ":material/add_circle:"),
        (actions[1], "URL Analyzer", "url_analyzer", ":material/link:"),
        (actions[2], "Message Analyzer", "message_analyzer", ":material/mark_email_unread:")]:
        with col:
            st.page_link(get_page_link(page), label=label, icon=icon, use_container_width=True)
    if not dashboard_demo_allowed(settings.environment):
        st.warning("This dashboard is a design preview. Synthetic metrics are disabled outside development mode.")
