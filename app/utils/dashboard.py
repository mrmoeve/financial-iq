import html
import re


def _signal_from_text(text: str, good_terms: list[str], bad_terms: list[str], neutral: str, good: str, bad: str):
    lowered = text.lower()
    if any(term in lowered for term in good_terms):
        return good
    if any(term in lowered for term in bad_terms):
        return bad
    return neutral


def derive_risk_level(score: int) -> tuple[str, str]:
    if score >= 80:
        return "Low Risk", "success"
    if score >= 65:
        return "Moderate Risk", "warning"
    return "Elevated Risk", "danger"


def derive_dashboard_metrics(analysis: dict) -> list[dict]:
    score = int(analysis.get("financial_health_score", 0))
    revenue_signal = _signal_from_text(
        analysis.get("revenue_trends", ""),
        ["grow", "growth", "increase", "expansion", "strong", "accelerat"],
        ["decline", "drop", "contraction", "soft", "pressure"],
        "Stable",
        "Growing",
        "Softening",
    )
    debt_signal = _signal_from_text(
        analysis.get("debt_analysis", ""),
        ["manageable", "contained", "improving", "low leverage", "disciplined"],
        ["leveraged", "pressure", "high debt", "refinancing", "covenant"],
        "Watch",
        "Contained",
        "Pressured",
    )
    cash_flow_signal = _signal_from_text(
        analysis.get("cash_flow_analysis", ""),
        ["strong", "improving", "positive", "healthy", "resilient"],
        ["weak", "negative", "strained", "volatile", "burn"],
        "Mixed",
        "Healthy",
        "Tight",
    )
    risk_label, risk_tone = derive_risk_level(score)

    return [
        {"label": "Financial Health", "value": f"{score}/100", "note": "Composite quality score from the uploaded filing.", "tone": "primary"},
        {"label": "Revenue", "value": revenue_signal, "note": analysis.get("revenue_trends", "Revenue direction is not clearly disclosed."), "tone": "success" if revenue_signal == "Growing" else "warning"},
        {"label": "Debt", "value": debt_signal, "note": analysis.get("debt_analysis", "Debt posture is not clearly disclosed."), "tone": "danger" if debt_signal == "Pressured" else "success"},
        {"label": "Cash Flow", "value": cash_flow_signal, "note": analysis.get("cash_flow_analysis", "Cash flow quality is not clearly disclosed."), "tone": "success" if cash_flow_signal == "Healthy" else "warning"},
        {"label": "Risk Level", "value": risk_label, "note": "Derived from the current financial health score.", "tone": risk_tone},
    ]


def extract_summary_snippet(text: str) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    if not clean:
        return "Not clearly disclosed."
    return clean[:150].rstrip(" .,;:") + ("..." if len(clean) > 150 else "")


def render_metric_card(metric: dict) -> str:
    return (
        f"<div class='metric-card {html.escape(metric['tone'])}'>"
        f"<div class='metric-label'>{html.escape(metric['label'])}</div>"
        f"<div class='metric-value'>{html.escape(metric['value'])}</div>"
        f"<div class='metric-note'>{html.escape(extract_summary_snippet(metric['note']))}</div>"
        f"</div>"
    )


def render_bullet_list(items: list[str]) -> str:
    blocks = "".join(f"<div class='bullet-item'>{html.escape(item)}</div>" for item in items)
    return f"<div class='bullet-list'>{blocks}</div>"
