"""Theme definitions and CSS for the shared application shell."""

from __future__ import annotations

from typing import Mapping

SUPPORTED_THEMES = ("dark", "light")

THEME_TOKENS: Mapping[str, Mapping[str, str]] = {
    "dark": {
        "background": "#050A07",
        "surface": "#0C1710",
        "surface_elevated": "#102018",
        "surface_interactive": "#142B1C",
        "text": "#E0FFE8",
        "muted": "#A5C9AE",
        "subtle": "#6E967B",
        "border": "#14532D",
        "primary": "#39FF14",
        "primary_strong": "#16A34A",
        "blue": "#86EFAC",
        "violet": "#A3E635",
        "neon_pink": "#4ADE80",
        "success": "#39FF14",
        "warning": "#FFD166",
        "danger": "#FF5C8A",
        "chart_grid": "#183A25",
        "chart_track": "#142B1C",
        "icon": "#A5C9AE",
    },
    "light": {
        "background": "#F4F6FC",
        "surface": "#FFFFFF",
        "surface_elevated": "#FAFBFF",
        "surface_interactive": "#EEF1FF",
        "text": "#18213A",
        "muted": "#52607A",
        "subtle": "#7885A0",
        "border": "#E1E6F1",
        "primary": "#5758D6",
        "primary_strong": "#4546BC",
        "blue": "#238CCB",
        "violet": "#8557D8",
        "neon_pink": "#C34B9A",
        "success": "#168466",
        "warning": "#A56A16",
        "danger": "#C9435B",
        "chart_grid": "#E5E9F3",
        "chart_track": "#E9EDF7",
        "icon": "#596783",
    },
}


def normalize_theme(value: str | None) -> str:
    """Return a supported theme name, defaulting safely to dark."""
    candidate = (value or "").strip().lower()
    return candidate if candidate in SUPPORTED_THEMES else "dark"


