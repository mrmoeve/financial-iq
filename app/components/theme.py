import html

import streamlit as st


def inject_theme():
    st.markdown(
        """
        <style>
        :root {
            --bg: #0B1220;
            --bg-soft: #0f172a;
            --card: #111827;
            --card-strong: #0f172a;
            --line: rgba(148, 163, 184, 0.16);
            --line-strong: rgba(37, 99, 235, 0.30);
            --primary: #2563EB;
            --success: #10B981;
            --warning: #F59E0B;
            --danger: #EF4444;
            --text: #F9FAFB;
            --muted: #9CA3AF;
        }

        html, body, [class*="css"]  {
            color: var(--text);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.16), transparent 30%),
                radial-gradient(circle at top right, rgba(16, 185, 129, 0.08), transparent 24%),
                linear-gradient(180deg, #08101d 0%, #0B1220 100%);
        }

        [data-testid="stAppViewContainer"] {
            background: transparent;
        }

        [data-testid="stHeader"],
        [data-testid="stToolbar"] {
            background: transparent;
        }

        .block-container {
            max-width: 1360px;
            padding-top: 1.25rem;
            padding-bottom: 2rem;
            padding-left: 1.4rem;
            padding-right: 1.4rem;
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--text) !important;
            letter-spacing: -0.02em;
        }

        p, li, label, .stMarkdown, .stCaption, .stText {
            color: var(--text);
        }

        .stCaption, .small-muted, .muted-copy {
            color: var(--muted) !important;
        }

        [data-testid="stSidebar"] {
            background: rgba(7, 12, 24, 0.96);
            border-right: 1px solid var(--line);
        }

        .platform-shell {
            position: relative;
            overflow: hidden;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(9, 18, 32, 0.96));
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 26px;
            box-shadow: 0 30px 80px rgba(2, 6, 23, 0.55);
            padding: 1.5rem;
        }

        .platform-shell::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px),
                linear-gradient(180deg, rgba(255,255,255,0.02) 1px, transparent 1px);
            background-size: 34px 34px;
            opacity: 0.25;
            pointer-events: none;
        }

        .hero-card,
        .panel-card,
        .analysis-card,
        .metric-card,
        .auth-panel,
        .auth-hero {
            position: relative;
            z-index: 1;
            background: linear-gradient(180deg, rgba(17, 24, 39, 0.96), rgba(11, 18, 32, 0.96));
            border: 1px solid var(--line);
            border-radius: 24px;
            box-shadow: 0 18px 40px rgba(2, 6, 23, 0.35);
        }

        .hero-card,
        .panel-card,
        .analysis-card {
            padding: 1.25rem;
        }

        .auth-shell {
            display: grid;
            grid-template-columns: minmax(0, 1.15fr) minmax(360px, 0.85fr);
            gap: 1.2rem;
            align-items: stretch;
        }

        .auth-hero,
        .auth-panel {
            padding: 1.5rem;
            min-height: 620px;
        }

        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: #bfdbfe;
            background: rgba(37, 99, 235, 0.14);
            border: 1px solid rgba(37, 99, 235, 0.25);
            padding: 0.4rem 0.7rem;
            border-radius: 999px;
        }

        .auth-title,
        .workspace-title {
            font-size: clamp(2.6rem, 4vw, 4.4rem);
            line-height: 0.94;
            margin: 1rem 0 0.9rem;
            font-weight: 800;
        }

        .auth-copy,
        .workspace-copy {
            color: var(--muted);
            font-size: 1.02rem;
            line-height: 1.75;
            max-width: 40rem;
        }

        .hero-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.85rem;
            margin-top: 1.5rem;
        }

        .hero-grid .hero-stat {
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 18px;
            padding: 1rem;
        }

        .hero-label {
            display: block;
            color: var(--muted);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.13em;
            margin-bottom: 0.5rem;
        }

        .hero-value {
            display: block;
            color: var(--text);
            font-size: 1.4rem;
            font-weight: 700;
        }

        .feature-list {
            display: grid;
            gap: 0.7rem;
            margin-top: 1.25rem;
        }

        .feature-item {
            display: flex;
            gap: 0.75rem;
            align-items: flex-start;
            padding: 0.85rem 0.95rem;
            background: rgba(8, 15, 29, 0.68);
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 18px;
        }

        .feature-dot {
            width: 0.62rem;
            height: 0.62rem;
            border-radius: 999px;
            margin-top: 0.42rem;
            background: linear-gradient(180deg, #60a5fa, #2563EB);
            box-shadow: 0 0 0 6px rgba(37, 99, 235, 0.12);
            flex: 0 0 auto;
        }

        .feature-title {
            font-weight: 700;
            color: var(--text);
            margin-bottom: 0.18rem;
        }

        .feature-copy {
            color: var(--muted);
            font-size: 0.95rem;
            line-height: 1.55;
        }

        .dashboard-hero {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            align-items: flex-start;
            margin-bottom: 1rem;
        }

        .status-chip,
        .signal-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.4rem 0.75rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .status-chip {
            background: rgba(16, 185, 129, 0.14);
            border: 1px solid rgba(16, 185, 129, 0.28);
            color: #d1fae5;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.9rem;
            margin: 1rem 0 1.35rem;
        }

        .metric-card {
            padding: 1rem 1rem 1.05rem;
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.76rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin-bottom: 0.7rem;
        }

        .metric-value {
            color: var(--text);
            font-size: 2rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 0.55rem;
        }

        .metric-note {
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.45;
            min-height: 2.6rem;
        }

        .metric-card.primary {
            border-color: rgba(37, 99, 235, 0.34);
            background:
                linear-gradient(180deg, rgba(37, 99, 235, 0.18), rgba(17, 24, 39, 0.96));
        }

        .metric-card.success .metric-value,
        .signal-badge.success {
            color: var(--success);
        }

        .metric-card.warning .metric-value,
        .signal-badge.warning {
            color: var(--warning);
        }

        .metric-card.danger .metric-value,
        .signal-badge.danger {
            color: var(--danger);
        }

        .signal-badge.success,
        .signal-badge.warning,
        .signal-badge.danger {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(148, 163, 184, 0.16);
        }

        .uploader-frame {
            border: 1.5px dashed rgba(96, 165, 250, 0.48);
            border-radius: 22px;
            padding: 1.05rem;
            background:
                linear-gradient(180deg, rgba(14, 22, 38, 0.95), rgba(9, 18, 32, 0.96));
        }

        .section-kicker {
            color: #93c5fd;
            font-size: 0.76rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .section-title {
            color: var(--text);
            font-size: 1.45rem;
            font-weight: 760;
            margin-bottom: 0.35rem;
        }

        .card-title {
            color: var(--text);
            font-size: 1.1rem;
            font-weight: 750;
            margin-bottom: 0.45rem;
        }

        .card-copy {
            color: var(--muted);
            font-size: 0.94rem;
            line-height: 1.65;
        }

        .bullet-list {
            display: grid;
            gap: 0.65rem;
            margin-top: 0.7rem;
        }

        .bullet-item {
            padding: 0.75rem 0.9rem;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.78);
            border: 1px solid rgba(148, 163, 184, 0.12);
            color: var(--text);
            line-height: 1.55;
        }

        .analysis-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.95rem;
            margin-top: 0.95rem;
        }

        .analysis-block {
            padding: 1rem;
            border-radius: 18px;
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(148, 163, 184, 0.12);
        }

        .ratio-table-title {
            margin-top: 1rem;
            margin-bottom: 0.6rem;
        }

        .auth-panel .stTabs [data-baseweb="tab-list"] {
            gap: 0.55rem;
            background: rgba(8, 15, 29, 0.9);
            border: 1px solid rgba(148, 163, 184, 0.14);
            padding: 0.35rem;
            border-radius: 16px;
        }

        .auth-panel .stTabs [data-baseweb="tab"] {
            height: 46px;
            border-radius: 12px;
            color: var(--muted);
            font-weight: 700;
            padding: 0 1rem;
        }

        .auth-panel .stTabs [aria-selected="true"] {
            background: rgba(37, 99, 235, 0.14) !important;
            color: var(--text) !important;
        }

        div[data-testid="stForm"] {
            background: transparent;
            border: 0;
            padding: 0;
        }

        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox [data-baseweb="select"] > div,
        .stMultiSelect [data-baseweb="select"] > div,
        .stFileUploader section {
            background: rgba(7, 12, 24, 0.92) !important;
            color: var(--text) !important;
            border-radius: 16px !important;
            border: 1px solid rgba(148, 163, 184, 0.16) !important;
        }

        .stTextInput label,
        .stSelectbox label,
        .stFileUploader label {
            color: var(--muted) !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            letter-spacing: 0.02em;
        }

        .stButton > button,
        .stDownloadButton > button,
        .stFormSubmitButton > button {
            min-height: 48px;
            border-radius: 16px;
            border: 1px solid rgba(37, 99, 235, 0.34);
            background: linear-gradient(180deg, #2563EB 0%, #1d4ed8 100%);
            color: #F9FAFB;
            font-size: 0.98rem;
            font-weight: 700;
            box-shadow: 0 18px 30px rgba(37, 99, 235, 0.24);
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stFormSubmitButton > button:hover {
            border-color: rgba(96, 165, 250, 0.65);
            transform: translateY(-1px);
        }

        .stDataFrame,
        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 18px;
            overflow: hidden;
            background: rgba(10, 16, 29, 0.88);
        }

        details {
            background: rgba(11, 18, 32, 0.82);
            border-radius: 18px;
            border: 1px solid rgba(148, 163, 184, 0.14);
            padding: 0.4rem 0.75rem;
        }

        .stAlert {
            border-radius: 18px;
            border-width: 1px;
        }

        @media (max-width: 1180px) {
            .metric-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .auth-shell {
                grid-template-columns: 1fr;
            }

            .auth-hero,
            .auth-panel {
                min-height: auto;
            }
        }

        @media (max-width: 860px) {
            .analysis-grid,
            .hero-grid,
            .metric-grid {
                grid-template-columns: 1fr;
            }

            .dashboard-hero {
                flex-direction: column;
            }

            .workspace-title {
                font-size: 2.2rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def card_header(eyebrow: str, title: str, copy: str) -> str:
    return (
        f"<div class='section-kicker'>{html.escape(eyebrow)}</div>"
        f"<div class='section-title'>{html.escape(title)}</div>"
        f"<div class='card-copy'>{html.escape(copy)}</div>"
    )
