import re
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


class TextSummarizer:
    """
    Extractive text summarizer using classical NLP techniques.
    No AI models are used.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_df=0.9,
            min_df=2
        )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------
    def summarize(self, text: str, max_sentences: int = 6) -> str:
        """
        Generate a summary from article text.

        :param text: full article content
        :param max_sentences: number of sentences in summary
        :return: summarized text
        """

        sentences = self._split_into_sentences(text)

        if len(sentences) <= max_sentences:
            return text.strip()

        scores = self._score_sentences(sentences)
        top_indices = self._select_top_sentences(scores, max_sentences)

        # Keep original order for readability
        top_indices.sort()

        summary = " ".join(sentences[i] for i in top_indices)
        return summary.strip()

    # --------------------------------------------------
    # Internal Helpers
    # --------------------------------------------------
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split article text into sentences.
        """
        text = re.sub(r"\s+", " ", text)
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if len(s.strip()) > 40]

    def _score_sentences(self, sentences: List[str]) -> np.ndarray:
        """
        Score each sentence using TF-IDF.
        """
        tfidf_matrix = self.vectorizer.fit_transform(sentences)

        # Sentence importance = sum of TF-IDF values
        scores = tfidf_matrix.sum(axis=1).A1

        # Position bias (earlier sentences slightly more important)
        position_weight = np.linspace(1.2, 0.8, len(scores))
        scores = scores * position_weight

        return scores

    def _select_top_sentences(
        self, scores: np.ndarray, max_sentences: int
    ) -> List[int]:
        """
        Select indices of top-ranked sentences.
        """
        ranked_indices = np.argsort(scores)[::-1]
        return ranked_indices[:max_sentences].tolist()