def theme_css(theme: str) -> str:
    """Build the application stylesheet from a vetted theme token set."""
    tokens = THEME_TOKENS[normalize_theme(theme)]
    variables = "\n".join(
        f"    --ss-{name.replace('_', '-')}: {value};"
        for name, value in tokens.items()
    )

    light_overrides = ""
    if normalize_theme(theme) == "light":
        light_overrides = """
/* Premium light workspace: cool porcelain surfaces with indigo, violet and cyan accents. */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--ss-background);
    background-image:
        radial-gradient(ellipse at 8% 0%, rgba(119, 117, 232, .12), transparent 38%),
        radial-gradient(ellipse at 94% 8%, rgba(55, 164, 211, .10), transparent 34%),
        linear-gradient(rgba(87, 88, 214, .022) 1px, transparent 1px),
        linear-gradient(90deg, rgba(87, 88, 214, .022) 1px, transparent 1px);
    background-size: auto, auto, 48px 48px, 48px 48px;
}
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, .90) !important;
    border-right: 1px solid #E1E6F1;
    box-shadow: 8px 0 32px rgba(31, 45, 86, .035);
}
[data-testid="stSidebar"] > div:first-child { background: transparent !important; }
[data-testid="stMetric"], .ss-panel, .ss-viz-card, .ss-kpi-card,
.ss-preview-shell, [data-testid="stExpander"] {
    box-shadow: 0 8px 26px rgba(34, 48, 91, .045),
                0 1px 2px rgba(34, 48, 91, .035);
}
[data-testid="stMetric"], .ss-panel, .ss-viz-card, .ss-kpi-card {
    border-color: #E3E8F3;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stNumberInput"] input {
    background: #FFFFFF !important;
    border-color: #DCE3F0 !important;
    color: #18213A !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #7778E4 !important;
    box-shadow: 0 0 0 3px rgba(87, 88, 214, .12) !important;
}
[data-testid="stButton"] button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #6263DF, #4C4FC5) !important;
    border: 1px solid #5557CE !important;
    color: #FFFFFF !important;
    box-shadow: 0 5px 14px rgba(87, 88, 214, .20);
}
[data-testid="stButton"] button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] button[kind="primary"]:hover {
    background: linear-gradient(135deg, #5557D1, #4144B8) !important;
    box-shadow: 0 7px 18px rgba(87, 88, 214, .25);
}
[data-testid="stTabs"] button[aria-selected="true"] { color: #4D4FC6 !important; }
.ss-brand-mark, .ss-public-brand-mark {
    background: linear-gradient(145deg, #F0F0FF, #E8F5FF);
    border-color: #D9DDF8;
    box-shadow: 0 5px 16px rgba(87, 88, 214, .10);
}
.ss-neon-callout {
    background: linear-gradient(120deg, rgba(87,88,214,.075), rgba(35,140,203,.045)), #FFFFFF;
    border-color: #DADFF5;
    box-shadow: 0 8px 22px rgba(58, 67, 133, .045);
}
.ss-dashboard-hero {
    background: radial-gradient(circle at 90% 0%, rgba(87,88,214,.10), transparent 36%),
                linear-gradient(135deg, #FFFFFF, #F8FAFF);
    box-shadow: 0 10px 30px rgba(34,48,91,.045);
}
.ss-status, .ss-live-pill { background: rgba(255,255,255,.78); }
"""

    return f"""
<style>
:root {{
{variables}
    color-scheme: {normalize_theme(theme)};
}}

.stApp {{
    --primary-color: var(--ss-primary);
    --background-color: var(--ss-background);
    --secondary-background-color: var(--ss-surface);
    --text-color: var(--ss-text);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
                 "Segoe UI", sans-serif;
    isolation: isolate;
}}
/* Galaxy-scale black hole: layered nebula, tilted accretion disc, and looping inward star particles. */
#scamshield-cosmos {{
    position: fixed; inset: 0; z-index: 0; overflow: hidden; pointer-events: none;
    opacity: {"0.88" if normalize_theme(theme) == "dark" else "0.20"};
    isolation: isolate;
}}
#scamshield-cosmos .ss-cosmos-stars {{
    position: absolute; inset: -20%;
    background-image:
      radial-gradient(1px 1px at 8% 18%, rgba(224,255,232,.82) 50%, transparent 100%),
      radial-gradient(1.5px 1.5px at 22% 72%, rgba(57,255,20,.78) 50%, transparent 100%),
      radial-gradient(1px 1px at 68% 28%, rgba(224,255,232,.78) 50%, transparent 100%),
      radial-gradient(2px 2px at 82% 64%, rgba(163,230,53,.82) 50%, transparent 100%),
      radial-gradient(1px 1px at 46% 44%, rgba(224,255,232,.68) 50%, transparent 100%),
      radial-gradient(ellipse at 76% 45%, rgba(57,255,20,.08), transparent 38%),
      radial-gradient(ellipse at 75% 45%, rgba(20,163,74,.10), transparent 54%);
    background-size: 390px 310px, 470px 380px, 520px 420px, 440px 360px, 600px 500px, 100% 100%, 100% 100%;
    animation: ss-star-drift 42s linear infinite;
}}
#scamshield-cosmos .ss-black-hole {{
    position: absolute; width: clamp(520px, 78vw, 1120px); height: clamp(520px, 78vw, 1120px);
    top: 50%; left: 74%; transform: translate(-50%, -50%); border-radius: 50%;
    background: radial-gradient(ellipse at center, transparent 0 12%, rgba(0,0,0,.12) 17%, transparent 27%, rgba(57,255,20,.045) 34%, transparent 58%);
    filter: drop-shadow(0 0 54px rgba(57,255,20,.10));
    animation: ss-hole-float 24s ease-in-out infinite alternate;
}}
#scamshield-cosmos .ss-galaxy-halo {{
    position:absolute; inset:8%; border-radius:50%;
    background:radial-gradient(ellipse, transparent 0 25%, rgba(57,255,20,.08) 39%, rgba(22,163,74,.12) 43%, rgba(163,230,53,.05) 49%, transparent 66%);
    filter:blur(8px); transform:rotateX(68deg) rotateZ(-18deg);
}}
#scamshield-cosmos .ss-accretion-disc {{
    position: absolute; inset: 13%; border-radius: 50%;
    background: conic-gradient(from 20deg, transparent 0deg, rgba(57,255,20,.03) 22deg,
      rgba(57,255,20,.55) 52deg, rgba(163,230,53,.75) 76deg,
      rgba(224,255,232,.88) 88deg, rgba(22,163,74,.42) 112deg,
      transparent 145deg, transparent 220deg, rgba(57,255,20,.08) 250deg,
      rgba(22,163,74,.48) 285deg, transparent 330deg, transparent 360deg);
    transform: rotateX(68deg) rotateZ(-18deg);
    box-shadow: 0 0 35px rgba(57,255,20,.18), inset 0 0 42px rgba(163,230,53,.12);
    mask: radial-gradient(ellipse, transparent 0 35%, #000 42% 59%, transparent 67%);
    animation: ss-disc-spin 26s linear infinite;
}}
#scamshield-cosmos .ss-photon-ring {{
    position: absolute; inset: 28%; border-radius: 50%; border: 2px solid rgba(163,230,53,.58);
    box-shadow: 0 0 18px rgba(57,255,20,.35), 0 0 55px rgba(57,255,20,.20), inset 0 0 18px rgba(57,255,20,.2);
    transform: rotateX(68deg) rotateZ(-18deg);
}}
#scamshield-cosmos .ss-event-horizon {{
    position: absolute; inset: 34%; border-radius: 50%;
    background: radial-gradient(circle at 40% 35%, #010301 0%, #000 68%);
    box-shadow: 0 0 0 4px rgba(0,0,0,.95), 0 0 45px 18px rgba(0,0,0,.92), 0 0 70px rgba(57,255,20,.16);
}}
#scamshield-cosmos .ss-star-orbit {{
    position:absolute; inset:var(--orbit-inset); border:1px solid rgba(57,255,20,.13); border-radius:50%;
    transform:rotateX(68deg) rotateZ(var(--orbit-angle)); animation:ss-orbit-turn var(--orbit-duration) linear infinite;
}}
#scamshield-cosmos .ss-star {{
    position:absolute; top:0; left:50%; width:var(--star-size); height:var(--star-size); border-radius:50%;
    background:#E0FFE8; box-shadow:0 0 8px 2px rgba(57,255,20,.82),0 0 20px rgba(163,230,53,.7);
    transform:translate(-50%,-50%); animation:ss-star-infall var(--infall-duration) ease-in-out infinite;
    animation-delay:var(--star-delay);
}}
[data-testid="stMain"], [data-testid="stSidebar"] {{ position: relative; z-index: 1; }}
[data-testid="stSidebar"] {{ background: color-mix(in srgb, var(--ss-surface) 94%, transparent); }}
html, body, [data-testid="stAppViewContainer"] {{
    background-color: var(--ss-background);
    background-image:
        radial-gradient(ellipse at 50% -12%, color-mix(in srgb, var(--ss-primary) 9%, transparent), transparent 58%),
        linear-gradient(color-mix(in srgb, var(--ss-primary) 3%, transparent) 1px, transparent 1px),
        linear-gradient(90deg, color-mix(in srgb, var(--ss-primary) 3%, transparent) 1px, transparent 1px);
    background-size: auto, 46px 46px, 46px 46px;
    color: var(--ss-text);
}}
{light_overrides}
*:focus-visible {{
    outline: 2px solid var(--ss-primary);
    outline-offset: 2px;
}}
[data-testid="stHeader"] {{
    background: transparent;
}}
[data-testid="stSidebar"] {{
    background: var(--ss-surface);
    border-right: 1px solid var(--ss-border);
}}
[data-testid="stSidebar"] > div:first-child {{
    background: var(--ss-surface);
}}
[data-testid="stMainBlockContainer"] {{
    max-width: 1440px;
    padding-top: 2.1rem;
    padding-bottom: 3rem;
}}
[data-testid="stVerticalBlock"] {{
    gap: 0.85rem;
}}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {{
    color: var(--ss-muted);
    line-height: 1.65;
}}
h1, h2, h3, h4, h5, h6 {{
    color: var(--ss-text) !important;
    letter-spacing: -0.035em;
}}
[data-testid="stCaptionContainer"] {{
    color: var(--ss-subtle);
}}
[data-testid="stMetric"] {{
    background: var(--ss-surface-elevated);
    border: 1px solid var(--ss-border);
    border-radius: 14px;
    padding: 1rem 1.1rem;
}}
[data-testid="stMetricLabel"] p {{
    color: var(--ss-muted) !important;
}}
[data-testid="stMetricValue"] {{
    color: var(--ss-text) !important;
}}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stNumberInput"] input {{
    background: var(--ss-surface-elevated);
    color: var(--ss-text);
    border-color: var(--ss-border);
    border-radius: 10px;
}}
[data-testid="stButton"] button,
[data-testid="stDownloadButton"] button {{
    border-radius: 10px;
    font-weight: 600;
    transition: border-color 140ms ease, transform 140ms ease, background 140ms ease;
}}
[data-testid="stButton"] button:hover,
[data-testid="stDownloadButton"] button:hover {{
    border-color: var(--ss-primary);
    transform: translateY(-1px);
}}
[data-testid="stSidebar"] [data-testid="stPageLink"] a,
[data-testid="stSidebar"] [data-testid="stNavigation"] a {{
    border-radius: 9px;
}}
[data-testid="stSidebar"] [aria-current="page"] {{
    background: color-mix(in srgb, var(--ss-primary) 13%, transparent);
    border-left: 2px solid var(--ss-primary);
}}
.ss-brand {{
    display: flex;
    align-items: center;
    gap: 0.72rem;
    padding: 0.25rem 0 0.75rem;
}}
.ss-brand-mark {{
    width: 39px;
    height: 39px;
    border: 1px solid color-mix(in srgb, var(--ss-primary) 50%, var(--ss-border));
    border-radius: 12px;
    display: grid;
    place-items: center;
    color: var(--ss-primary);
    background: color-mix(in srgb, var(--ss-primary) 10%, var(--ss-surface));
    box-shadow: 0 0 22px color-mix(in srgb, var(--ss-primary) 12%, transparent);
}}
.ss-brand-name {{
    color: var(--ss-text);
    font-size: 1.02rem;
    font-weight: 750;
    letter-spacing: -0.035em;
    line-height: 1.1;
}}
.ss-brand-subtitle {{
    color: var(--ss-subtle);
    font-size: 0.66rem;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    margin-top: 0.28rem;
}}
.ss-eyebrow {{
    color: var(--ss-primary);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
}}
.ss-panel {{
    background: var(--ss-surface);
    border: 1px solid var(--ss-border);
    border-radius: 16px;
    padding: 1.25rem 1.35rem;
}}
.ss-panel-title {{
    color: var(--ss-text);
    font-size: 0.98rem;
    font-weight: 650;
    margin-bottom: 0.35rem;
}}
.ss-panel-copy {{
    color: var(--ss-muted);
    font-size: 0.88rem;
    line-height: 1.6;
}}
.ss-status {{
    display: inline-flex;
    align-items: center;
    gap: 0.48rem;
    color: var(--ss-muted);
    font-size: 0.78rem;
    border: 1px solid var(--ss-border);
    border-radius: 999px;
    padding: 0.35rem 0.65rem;
}}
.ss-status-dot {{
    width: 7px;
    height: 7px;
    display: inline-block;
    border-radius: 50%;
    background: var(--ss-success);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--ss-success) 14%, transparent);
}}
.ss-divider {{
    height: 1px;
    border: 0;
    background: var(--ss-border);
    margin: 1rem 0;
}}
.ss-code {{
    color: var(--ss-primary);
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.82rem;
}}
/* Phase 2 public-site and dashboard components */
.ss-public-brand {{
    display: flex; align-items: center; gap: .62rem;
    color: var(--ss-text); font-size: 1.02rem; font-weight: 760;
    letter-spacing: -.035em; white-space: nowrap;
}}
.ss-public-brand b {{ color: var(--ss-primary); }}
.ss-public-brand-mark {{
    width: 34px; height: 34px; display: grid; place-items: center;
    border: 1px solid var(--ss-border); border-radius: 11px;
    color: var(--ss-primary); background: var(--ss-surface-elevated);
}}
.ss-public-nav {{
    display: flex; justify-content: center; gap: clamp(.7rem, 2.2vw, 2rem);
    align-items: center; min-height: 38px;
}}
.ss-public-nav a {{
    color: var(--ss-muted); font-size: .84rem; font-weight: 560;
    text-decoration: none; white-space: nowrap;
}}
.ss-public-nav a:hover {{ color: var(--ss-primary); }}
.ss-public-nav-divider {{ height: 1px; background: var(--ss-border); margin: .5rem 0 1.9rem; }}
.ss-cinematic-cta-note {{ color: var(--ss-primary); font: 650 .65rem/1.5 ui-monospace,monospace; letter-spacing: .18em; text-align: center; margin: .25rem 0 .7rem; }}
.ss-hero-title {{
    color: var(--ss-text); font-size: clamp(2.55rem, 5.2vw, 4.6rem);
    font-weight: 790; letter-spacing: -.065em; line-height: 1.02;
    max-width: 760px; margin: .85rem 0 1rem;
}}
.ss-hero-copy {{
    color: var(--ss-muted); font-size: clamp(1rem, 1.35vw, 1.15rem);
    line-height: 1.72; max-width: 650px; margin-bottom: 1.45rem;
}}
.ss-secondary-cta {{
    display: inline-flex; align-items: center; justify-content: center;
    padding: .65rem 1rem; min-height: 42px; border: 1px solid var(--ss-border);
    border-radius: 10px; color: var(--ss-text); font-size: .88rem;
    font-weight: 650; text-decoration: none; background: var(--ss-surface);
}}
.ss-secondary-cta:hover {{ border-color: var(--ss-primary); color: var(--ss-primary); }}
.ss-hero-footnote {{ color: var(--ss-subtle); font-size: .76rem; margin-top: 1.05rem; }}
.ss-hero-footnote .ss-status-dot {{ margin-right: .45rem; }}
.ss-preview-shell {{
    overflow: hidden; border: 1px solid var(--ss-border); border-radius: 19px;
    background: linear-gradient(155deg, var(--ss-surface-elevated), var(--ss-surface));
    box-shadow: 0 22px 70px color-mix(in srgb, var(--ss-text) 8%, transparent);
}}
.ss-preview-topbar {{
    display: flex; align-items: center; gap: .75rem; padding: .8rem 1rem;
    border-bottom: 1px solid var(--ss-border); background: color-mix(in srgb, var(--ss-surface) 72%, transparent);
}}
.ss-preview-dots {{ display: flex; gap: 5px; }}
.ss-preview-dots i {{ width: 7px; height: 7px; display: block; border-radius: 50%; background: var(--ss-subtle); opacity: .7; }}
.ss-preview-label {{ color: var(--ss-subtle); font: 650 .62rem ui-monospace, monospace; letter-spacing: .12em; }}
.ss-preview-live {{ margin-left: auto; color: var(--ss-primary); font: 700 .58rem ui-monospace, monospace; letter-spacing: .09em; }}
.ss-preview-body {{ padding: 1.3rem; }}
.ss-preview-kicker {{ color: var(--ss-primary); font-size: .62rem; letter-spacing: .16em; font-weight: 750; }}
.ss-preview-heading {{ color: var(--ss-text); font-size: 1.3rem; font-weight: 740; letter-spacing: -.04em; margin: .45rem 0 1.1rem; }}
.ss-preview-input {{
    display: flex; align-items: center; gap: .7rem; padding: .8rem .85rem;
    color: var(--ss-subtle); font-size: .75rem; background: var(--ss-background);
    border: 1px solid var(--ss-border); border-radius: 10px;
}}
.ss-preview-input-icon {{ color: var(--ss-primary); font-size: 1.3rem; line-height: 1; }}
.ss-preview-grid {{ display: grid; grid-template-columns: 1fr; gap: .55rem; margin: 1rem 0; }}
.ss-preview-chip {{
    display: grid; grid-template-columns: 30px 1fr auto; align-items: center; gap: .55rem;
    padding: .6rem .7rem; border: 1px solid var(--ss-border); border-radius: 9px;
    color: var(--ss-text); font-size: .76rem;
}}
.ss-preview-chip b {{ color: var(--ss-primary); font: 700 .68rem ui-monospace, monospace; }}
.ss-preview-chip em {{ color: var(--ss-subtle); font-style: normal; font-size: .65rem; }}
.ss-preview-assessment {{
    display: flex; align-items: center; justify-content: space-between; gap: .7rem;
    padding: .85rem; border-radius: 11px; background: color-mix(in srgb, var(--ss-primary) 7%, var(--ss-surface));
    border: 1px solid color-mix(in srgb, var(--ss-primary) 25%, var(--ss-border));
}}
.ss-preview-assessment-label {{ display: block; color: var(--ss-subtle); font: 650 .58rem ui-monospace, monospace; letter-spacing: .1em; margin-bottom: .25rem; }}
.ss-preview-assessment strong {{ color: var(--ss-text); font-size: .88rem; }}
.ss-preview-neutral {{ color: var(--ss-subtle); font: 700 .58rem ui-monospace, monospace; }}
.ss-preview-foot {{ padding: .65rem 1rem; border-top: 1px solid var(--ss-border); color: var(--ss-subtle); font-size: .65rem; }}
.ss-section-kicker {{ color: var(--ss-primary); font-size: .68rem; font-weight: 760; letter-spacing: .16em; margin-bottom: .35rem; }}
.ss-section-gap {{ height: 3.7rem; }}
.ss-section-gap-small {{ height: 1.5rem; }}
.ss-feature-card {{
    height: 100%; min-height: 185px; padding: 1.15rem; margin: .25rem 0;
    border: 1px solid var(--ss-border); border-radius: 15px; background: var(--ss-surface);
}}
.ss-feature-number {{ color: var(--ss-primary); font: 700 .72rem ui-monospace, monospace; margin-bottom: 1.1rem; }}
.ss-feature-title {{ color: var(--ss-text); font-size: 1rem; font-weight: 700; margin-bottom: .45rem; }}
.ss-feature-copy {{ color: var(--ss-muted); font-size: .81rem; line-height: 1.6; min-height: 3.8rem; }}
.ss-feature-status {{ color: var(--ss-primary); font: 650 .61rem ui-monospace, monospace; letter-spacing: .08em; margin-top: .8rem; text-transform: uppercase; }}
.ss-step-card {{
    min-height: 132px; padding: 1rem 1.05rem; margin: .25rem 0;
    background: var(--ss-surface); border: 1px solid var(--ss-border); border-radius: 13px;
}}
.ss-step-card span {{ display: block; color: var(--ss-primary); font: 700 .7rem ui-monospace, monospace; margin-bottom: .6rem; }}
.ss-step-card b {{ color: var(--ss-text); font-size: .95rem; }}
.ss-step-card p {{ color: var(--ss-muted); font-size: .78rem; line-height: 1.55; margin: .35rem 0 0; }}
.ss-trust-row {{ display: flex; align-items: flex-start; gap: .65rem; padding: .45rem 0; color: var(--ss-muted); font-size: .82rem; border-bottom: 1px solid var(--ss-border); }}
.ss-trust-row span {{ color: var(--ss-success); font-weight: 800; }}
.ss-footer {{ margin-top: 3rem; padding: 1.25rem 0 .5rem; border-top: 1px solid var(--ss-border); color: var(--ss-muted); font-size: .78rem; }}
.ss-footer b {{ color: var(--ss-text); }}
.ss-footer span {{ display: block; color: var(--ss-subtle); margin-top: .35rem; font-size: .7rem; }}
.ss-date-label {{ color: var(--ss-subtle); text-align: right; font-size: .76rem; padding-bottom: .7rem; }}
.ss-metric-card {{
    height: 100%; min-height: 136px; padding: 1rem; border-radius: 14px;
    border: 1px solid var(--ss-border); background: var(--ss-surface);
}}
.ss-metric-top {{ display: flex; align-items: center; justify-content: space-between; gap: .5rem; color: var(--ss-muted); font-size: .76rem; font-weight: 630; }}
.ss-metric-icon {{ color: var(--ss-primary); font: 700 .59rem ui-monospace, monospace; letter-spacing: .08em; }}
.ss-metric-value {{ color: var(--ss-text); font-size: 2rem; font-weight: 770; letter-spacing: -.06em; margin: .5rem 0 .1rem; }}
.ss-metric-hint {{ color: var(--ss-subtle); font-size: .68rem; line-height: 1.4; }}
.ss-dashboard-panel {{ min-height: 265px; }}
.ss-panel-heading {{ display: flex; align-items: center; justify-content: space-between; gap: .5rem; padding-bottom: .85rem; border-bottom: 1px solid var(--ss-border); }}
.ss-panel-heading b {{ color: var(--ss-text); font-size: .93rem; }}
.ss-panel-heading span {{ color: var(--ss-subtle); font: 650 .58rem ui-monospace, monospace; letter-spacing: .1em; }}
.ss-empty-state {{ display: flex; flex-direction: column; align-items: flex-start; padding: 1.2rem .2rem .8rem; }}
.ss-empty-compact {{ padding-top: 1.6rem; }}
.ss-empty-icon {{ display: grid; place-items: center; width: 34px; height: 34px; border-radius: 10px; color: var(--ss-primary); background: color-mix(in srgb, var(--ss-primary) 10%, var(--ss-surface)); font-size: 1.3rem; margin-bottom: .7rem; }}
.ss-empty-state b {{ color: var(--ss-text); font-size: .88rem; }}
.ss-empty-state p {{ color: var(--ss-muted); font-size: .76rem; line-height: 1.55; margin: .35rem 0 .3rem; }}
.ss-shortcut-card {{ min-height: 128px; padding: 1rem; border: 1px solid var(--ss-border); background: var(--ss-surface); border-radius: 13px; }}
.ss-shortcut-card b {{ color: var(--ss-text); font-size: .9rem; }}
.ss-shortcut-card p {{ color: var(--ss-muted); font-size: .74rem; line-height: 1.5; min-height: 2.5rem; }}
.ss-shortcut-status {{ color: var(--ss-subtle); font: 650 .56rem ui-monospace, monospace; letter-spacing: .08em; }}
[data-testid="stPageLink"] a {{ border-radius: 10px; font-weight: 620; }}
[data-testid="stForm"] {{ padding: 1rem; border: 1px solid var(--ss-border); border-radius: 14px; background: var(--ss-surface); }}
[data-testid="stCodeBlock"] pre {{ background: var(--ss-surface-elevated) !important; color: var(--ss-text) !important; border: 1px solid var(--ss-border); }}
[data-testid="stAlert"] {{ border-radius: 12px; }}

/* Theme-complete Streamlit controls. Streamlit's base theme is static, so
   explicitly bind every interactive text surface to our active theme tokens. */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stSidebar"],
[data-testid="stMainBlockContainer"],
section.main,
.block-container {{
    color: var(--ss-text) !important;
}}
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] *,
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] label *,
[data-testid="stRadio"] label,
[data-testid="stRadio"] label *,
[data-testid="stToggle"] label,
[data-testid="stToggle"] label *,
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] label * {{
    color: var(--ss-text) !important;
}}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] * {{
    color: var(--ss-muted) !important;
}}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {{
    background: var(--ss-surface-elevated) !important;
    color: var(--ss-text) !important;
    border-color: var(--ss-border) !important;
    caret-color: var(--ss-primary);
}}
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stMultiSelect"] [data-baseweb="select"] * {{
    color: var(--ss-text) !important;
}}
[data-testid="stSelectbox"] [data-baseweb="select"] svg,
[data-testid="stMultiSelect"] [data-baseweb="select"] svg {{
    fill: var(--ss-muted) !important;
    color: var(--ss-muted) !important;
}}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder,
[data-testid="stNumberInput"] input::placeholder {{
    color: var(--ss-subtle) !important;
    opacity: 1;
}}
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {{
    background: var(--ss-surface-elevated) !important;
    border-color: var(--ss-border) !important;
}}
[data-baseweb="menu"] *,
[role="option"],
[role="listbox"] * {{
    color: var(--ss-text) !important;
}}
[data-testid="stButton"] button,
[data-testid="stDownloadButton"] button,
[data-testid="stFormSubmitButton"] button {{
    color: var(--ss-text) !important;
    background: var(--ss-surface-elevated) !important;
    border: 1px solid var(--ss-border) !important;
}}
[data-testid="stButton"] button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"] {{
    color: #FFFFFF !important;
    background: var(--ss-primary-strong) !important;
    border-color: var(--ss-primary-strong) !important;
}}
[data-testid="stPageLink"] a,
[data-testid="stSidebar"] [data-testid="stPageLink"] a {{
    color: var(--ss-text) !important;
}}
[data-testid="stTabs"] button,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary * {{
    color: var(--ss-text) !important;
}}
[data-testid="stAlert"] {{
    color: var(--ss-text) !important;
    border: 1px solid var(--ss-border);
}}
[data-testid="stAlert"] p,
[data-testid="stAlert"] span {{
    color: inherit !important;
}}

/* Neon polish: restrained glow, clear hierarchy, and responsive micro-interactions. */
[data-testid="stMainBlockContainer"] > div {{
    animation: ss-content-enter 420ms ease-out both;
}}
h1 {{
    background: linear-gradient(100deg, var(--ss-text) 0%, var(--ss-primary) 68%, var(--ss-violet) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    width: fit-content;
    max-width: 100%;
}}
.ss-panel, .ss-feature-card, .ss-metric-card, .ss-kpi-card, .ss-viz-card,
.ss-shortcut-card, [data-testid="stForm"], [data-testid="stMetric"] {{
    transition: border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
}}
.ss-panel:hover, .ss-feature-card:hover, .ss-metric-card:hover,
.ss-kpi-card:hover, .ss-viz-card:hover, .ss-shortcut-card:hover {{
    border-color: color-mix(in srgb, var(--ss-primary) 58%, var(--ss-border));
    box-shadow: 0 0 0 1px color-mix(in srgb, var(--ss-primary) 12%, transparent),
                0 12px 34px color-mix(in srgb, var(--ss-primary) 7%, transparent);
}}
[data-testid="stButton"] button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"] {{
    box-shadow: 0 0 0 1px color-mix(in srgb, var(--ss-primary) 25%, transparent),
                0 0 22px color-mix(in srgb, var(--ss-primary) 14%, transparent);
    letter-spacing: .01em;
}}
[data-testid="stButton"] button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] button[kind="primary"]:hover {{
    box-shadow: 0 0 0 1px color-mix(in srgb, var(--ss-primary) 55%, transparent),
                0 0 30px color-mix(in srgb, var(--ss-primary) 25%, transparent);
    filter: brightness(1.06);
}}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {{
    border-color: var(--ss-primary) !important;
    box-shadow: 0 0 0 1px var(--ss-primary),
                0 0 18px color-mix(in srgb, var(--ss-primary) 15%, transparent) !important;
}}
[data-testid="stTabs"] button[aria-selected="true"] {{
    border-bottom-color: var(--ss-primary) !important;
    color: var(--ss-primary) !important;
}}
.ss-neon-callout {{
    border: 1px solid color-mix(in srgb, var(--ss-primary) 34%, var(--ss-border));
    border-radius: 14px; padding: .9rem 1rem;
    background: radial-gradient(ellipse at 0% 0%, color-mix(in srgb, var(--ss-primary) 10%, transparent), transparent 70%), var(--ss-surface);
}}
.ss-neon-kicker {{ color: var(--ss-primary); font: 750 .64rem ui-monospace, monospace; letter-spacing: .14em; text-transform: uppercase; }}
.ss-finding-card {{ border: 1px solid var(--ss-border); border-left: 3px solid var(--ss-violet); border-radius: 10px; padding: .85rem 1rem; margin: .45rem 0; background: color-mix(in srgb, var(--ss-surface-elevated) 88%, transparent); }}
.ss-finding-card--high {{ border-left-color: var(--ss-danger); }}
.ss-finding-card--review {{ border-left-color: var(--ss-warning); }}
.ss-finding-card b {{ color: var(--ss-text); }}
.ss-finding-card p {{ margin: .35rem 0 0; color: var(--ss-muted); font-size: .84rem; line-height: 1.55; }}
@keyframes ss-content-enter {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}

[data-testid="stMetricLabel"] p {{ color: var(--ss-muted) !important; }}
[data-testid="stMetricValue"] {{ color: var(--ss-text) !important; }}
[data-testid="stDataFrame"],
[data-testid="stTable"] {{ color: var(--ss-text) !important; }}

/* Theme-aware icons. Streamlit renders navigation and widget icons as Material
   icon glyphs, while some controls use inline SVG. Color the icon containers
   (not every SVG path) so custom charts and semantic risk colors stay intact. */
[data-testid="stIconMaterial"],
[data-testid="stIconMaterial"] span,
span.material-icons,
span.material-icons-round,
span.material-symbols-rounded,
.material-symbols-outlined {{
    color: var(--ss-icon) !important;
    opacity: 1 !important;
}}
[data-testid="stSidebar"] [data-testid="stPageLink"] svg,
[data-testid="stMain"] [data-testid="stPageLink"] svg,
[data-testid="stButton"] button svg,
[data-testid="stDownloadButton"] button svg,
[data-testid="stFormSubmitButton"] button svg,
[data-testid="stExpander"] summary svg {{
    color: var(--ss-icon) !important;
    opacity: 1 !important;
}}
[data-testid="stSidebar"] [aria-current="page"] [data-testid="stIconMaterial"],
[data-testid="stSidebar"] [aria-current="page"] .material-symbols-rounded,
[data-testid="stSidebar"] [aria-current="page"] .material-icons,
[data-testid="stSidebar"] [aria-current="page"] svg {{
    color: var(--ss-primary) !important;
}}
[data-testid="stButton"] button[kind="primary"] [data-testid="stIconMaterial"],
[data-testid="stButton"] button[kind="primary"] .material-symbols-rounded,
[data-testid="stButton"] button[kind="primary"] svg,
[data-testid="stFormSubmitButton"] button[kind="primary"] [data-testid="stIconMaterial"],
[data-testid="stFormSubmitButton"] button[kind="primary"] svg {{
    color: #FFFFFF !important;
}}
/* Inline SVG brand marks inherit their containing theme color. */
.ss-brand-mark svg,
.ss-public-brand-mark svg {{ color: inherit; }}

/* Dashboard visualizations */
.ss-demo-banner {{
    display:flex; align-items:center; gap:.7rem; padding:.8rem 1rem;
    border:1px solid color-mix(in srgb, var(--ss-warning) 40%, var(--ss-border));
    background:color-mix(in srgb, var(--ss-warning) 9%, var(--ss-surface));
    color:var(--ss-text); border-radius:12px; font-size:.82rem; line-height:1.5;
}}
.ss-demo-banner strong {{ color:var(--ss-warning); font-size:.7rem; letter-spacing:.1em; white-space:nowrap; }}
.ss-dashboard-hero {{
    display:flex; align-items:flex-end; justify-content:space-between; gap:1rem;
    padding:1.25rem 1.35rem; border:1px solid var(--ss-border); border-radius:17px;
    background:radial-gradient(circle at 88% 8%, color-mix(in srgb, var(--ss-primary) 13%, transparent), transparent 35%), var(--ss-surface);
}}
.ss-dashboard-hero h2 {{ color:var(--ss-text); font-size:clamp(1.5rem, 2.2vw, 2rem); letter-spacing:-.045em; margin:.35rem 0 .3rem; }}
.ss-dashboard-hero p {{ color:var(--ss-muted); margin:0; font-size:.86rem; }}
.ss-live-pill {{ display:inline-flex; align-items:center; gap:.45rem; padding:.38rem .65rem; border:1px solid var(--ss-border); border-radius:99px; color:var(--ss-muted); font-size:.68rem; white-space:nowrap; }}
.ss-live-pill i {{ width:7px; height:7px; border-radius:50%; background:var(--ss-warning); display:inline-block; }}
.ss-kpi-card {{
    position:relative; overflow:hidden; min-height:142px; padding:1rem 1.05rem;
    border:1px solid var(--ss-border); border-radius:15px; background:var(--ss-surface);
}}
.ss-kpi-card:after {{ content:""; position:absolute; right:-28px; top:-32px; width:95px; height:95px; border-radius:50%; background:color-mix(in srgb, var(--ss-kpi-accent) 12%, transparent); }}
.ss-kpi-head {{ display:flex; justify-content:space-between; align-items:center; gap:.5rem; color:var(--ss-muted); font-size:.75rem; font-weight:650; }}
.ss-kpi-icon {{ display:grid; place-items:center; width:31px; height:31px; border-radius:9px; color:var(--ss-kpi-accent); background:color-mix(in srgb, var(--ss-kpi-accent) 12%, var(--ss-surface)); font-size:.95rem; }}
.ss-kpi-value-row {{ display:flex; align-items:baseline; gap:.55rem; margin:.65rem 0 .12rem; }}
.ss-kpi-value {{ color:var(--ss-text); font-size:1.95rem; line-height:1.1; font-weight:790; letter-spacing:-.06em; }}
.ss-kpi-change {{ color:var(--ss-kpi-accent); font-size:.68rem; font-weight:700; }}
.ss-kpi-foot {{ color:var(--ss-subtle); font-size:.67rem; }}
.ss-viz-card {{ height:100%; padding:1.1rem 1.15rem; border:1px solid var(--ss-border); border-radius:15px; background:var(--ss-surface); }}
.ss-viz-head {{ display:flex; align-items:flex-start; justify-content:space-between; gap:.7rem; margin-bottom:.9rem; }}
.ss-viz-title {{ color:var(--ss-text); font-size:.92rem; font-weight:720; }}
.ss-viz-subtitle {{ color:var(--ss-subtle); font-size:.68rem; margin-top:.2rem; }}
.ss-viz-tag {{ color:var(--ss-primary); border:1px solid var(--ss-border); border-radius:7px; padding:.25rem .4rem; font:700 .56rem ui-monospace,monospace; letter-spacing:.07em; white-space:nowrap; }}
.ss-trend-svg {{ width:100%; height:auto; display:block; overflow:visible; }}
.ss-trend-grid {{ stroke:var(--ss-chart-grid); stroke-width:1; stroke-dasharray:4 5; }}
.ss-trend-line {{ fill:none; stroke:var(--ss-primary); stroke-width:3.5; stroke-linecap:round; stroke-linejoin:round; }}
.ss-trend-area {{ fill:url(#ssTrendFill); }}
.ss-trend-point {{ fill:var(--ss-surface); stroke:var(--ss-primary); stroke-width:2.5; }}
.ss-chart-labels {{ display:flex; justify-content:space-between; color:var(--ss-subtle); font-size:.62rem; padding:.15rem .2rem 0; }}
.ss-risk-layout {{ display:flex; align-items:center; gap:1rem; min-height:180px; }}
.ss-donut {{ width:142px; height:142px; flex:0 0 142px; display:grid; place-items:center; border-radius:50%; background:conic-gradient(var(--ss-danger) 0 17%, var(--ss-warning) 17% 47%, var(--ss-primary) 47% 76%, var(--ss-success) 76% 100%); position:relative; }}
.ss-donut:before {{ content:""; position:absolute; inset:17px; border-radius:50%; background:var(--ss-surface); border:1px solid var(--ss-border); }}
.ss-donut-center {{ position:relative; z-index:1; text-align:center; }}
.ss-donut-center b {{ display:block; color:var(--ss-text); font-size:1.2rem; letter-spacing:-.04em; }}
.ss-donut-center span {{ color:var(--ss-subtle); font:700 .52rem ui-monospace,monospace; letter-spacing:.1em; }}
.ss-legend {{ flex:1; display:grid; gap:.58rem; }}
.ss-legend-row {{ display:grid; grid-template-columns:9px 1fr auto; align-items:center; gap:.45rem; color:var(--ss-muted); font-size:.68rem; }}
.ss-legend-dot {{ width:8px; height:8px; border-radius:50%; }}
.ss-legend-row b {{ color:var(--ss-text); font-size:.68rem; }}
.ss-category-list {{ display:grid; gap:.85rem; }}
.ss-category-top {{ display:flex; align-items:center; justify-content:space-between; color:var(--ss-muted); font-size:.7rem; margin-bottom:.32rem; }}
.ss-category-top b {{ color:var(--ss-text); font-size:.7rem; }}
.ss-category-track {{ height:7px; overflow:hidden; border-radius:20px; background:var(--ss-chart-track); }}
.ss-category-fill {{ height:100%; border-radius:20px; background:linear-gradient(90deg,var(--ss-primary),var(--ss-blue)); }}
.ss-score-layout {{ display:flex; align-items:center; gap:1rem; }}
.ss-score-ring {{ width:112px; height:112px; flex:0 0 112px; display:grid; place-items:center; border-radius:50%; background:conic-gradient(var(--ss-warning) 0 72%, var(--ss-chart-track) 72% 100%); position:relative; }}
.ss-score-ring:before {{ content:""; position:absolute; inset:10px; border-radius:50%; background:var(--ss-surface); border:1px solid var(--ss-border); }}
.ss-score-value {{ position:relative; z-index:1; color:var(--ss-text); font-size:1.55rem; font-weight:800; letter-spacing:-.06em; }}
.ss-score-value small {{ color:var(--ss-subtle); font-size:.58rem; font-weight:650; letter-spacing:0; }}
.ss-score-copy b {{ color:var(--ss-text); font-size:.82rem; }}
.ss-score-copy p {{ color:var(--ss-muted); font-size:.69rem; line-height:1.5; margin:.28rem 0 0; }}
.ss-sample-table {{ width:100%; border-collapse:collapse; }}
.ss-sample-table th {{ text-align:left; color:var(--ss-subtle); font:700 .58rem ui-monospace,monospace; letter-spacing:.08em; padding:.65rem .45rem; border-bottom:1px solid var(--ss-border); }}
.ss-sample-table td {{ color:var(--ss-muted); font-size:.7rem; padding:.75rem .45rem; border-bottom:1px solid var(--ss-border); }}
.ss-sample-table td:first-child {{ color:var(--ss-text); font-weight:650; }}
.ss-risk-badge {{ display:inline-block; border-radius:6px; padding:.24rem .42rem; font-size:.58rem; font-weight:750; white-space:nowrap; }}
.ss-risk-high {{ color:var(--ss-danger); background:color-mix(in srgb,var(--ss-danger) 12%,var(--ss-surface)); }}
.ss-risk-medium {{ color:var(--ss-warning); background:color-mix(in srgb,var(--ss-warning) 12%,var(--ss-surface)); }}
.ss-risk-low {{ color:var(--ss-success); background:color-mix(in srgb,var(--ss-success) 12%,var(--ss-surface)); }}
.ss-shortcut-card {{ transition:transform 150ms ease,border-color 150ms ease; }}
.ss-shortcut-card:hover {{ transform:translateY(-2px); border-color:var(--ss-primary); }}

@keyframes ss-disc-spin {{ from {{ rotate: 0deg; }} to {{ rotate: 360deg; }} }}
@keyframes ss-hole-float {{ from {{ margin-left: -1%; }} to {{ margin-left: 1%; }} }}
@keyframes ss-star-drift {{ from {{ background-position: 0 0, 0 0, 0 0, 0 0, 0 0, center, center; }} to {{ background-position: 390px 310px, -470px 380px, 520px -420px, -440px -360px, 600px 500px, center, center; }} }}
@keyframes ss-orbit-turn {{ from {{ rotate: 0deg; }} to {{ rotate: 360deg; }} }}
@keyframes ss-star-infall {{ 0%, 100% {{ scale: 1; opacity: .96; }} 70% {{ scale: .42; opacity: .75; }} 92% {{ scale: .08; opacity: .08; }} }}
@media (max-width: 768px) {{
    #scamshield-cosmos .ss-black-hole {{ width: 520px; height: 520px; left: 90%; top: 45%; opacity: .62; }}
}}
@media (prefers-reduced-motion: reduce) {{
    #scamshield-cosmos .ss-cosmos-stars,
    #scamshield-cosmos .ss-black-hole,
    #scamshield-cosmos .ss-accretion-disc,
    #scamshield-cosmos .ss-star-orbit,
    #scamshield-cosmos .ss-star {{ animation: none !important; }}
}}
@media (max-width: 900px) {{
    .ss-public-nav {{ gap: .85rem; }}
    .ss-public-nav a {{ font-size: .75rem; }}
    .ss-hero-title {{ font-size: clamp(2.3rem, 7vw, 3.4rem); }}
}}
@media (max-width: 768px) {{
    [data-testid="stMainBlockContainer"] {{
        padding: 1.2rem 1rem 2rem;
    }}
    .ss-panel {{ padding: 1rem; border-radius: 13px; }}
    .ss-public-nav {{ justify-content: flex-start; flex-wrap: wrap; padding: .55rem 0; }}
    .ss-public-nav-divider {{ margin-bottom: 1.15rem; }}
    .ss-hero-title {{ font-size: clamp(2.2rem, 10vw, 3.3rem); }}
    .ss-section-gap {{ height: 2.2rem; }}
    .ss-feature-card, .ss-step-card {{ min-height: auto; }}
    .ss-feature-copy {{ min-height: auto; }}
    .ss-date-label {{ text-align: left; }}
    .ss-metric-card {{ min-height: 120px; }}
    .ss-dashboard-hero {{ align-items:flex-start; flex-direction:column; }}
    .ss-risk-layout {{ justify-content:center; }}
    .ss-sample-table {{ min-width:540px; }}
}}
@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
    }}
}}
</style>
<!-- Cinematic landing scene is rendered by components/cinematic_experience.py. -->
"""
