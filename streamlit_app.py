import uuid

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from app.components.theme import inject_theme
from app.db import repository
from app.db.session import SessionLocal, init_db
from app.services.analysis import analyze_financial_document
from app.services.auth import authenticate_user, register_user
from app.services.extractor import SUPPORTED_EXTENSIONS, extract_text_from_upload
from app.services.report_export import build_analysis_pdf
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


def render_auth():
    st.markdown("<div class='hero-card'>", unsafe_allow_html=True)
    st.title("StatementIQ")
    st.caption("AI-powered financial statement analysis for investors, operators, and advisors.")

    tab_login, tab_signup = st.tabs(["Login", "Create account"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
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
            finally:
                db.close()

    with tab_signup:
        with st.form("signup_form"):
            email = st.text_input("Work Email")
            password = st.text_input("Create Password", type="password")
            submitted = st.form_submit_button("Create account", use_container_width=True)
        if submitted:
            if len(password) < 8:
                st.error("Password must be at least 8 characters.")
            else:
                db = get_db()
                try:
                    register_user(db, email, password)
                    st.success("Account created. Log in to continue.")
                except ValueError as exc:
                    st.error(str(exc))
                finally:
                    db.close()

    st.markdown("</div>", unsafe_allow_html=True)


def render_analysis(analysis: dict):
    score = analysis["financial_health_score"]
    st.markdown(f"<div class='metric-pill'>Financial Health Score: {score}/100</div>", unsafe_allow_html=True)
    st.subheader("Executive Summary")
    st.write(analysis["executive_summary"])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Strengths")
        for item in analysis["strengths"]:
            st.write(f"- {item}")
        st.subheader("Revenue Trends")
        st.write(analysis["revenue_trends"])
        st.subheader("Debt Analysis")
        st.write(analysis["debt_analysis"])
    with col2:
        st.subheader("Risks")
        for item in analysis["risks"]:
            st.write(f"- {item}")
        st.subheader("Profitability Trends")
        st.write(analysis["profitability_trends"])
        st.subheader("Cash Flow Analysis")
        st.write(analysis["cash_flow_analysis"])

    st.subheader("Key Financial Ratios")
    st.dataframe(pd.DataFrame(display_ratio_table_rows(analysis)), use_container_width=True, hide_index=True)

    st.subheader("Investor Takeaways")
    for item in analysis["investor_takeaways"]:
        st.write(f"- {item}")


def render_dashboard():
    top_left, top_right = st.columns([3, 1])
    with top_left:
        st.title("StatementIQ Workspace")
        st.caption("Upload filings and financial statements, then generate a structured investment-readiness analysis.")
    with top_right:
        st.write("")
        st.write(f"Signed in as `{st.session_state['user_email']}`")
        if st.button("Log out", use_container_width=True):
            st.session_state["user_id"] = None
            st.session_state["user_email"] = None
            st.rerun()

    upload_col, history_col = st.columns([1.7, 1.1], gap="large")

    with upload_col:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("New Analysis")
        company_name = st.text_input("Company Name", placeholder="Apple Inc.")
        document_type = st.selectbox(
            "Document Type",
            ["Annual Report", "10-K", "10-Q", "Income Statement", "Balance Sheet", "Cash Flow Statement", "Other"],
        )
        uploaded_file = st.file_uploader(
            f"Upload document ({', '.join(sorted(SUPPORTED_EXTENSIONS))})",
            type=list(SUPPORTED_EXTENSIONS),
        )

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
                                user_id=uuid.UUID(st.session_state["user_id"]),
                                company_name=company_name,
                                document_name=uploaded_file.name,
                                document_type=document_type,
                                extracted_text=extracted_text,
                                analysis_json=analysis,
                                financial_health_score=analysis["financial_health_score"],
                            )
                        finally:
                            db.close()

                        st.success("Analysis complete.")
                        render_analysis(analysis)
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
        st.markdown("</div>", unsafe_allow_html=True)

    with history_col:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.subheader("Analysis History")
        db = get_db()
        try:
            analyses = repository.list_analyses_for_user(db, st.session_state["user_id"])
        finally:
            db.close()

        if not analyses:
            st.caption("No analyses yet. Upload a financial document to get started.")
        else:
            for item in analyses:
                with st.expander(f"{item.company_name} • {item.document_type} • Score {item.financial_health_score}"):
                    st.write(item.document_name)
                    st.caption(item.created_at.strftime("%Y-%m-%d %H:%M UTC"))
                    render_analysis(item.analysis_json)
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


def main():
    init_session_state()
    if not DB_READY:
        st.error("Database connection failed. Check `DATABASE_URL`, start PostgreSQL, and rerun the app.")
        st.stop()
    if not st.session_state["user_id"]:
        render_auth()
        return
    render_dashboard()


if __name__ == "__main__":
    main()
