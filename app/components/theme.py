import streamlit as st


def inject_theme():
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(14, 116, 144, 0.10), transparent 28%),
                radial-gradient(circle at top right, rgba(30, 64, 175, 0.08), transparent 24%),
                linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
        }
        .block-container {
            max-width: 1180px;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3 {
            color: #0f172a;
        }
        .hero-card, .panel-card {
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid rgba(148, 163, 184, 0.25);
            box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
            border-radius: 20px;
            padding: 1.2rem 1.2rem 1rem 1.2rem;
            backdrop-filter: blur(8px);
        }
        .metric-pill {
            display: inline-block;
            background: #0f172a;
            color: #ffffff;
            border-radius: 999px;
            padding: 0.35rem 0.75rem;
            font-weight: 600;
            margin-bottom: 0.8rem;
        }
        .small-muted {
            color: #475569;
            font-size: 0.92rem;
        }
        @media (max-width: 768px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
