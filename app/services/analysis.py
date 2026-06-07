import json
import re
from statistics import mean

from openai import OpenAI

from app.config import get_settings


PROMPT_TEMPLATE = """
You are a senior equity research analyst.
Analyze the following company financial statement or filing text and return valid JSON only.

Return this schema:
{
  "financial_health_score": integer from 0 to 100,
  "executive_summary": string,
  "strengths": [string, string, string],
  "risks": [string, string, string],
  "revenue_trends": string,
  "profitability_trends": string,
  "debt_analysis": string,
  "cash_flow_analysis": string,
  "key_financial_ratios": [
    {"name": string, "value": string, "insight": string}
  ],
  "investor_takeaways": [string, string, string]
}

Ground the answer in the provided text. If a metric is unavailable, say it is not clearly disclosed.

Document text:
{document_text}
"""


def _extract_currency_values(text: str) -> list[float]:
    matches = re.findall(r"\$?\s?(\d[\d,]*(?:\.\d+)?)", text)
    values = []
    for item in matches[:200]:
        try:
            values.append(float(item.replace(",", "")))
        except ValueError:
            continue
    return values


def _fallback_analysis(document_text: str) -> dict:
    values = _extract_currency_values(document_text)
    average_value = mean(values) if values else 0.0
    score = 60
    if average_value > 1_000:
        score += 10
    if "risk" in document_text.lower():
        score -= 5
    if "debt" in document_text.lower():
        score -= 5
    score = max(0, min(100, int(score)))

    return {
        "financial_health_score": score,
        "executive_summary": "This filing presents a mixed but investable profile based on the extracted disclosures.",
        "strengths": [
            "The document contains detailed financial disclosures that support structured review.",
            "Reported scale appears meaningful relative to smaller issuers.",
            "Management commentary and statement sections provide enough context for an initial assessment.",
        ],
        "risks": [
            "The uploaded text may omit tables or scanned content that could alter the conclusion.",
            "Debt, liquidity, or margin signals may not be fully quantified in the extracted text.",
            "This MVP summary is directional and should be validated against source statements.",
        ],
        "revenue_trends": "Revenue trend indicators should be confirmed against period-over-period figures in the source filing.",
        "profitability_trends": "Profitability appears stable to mixed based on the available narrative, but exact margin trends are not clearly disclosed.",
        "debt_analysis": "Debt obligations and leverage should be reviewed carefully because the extracted text alone may not preserve note detail.",
        "cash_flow_analysis": "Cash flow quality cannot be fully confirmed unless the statement of cash flows and related notes are clearly present.",
        "key_financial_ratios": [
            {"name": "Liquidity Coverage", "value": "Not clearly disclosed", "insight": "Source figures are required for calculation."},
            {"name": "Debt Load", "value": "Not clearly disclosed", "insight": "Leverage metrics depend on preserved balance sheet values."},
            {"name": "Profit Margin", "value": "Not clearly disclosed", "insight": "Income statement details were not normalized automatically."},
        ],
        "investor_takeaways": [
            "Use this report as a first-pass screening view rather than a final investment opinion.",
            "Cross-check headline conclusions against the original tables and footnotes.",
            "Prioritize revenue growth, margins, leverage, and operating cash flow in follow-up review.",
        ],
    }


def analyze_financial_document(document_text: str) -> dict:
    settings = get_settings()
    if not settings.openai_api_key:
        return _fallback_analysis(document_text)

    client = OpenAI(api_key=settings.openai_api_key)
    prompt = PROMPT_TEMPLATE.format(document_text=document_text[:120000])

    try:
        response = client.responses.create(
            model=settings.openai_model,
            input=prompt,
            temperature=0.2,
        )
        raw_output = response.output_text.strip()
        if raw_output.startswith("```"):
            raw_output = raw_output.strip("`")
            raw_output = raw_output.replace("json\n", "", 1)
        parsed = json.loads(raw_output)
        return parsed
    except Exception:
        return _fallback_analysis(document_text)
