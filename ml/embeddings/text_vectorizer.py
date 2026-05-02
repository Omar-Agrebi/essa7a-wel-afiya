"""
SpaCy-based text vectorizer for NLP preprocessing and embedding extraction.
No FastAPI, SQLAlchemy, or agent imports allowed in this module.
"""
import logging
import numpy as np

logger = logging.getLogger(__name__)


class TextVectorizer:
    """
    Utility class for NLP text preprocessing using spaCy.
    Provides lemmatization, stopword removal, embedding extraction,
    and cosine similarity computation via spaCy's en_core_web_sm model.
    """

    def __init__(self) -> None:
        """
        Load spaCy's en_core_web_sm model.

        Raises:
            RuntimeError: If the spaCy model is not installed.
        """
        try:
            import spacy
            self._nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' is not installed. "
                "Run: python -m spacy download en_core_web_sm"
            )

    def preprocess(self, text: str) -> str:
        """
        Lemmatize and remove stopwords and punctuation from text.

        Args:
            text: Raw input string.

        Returns:
            str: Space-joined lemmatized tokens (alpha, non-stop).
        """
        doc = self._nlp(text)
        tokens = [
            token.lemma_.lower()
            for token in doc
            if token.is_alpha and not token.is_stop and not token.is_punct
        ]
        return " ".join(tokens)

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Get spaCy document vector for given text (300-dimensional).

        Args:
            text: Raw input string.

        Returns:
            np.ndarray: 300-dim document vector.
        """
        preprocessed = self.preprocess(text)
        doc = self._nlp(preprocessed)
        return doc.vector.copy()

    def batch_embed(self, texts: list[str]) -> np.ndarray:
        """
        Get embeddings for a list of texts.

        Args:
            texts: List of raw input strings.

        Returns:
            np.ndarray: Shape (n_texts, 300) embedding matrix.
        """
        return np.array([self.get_embedding(t) for t in texts])

    def cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors. Returns 0.0 for zero vectors.

        Args:
            v1: First vector.
            v2: Second vector.

        Returns:
            float: Cosine similarity in range [0.0, 1.0].
        """
        norm1 = float(np.linalg.norm(v1))
        norm2 = float(np.linalg.norm(v2))
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        return float(np.dot(v1, v2) / (norm1 * norm2))
