from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _section(title: str, body: str, styles) -> list:
    return [
        Paragraph(title, styles["Heading2"]),
        Spacer(1, 0.08 * inch),
        Paragraph(body, styles["BodyText"]),
        Spacer(1, 0.16 * inch),
    ]


def build_analysis_pdf(company_name: str, document_name: str, analysis: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Meta", fontSize=10, textColor=colors.grey))

    elements = [
        Paragraph(f"StatementIQ Report: {company_name}", styles["Title"]),
        Spacer(1, 0.1 * inch),
        Paragraph(f"Source Document: {document_name}", styles["Meta"]),
        Spacer(1, 0.2 * inch),
        Paragraph(f"Financial Health Score: {analysis['financial_health_score']}/100", styles["Heading2"]),
        Spacer(1, 0.16 * inch),
    ]

    elements.extend(_section("Executive Summary", analysis["executive_summary"], styles))
    elements.extend(_section("Revenue Trends", analysis["revenue_trends"], styles))
    elements.extend(_section("Profitability Trends", analysis["profitability_trends"], styles))
    elements.extend(_section("Debt Analysis", analysis["debt_analysis"], styles))
    elements.extend(_section("Cash Flow Analysis", analysis["cash_flow_analysis"], styles))

    strengths = "<br/>".join(f"- {item}" for item in analysis["strengths"])
    risks = "<br/>".join(f"- {item}" for item in analysis["risks"])
    takeaways = "<br/>".join(f"- {item}" for item in analysis["investor_takeaways"])
    elements.extend(_section("Strengths", strengths, styles))
    elements.extend(_section("Risks", risks, styles))
    elements.extend(_section("Investor Takeaways", takeaways, styles))

    rows = [["Ratio", "Value", "Insight"]]
    for ratio in analysis["key_financial_ratios"]:
        rows.append([ratio["name"], ratio["value"], ratio["insight"]])
    ratio_table = Table(rows, colWidths=[1.7 * inch, 1.4 * inch, 3.6 * inch])
    ratio_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#f8fafc")]),
            ]
        )
    )
    elements.append(Paragraph("Key Financial Ratios", styles["Heading2"]))
    elements.append(Spacer(1, 0.08 * inch))
    elements.append(ratio_table)

    doc.build(elements)
    return buffer.getvalue()
