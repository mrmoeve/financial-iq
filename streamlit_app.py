import html

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from app.components.theme import card_header, inject_theme
from app.db import repository
from app.db.session import SessionLocal, init_db
from app.services.analysis import analyze_financial_document
from app.services.auth import PasswordHashingError, PasswordValidationError, authenticate_user, register_user
from app.services.extractor import SUPPORTED_EXTENSIONS, extract_text_from_upload
from app.services.report_export import build_analysis_pdf
from app.utils.dashboard import derive_dashboard_metrics, derive_risk_level, render_bullet_list, render_metric_card
from app.utils.formatting import display_ratio_table_rows


load_dotenv()
st.set_page_config(page_title="StatementIQ", page_icon=":bar_chart:", layout="wide")
inject_theme()

DB_READY = True
try:
    init_db()
except SQLAlchemyError:
    DB_READY = False


def get_db():
    return SessionLocal()


def init_session_state():
    st.session_state.setdefault("user_id", None)
    st.session_state.setdefault("user_email", None)
    st.session_state.setdefault("current_analysis", None)
    st.session_state.setdefault("current_company_name", None)
    st.session_state.setdefault("current_document_name", None)
    st.session_state.setdefault("current_document_type", None)


def _render_auth_hero():
    st.markdown(
        """
        <div class='auth-hero'>
            <div class='eyebrow'>Institutional Financial Intelligence</div>
            <div class='auth-title'>StatementIQ</div>
            <div class='auth-copy'>
                Upload annual reports, 10-Ks, 10-Qs, and core financial statements into a workspace
                designed to feel closer to a professional research terminal than a generic upload form.
            </div>
            <div class='hero-grid'>
                <div class='hero-stat'>
                    <span class='hero-label'>Coverage</span>
                    <span class='hero-value'>10-K • 10-Q • Annual Reports</span>
                </div>
                <div class='hero-stat'>
                    <span class='hero-label'>Outputs</span>
                    <span class='hero-value'>Health Score • Risks • Ratios</span>
                </div>
                <div class='hero-stat'>
                    <span class='hero-label'>Workflow</span>
                    <span class='hero-value'>Upload → Analyze → Export</span>
                </div>
                <div class='hero-stat'>
                    <span class='hero-label'>Mode</span>
                    <span class='hero-value'>Investor-grade dashboard</span>
                </div>
            </div>
            <div class='feature-list'>
                <div class='feature-item'>
                    <div class='feature-dot'></div>
                    <div>
                        <div class='feature-title'>Structured underwriting lens</div>
                        <div class='feature-copy'>Rapidly isolate operating quality, leverage pressure, cash flow durability, and the narrative behind the score.</div>
                    </div>
                </div>
                <div class='feature-item'>
                    <div class='feature-dot'></div>
                    <div>
                        <div class='feature-title'>Persistent research history</div>
                        <div class='feature-copy'>Each uploaded document is preserved as an analysis record with reusable summaries and PDF exports.</div>
                    </div>
                </div>
                <div class='feature-item'>
                    <div class='feature-dot'></div>
                    <div>
                        <div class='feature-title'>Terminal-inspired interface</div>
                        <div class='feature-copy'>Dark market-data styling, dense KPI cards, and cleaner reading surfaces for long-form filing review.</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_auth():
    left_col, right_col = st.columns([1.2, 0.9], gap="large")
    with left_col:
        _render_auth_hero()
    with right_col:
        st.markdown("<div class='auth-panel'>", unsafe_allow_html=True)
        st.markdown(card_header("Secure Workspace Access", "Sign in to your research environment", "Create an account or log in to continue analyzing statements and exporting investment-ready reports."), unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["Login", "Create account"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="analyst@fund.com")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Enter Workspace", use_container_width=True)
            if submitted:
                db = get_db()
                try:
                    user = authenticate_user(db, email, password)
                    if not user:
                        st.error("Invalid email or password.")
                    else:
                        st.session_state["user_id"] = str(user.id)
                        st.session_state["user_email"] = user.email
                        st.rerun()
                except Exception:
                    st.error("Invalid email or password.")
                finally:
                    db.close()

        with tab_signup:
            with st.form("signup_form"):
                email = st.text_input("Work Email", placeholder="team@statementiq.com")
                password = st.text_input("Create Password", type="password", placeholder="Use at least 8 characters")
                submitted = st.form_submit_button("Create Workspace Access", use_container_width=True)
            if submitted:
                db = get_db()
                try:
                    register_user(db, email, password)
                    st.success("Account created. Log in to continue.")
                except PasswordValidationError as exc:
                    st.error(str(exc))
                except PasswordHashingError as exc:
                    st.error(str(exc))
                except ValueError as exc:
                    st.error(str(exc))
                except Exception:
                    st.error("Unable to create account. Please use a shorter password.")
                finally:
                    db.close()

        st.markdown("</div>", unsafe_allow_html=True)


def render_metric_grid(analysis: dict):
    metrics = derive_dashboard_metrics(analysis)
    html_grid = "".join(render_metric_card(metric) for metric in metrics)
    st.markdown(f"<div class='metric-grid'>{html_grid}</div>", unsafe_allow_html=True)


def render_analysis(analysis: dict, company_name: str, document_name: str, document_type: str):
    risk_label, risk_tone = derive_risk_level(int(analysis["financial_health_score"]))
    strengths_html = render_bullet_list(analysis["strengths"])
    risks_html = render_bullet_list(analysis["risks"])
    takeaways_html = render_bullet_list(analysis["investor_takeaways"])
    safe_company = html.escape(company_name)
    safe_document = html.escape(document_name)
    safe_document_type = html.escape(document_type)
    safe_revenue = html.escape(analysis["revenue_trends"])
    safe_profitability = html.escape(analysis["profitability_trends"])
    safe_debt = html.escape(analysis["debt_analysis"])
    safe_cash_flow = html.escape(analysis["cash_flow_analysis"])

    st.markdown("<div class='analysis-card'>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class='dashboard-hero'>
            <div>
                <div class='eyebrow'>Statement Intelligence Workspace</div>
                <div class='workspace-title'>{safe_company}</div>
                <div class='workspace-copy'>
                    {safe_document_type} review for <strong>{safe_document}</strong>. The layout below highlights the health score,
                    directional signals, and the most important investor-facing findings from the uploaded filing.
                </div>
            </div>
            <div>
                <div class='status-chip'>Analysis Ready</div>
                <div style='height:0.65rem'></div>
                <div class='signal-badge {risk_tone}'>{risk_label}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_metric_grid(analysis)

    summary_col, insight_col = st.columns([1.3, 1], gap="large")
    with summary_col:
        st.markdown(card_header("Executive View", "Executive Summary", analysis["executive_summary"]), unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class='analysis-grid'>
                <div class='analysis-block'>
                    <div class='card-title'>Revenue Trends</div>
                    <div class='card-copy'>{safe_revenue}</div>
                </div>
                <div class='analysis-block'>
                    <div class='card-title'>Profitability Trends</div>
                    <div class='card-copy'>{safe_profitability}</div>
                </div>
                <div class='analysis-block'>
                    <div class='card-title'>Debt Analysis</div>
                    <div class='card-copy'>{safe_debt}</div>
                </div>
                <div class='analysis-block'>
                    <div class='card-title'>Cash Flow Analysis</div>
                    <div class='card-copy'>{safe_cash_flow}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with insight_col:
        st.markdown("<div class='analysis-block'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Strengths</div>", unsafe_allow_html=True)
        st.markdown(strengths_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
        st.markdown("<div class='analysis-block'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Risks</div>", unsafe_allow_html=True)
        st.markdown(risks_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='ratio-table-title'>", unsafe_allow_html=True)
    st.markdown(card_header("Quant Layer", "Key Financial Ratios", "Ratio interpretations are preserved alongside the qualitative read so you can screen quickly."), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(display_ratio_table_rows(analysis)), use_container_width=True, hide_index=True)

    st.markdown("<div style='height:0.95rem'></div>", unsafe_allow_html=True)
    st.markdown("<div class='analysis-block'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>Investor Takeaways</div>", unsafe_allow_html=True)
    st.markdown(takeaways_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _load_history():
    db = get_db()
    try:
        return repository.list_analyses_for_user(db, st.session_state["user_id"])
    finally:
        db.close()


def _remember_current_analysis(company_name: str, document_name: str, document_type: str, analysis: dict):
    st.session_state["current_analysis"] = analysis
    st.session_state["current_company_name"] = company_name
    st.session_state["current_document_name"] = document_name
    st.session_state["current_document_type"] = document_type


def render_dashboard():
    analyses = _load_history()
    selected_analysis = st.session_state["current_analysis"] or (analyses[0].analysis_json if analyses else None)
    selected_company = st.session_state["current_company_name"] or (analyses[0].company_name if analyses else "No company selected")
    selected_document = st.session_state["current_document_name"] or (analyses[0].document_name if analyses else "Awaiting upload")
    selected_type = st.session_state["current_document_type"] or (analyses[0].document_type if analyses else "Uploaded Document")

    st.markdown("<div class='platform-shell'>", unsafe_allow_html=True)
    header_left, header_right = st.columns([4.3, 1], gap="large")
    with header_left:
        st.markdown(
            """
            <div class='eyebrow'>Market Intelligence Platform</div>
            <div class='workspace-title'>StatementIQ Workspace</div>
            <div class='workspace-copy'>
                Screen filings, evaluate financial strength, and turn dense disclosures into an organized decision-ready dashboard.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with header_right:
        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='signal-badge success'>{st.session_state['user_email']}</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:0.65rem'></div>", unsafe_allow_html=True)
        if st.button("Log out", use_container_width=True):
            st.session_state["user_id"] = None
            st.session_state["user_email"] = None
            st.session_state["current_analysis"] = None
            st.session_state["current_company_name"] = None
            st.session_state["current_document_name"] = None
            st.session_state["current_document_type"] = None
            st.rerun()

    if selected_analysis:
        render_metric_grid(selected_analysis)
    else:
        st.markdown(
            """
            <div class='metric-grid'>
                <div class='metric-card primary'><div class='metric-label'>Financial Health</div><div class='metric-value'>--</div><div class='metric-note'>Upload a filing to generate the first score.</div></div>
                <div class='metric-card success'><div class='metric-label'>Revenue</div><div class='metric-value'>Pending</div><div class='metric-note'>Trend signal appears after analysis completes.</div></div>
                <div class='metric-card warning'><div class='metric-label'>Debt</div><div class='metric-value'>Pending</div><div class='metric-note'>Leverage commentary appears after analysis completes.</div></div>
                <div class='metric-card success'><div class='metric-label'>Cash Flow</div><div class='metric-value'>Pending</div><div class='metric-note'>Liquidity and cash conversion appear after analysis completes.</div></div>
                <div class='metric-card danger'><div class='metric-label'>Risk Level</div><div class='metric-value'>Pending</div><div class='metric-note'>Risk signal is derived from the score.</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    upload_col, history_col = st.columns([1.1, 0.9], gap="large")

    with upload_col:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown(card_header("New Analysis", "Upload a financial filing", "Drag in a text-based PDF, 10-K, 10-Q, or core statement to generate a structured institutional-style readout."), unsafe_allow_html=True)
        company_name = st.text_input("Company Name", placeholder="Apple Inc.")
        document_type = st.selectbox(
            "Document Type",
            ["Annual Report", "10-K", "10-Q", "Income Statement", "Balance Sheet", "Cash Flow Statement", "Other"],
        )
        st.markdown("<div class='uploader-frame'>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            f"Upload document ({', '.join(sorted(SUPPORTED_EXTENSIONS))})",
            type=list(SUPPORTED_EXTENSIONS),
            help="Best results come from text-based PDFs and machine-readable filings.",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Analyze Document", type="primary", use_container_width=True):
            if not company_name or not uploaded_file:
                st.error("Company name and upload are required.")
            else:
                with st.spinner("Extracting text and generating analysis..."):
                    try:
                        extracted_text = extract_text_from_upload(uploaded_file)
                        analysis = analyze_financial_document(extracted_text)
                        db = get_db()
                        try:
                            saved_analysis = repository.create_analysis(
                                db_session=db,
                                user_id=st.session_state["user_id"],
                                company_name=company_name,
                                document_name=uploaded_file.name,
                                document_type=document_type,
                                extracted_text=extracted_text,
                                analysis_json=analysis,
                                financial_health_score=analysis["financial_health_score"],
                            )
                        finally:
                            db.close()

                        _remember_current_analysis(company_name, uploaded_file.name, document_type, analysis)
                        st.success("Analysis complete.")
                        render_analysis(analysis, company_name, uploaded_file.name, document_type)
                        pdf_bytes = build_analysis_pdf(company_name, uploaded_file.name, analysis)
                        st.download_button(
                            "Download PDF Report",
                            data=pdf_bytes,
                            file_name=f"{company_name.lower().replace(' ', '_')}_statementiq_report.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"pdf_{saved_analysis.id}",
                        )
                    except Exception as exc:
                        st.error(f"Analysis failed: {exc}")

        if selected_analysis:
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            render_analysis(selected_analysis, selected_company, selected_document, selected_type)
            selected_pdf = build_analysis_pdf(selected_company, selected_document, selected_analysis)
            st.download_button(
                "Export Active Analysis",
                data=selected_pdf,
                file_name=f"{selected_company.lower().replace(' ', '_')}_active_analysis.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="active_pdf_export",
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with history_col:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown(card_header("Research Log", "Analysis history", "Reopen past analyses, compare score snapshots, and export prior reports without rerunning the filing."), unsafe_allow_html=True)
        if not analyses:
            st.caption("No analyses yet. Upload a financial document to populate the research log.")
        else:
            for item in analyses:
                risk_label, risk_tone = derive_risk_level(item.financial_health_score)
                with st.expander(f"{item.company_name} • {item.document_type} • {item.financial_health_score}/100"):
                    st.markdown(f"<div class='signal-badge {risk_tone}'>{risk_label}</div>", unsafe_allow_html=True)
                    st.caption(item.created_at.strftime("%Y-%m-%d %H:%M UTC"))
                    st.write(item.document_name)
                    if st.button("Open Analysis", key=f"open_{item.id}", use_container_width=True):
                        _remember_current_analysis(item.company_name, item.document_name, item.document_type, item.analysis_json)
                        st.rerun()
                    pdf_bytes = build_analysis_pdf(item.company_name, item.document_name, item.analysis_json)
                    st.download_button(
                        "Export PDF",
                        data=pdf_bytes,
                        file_name=f"{item.company_name.lower().replace(' ', '_')}_{item.id}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"history_pdf_{item.id}",
                    )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def main():
    init_session_state()
    if not DB_READY:
        st.error("Database connection failed. Check `DATABASE_URL` and rerun the app.")
        st.stop()
    if not st.session_state["user_id"]:
        render_auth()
        return
    render_dashboard()


if __name__ == "__main__":
    main()
