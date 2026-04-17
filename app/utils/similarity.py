"""
Utility functions for vector and set-based similarity computation.
Standalone module — no framework imports.
"""
import numpy as np


def cosine_sim(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Compute safe cosine similarity between two numpy arrays.
    Returns 0.0 if either vector is a zero vector.

    Args:
        v1: First vector.
        v2: Second vector.

    Returns:
        float: Cosine similarity in range [-1.0, 1.0], or 0.0 for zero vectors.
    """
    norm1 = float(np.linalg.norm(v1))
    norm2 = float(np.linalg.norm(v2))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))


def jaccard_similarity(set1: set, set2: set) -> float:
    """
    Compute Jaccard similarity between two sets.

    Args:
        set1: First set.
        set2: Second set.

    Returns:
        float: |intersection| / |union|, or 0.0 if both sets are empty.
    """
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return float(intersection) / float(union) if union > 0 else 0.0


def skill_overlap_score(
    user_skills: list[str], opp_skills: list[str]
) -> float:
    """
    Compute skill overlap score between user skills and opportunity required skills.
    Uses Jaccard similarity with case-insensitive comparison.

    Args:
        user_skills: List of user skill strings.
        opp_skills: List of opportunity required skill strings.

    Returns:
        float: Overlap ratio in range [0.0, 1.0].
    """
    set1 = {s.lower().strip() for s in user_skills}
    set2 = {s.lower().strip() for s in opp_skills}
    return jaccard_similarity(set1, set2)
