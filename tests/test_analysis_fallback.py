import os
import unittest

from app.services.analysis import analyze_financial_document


class AnalysisFallbackTest(unittest.TestCase):
    def test_fallback_analysis_returns_required_keys(self):
        os.environ["OPENAI_API_KEY"] = ""
        result = analyze_financial_document("Revenue was $1000 and cash flow improved while debt declined.")
        self.assertIn("financial_health_score", result)
        self.assertIn("executive_summary", result)
        self.assertEqual(len(result["strengths"]), 3)


if __name__ == "__main__":
    unittest.main()
