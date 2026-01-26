"""
⚠️ DEPRECATED: This rule-based sentiment analyzer is no longer used.

Use app/services/sentiment_ml.py instead for production sentiment analysis.
This file is kept for backward compatibility only.

The new ML-based sentiment service uses:
- Model: cardiffnlp/twitter-roberta-base-sentiment-latest
- Returns: Positive, Neutral, Negative with confidence scores (0-1)
- Caching: Integrated with Redis for performance
"""

import re
from typing import Dict


class SentimentAnalyzer:
    """
    ⚠️ DEPRECATED: Rule-based sentiment analyzer.
    Use SentimentService from sentiment_ml.py instead.
    """

    POSITIVE_WORDS = {
        "good", "great", "positive", "success", "growth", "benefit",
        "improve", "strong", "profit", "gain", "happy", "win", "excellent"
    }

    NEGATIVE_WORDS = {
        "bad", "poor", "negative", "loss", "decline", "fail",
        "weak", "drop", "crisis", "risk", "sad", "fall", "problem"
    }

    NEGATIONS = {"not", "no", "never", "hardly"}

    def analyze(self, text: str) -> Dict:
        """
        ⚠️ DEPRECATED: Analyze sentiment of given text using rule-based approach.
        This is inaccurate and should not be used for production.
        Use SentimentService.analyze() from sentiment_ml.py instead.
        """

        words = self._tokenize(text)

        score = 0
        negate = False

        for word in words:
            if word in self.NEGATIONS:
                negate = True
                continue

            if word in self.POSITIVE_WORDS:
                score += -1 if negate else 1
                negate = False

            elif word in self.NEGATIVE_WORDS:
                score += 1 if negate else -1
                negate = False

        normalized_score = max(min(score / 10, 1), -1)

        return {
            "sentiment": self._label(normalized_score),
            "score": round(normalized_score, 2),
        }

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------
    def _tokenize(self, text: str):
        text = text.lower()
        return re.findall(r"\b[a-z]+\b", text)

    def _label(self, score: float) -> str:
        if score > 0.1:
            return "Positive"
        elif score < -0.1:
            return "Negative"
        return "Neutral"

