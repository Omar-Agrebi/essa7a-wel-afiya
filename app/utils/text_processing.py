"""
Utility functions for text cleaning and preprocessing.
Standalone module — no framework imports.
"""
import re
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import CountVectorizer


def clean_html(text: str) -> str:
    """
    Strip HTML tags and return plain text.

    Args:
        text: HTML or plain text string.

    Returns:
        str: Plain text with HTML tags removed.
    """
    return BeautifulSoup(text, "html.parser").get_text(separator=" ", strip=True)


def remove_special_chars(text: str) -> str:
    """
    Remove special characters, keeping alphanumeric, spaces, and basic punctuation.

    Args:
        text: Input string.

    Returns:
        str: Cleaned string with only safe characters retained.
    """
    return re.sub(r"[^a-zA-Z0-9\s.,;:!?'\"-]", "", text)


def normalize_whitespace(text: str) -> str:
    """
    Collapse multiple spaces, tabs, and newlines into a single space and strip.

    Args:
        text: Input string.

    Returns:
        str: Whitespace-normalized string.
    """
    return re.sub(r"\s+", " ", text).strip()


def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    """
    Extract the top_n most frequent terms from a single text using CountVectorizer.

    Args:
        text: Input text string.
        top_n: Number of top keywords to return.

    Returns:
        list[str]: Top keyword strings by frequency.
    """
    try:
        vectorizer = CountVectorizer(stop_words="english", max_features=top_n)
        vectorizer.fit([text])
        terms = vectorizer.get_feature_names_out().tolist()
        return terms
    except Exception:
        return []


def truncate(text: str, max_chars: int = 500) -> str:
    """
    Truncate text to max_chars and append '...' if truncated.

    Args:
        text: Input string.
        max_chars: Maximum number of characters to keep.

    Returns:
        str: Truncated string, with '...' appended if truncation occurred.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."
