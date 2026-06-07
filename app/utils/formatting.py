def display_ratio_table_rows(analysis: dict) -> list[dict]:
    return [
        {
            "Ratio": item.get("name", ""),
            "Value": item.get("value", ""),
            "Insight": item.get("insight", ""),
        }
        for item in analysis.get("key_financial_ratios", [])
    ]
