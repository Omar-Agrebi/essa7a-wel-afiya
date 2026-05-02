"""
Standalone ML recommender for scoring and ranking opportunities per user.
No FastAPI, SQLAlchemy, or agent imports allowed in this module.
"""
import logging
from datetime import date
import dateparser
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

logger = logging.getLogger(__name__)


class OpportunityRecommender:
    """
    TF-IDF cosine similarity recommender.
    Scores opportunities against user profiles on three dimensions:
      - Semantic similarity (TF-IDF cosine)
      - Academic level match
      - Deadline recency
    Produces final_score and human-readable match_reasons per opportunity.
    """

    def __init__(self) -> None:
        """Initialize recommender with empty state."""
        self.vectorizer: TfidfVectorizer | None = None
        self.opportunity_matrix = None
        self.is_fitted: bool = False

    # ── Text helpers ─────────────────────────────────────────────────────────

    def _build_text(self, opp: dict) -> str:
        """
        Build a combined text string from an opportunity dict.

        Args:
            opp: Opportunity dict with title, description, skills_required.

        Returns:
            str: Combined text for TF-IDF vectorization.
        """
        title = opp.get("title") or ""
        desc = opp.get("description") or ""
        skills = " ".join(opp.get("skills_required") or [])
        category = opp.get("category") or ""
        return f"{title} {desc} {skills} {category}".strip()

    def _build_user_text(self, user: dict) -> str:
        """
        Build a combined text string from a user profile dict.

        Args:
            user: User dict with skills and interests.

        Returns:
            str: Combined text for TF-IDF vectorization.
        """
        skills = " ".join(user.get("skills") or [])
        interests = " ".join(user.get("interests") or [])
        return f"{skills} {interests}".strip()

    # ── Fit ──────────────────────────────────────────────────────────────────

    def fit(self, opportunities: list[dict]) -> None:
        """
        Build the TF-IDF opportunity matrix from a list of opportunity dicts.
        Must be called before compute_similarity_scores or recommend.

        Args:
            opportunities: List of opportunity dicts.
        """
        texts = [self._build_text(opp) for opp in opportunities]
        self.vectorizer = TfidfVectorizer(
            max_features=5000, stop_words="english"
        )
        self.opportunity_matrix = self.vectorizer.fit_transform(texts)
        self.is_fitted = True
        logger.debug(
            f"OpportunityRecommender fitted on {len(opportunities)} opportunities."
        )

    # ── Scoring helpers ──────────────────────────────────────────────────────

    def compute_similarity_scores(
        self, user: dict, opportunities: list[dict]
    ) -> list[float]:
        """
        Compute cosine similarity between the user profile and all opportunities.

        Args:
            user: User dict with skills and interests.
            opportunities: List of opportunity dicts (must match what was fitted).

        Returns:
            list[float]: Similarity score per opportunity (0.0 – 1.0).
        """
        assert self.is_fitted, "Recommender must be fitted before scoring."
        user_text = self._build_user_text(user)
        user_vec = self.vectorizer.transform([user_text])
        scores = cosine_similarity(user_vec, self.opportunity_matrix)[0]
        return scores.tolist()

    def compute_level_match(
        self, user_level: str, eligibility: str | None
    ) -> float:
        """
        Compute academic level match score.

        Args:
            user_level: User's academic level string.
            eligibility: Opportunity eligibility text.

        Returns:
            float: 1.0 exact match, 0.3–0.5 adjacent, 0.5 unknown, 0.0 incompatible.
        """
        if eligibility is None:
            return 0.5
        user_lower = user_level.lower().strip()
        elig_lower = eligibility.lower()
        if user_lower in elig_lower:
            return 1.0
        adjacent: dict[tuple[str, str], float] = {
            ("bachelor", "master"): 0.5,
            ("master", "bachelor"): 0.3,
            ("master", "phd"): 0.5,
            ("phd", "master"): 0.4,
            ("phd", "postdoc"): 0.5,
            ("postdoc", "phd"): 0.4,
        }
        for (lvl1, lvl2), score in adjacent.items():
            if user_lower == lvl1 and lvl2 in elig_lower:
                return score
        return 0.0

    def compute_recency_score(self, deadline: str | None) -> float:
        """
        Compute deadline recency score.

        Args:
            deadline: Raw deadline string or None.

        Returns:
            float: 1.0 far future, 0.5 medium, 0.2 urgent, 0.0 expired, 0.3 unknown.
        """
        if deadline is None:
            return 0.3
        try:
            parsed = dateparser.parse(
                deadline,
                settings={"RETURN_AS_TIMEZONE_AWARE": False, "PREFER_FUTURE_DATES": True},
            )
            if parsed is None:
                return 0.3
            days_left = (parsed.date() - date.today()).days
            if days_left > 30:
                return 1.0
            if days_left >= 10:
                return 0.5
            if days_left >= 0:
                return 0.2
            return 0.0
        except Exception:
            return 0.3

    def generate_match_reasons(
        self,
        user: dict,
        opp: dict,
        similarity: float,
        level_match: float,
        recency: float,
    ) -> list[str]:
        """
        Generate human-readable reasons explaining why an opportunity was recommended.

        Args:
            user: User profile dict.
            opp: Opportunity dict.
            similarity: Cosine similarity score.
            level_match: Level match score.
            recency: Recency score.

        Returns:
            list[str]: List of reason strings.
        """
        reasons: list[str] = []

        # Skill overlap
        user_skills = {s.lower() for s in (user.get("skills") or [])}
        opp_skills = {s.lower() for s in (opp.get("skills_required") or [])}
        overlap = user_skills & opp_skills
        if overlap:
            top = list(overlap)[:3]
            reasons.append(
                f"{len(overlap)} of your skills match ({', '.join(top)})"
            )

        # Level match
        if level_match == 1.0:
            level_str = (user.get("level") or "").title()
            reasons.append(f"{level_str} level compatible")

        # Semantic similarity
        if similarity > 0.3:
            reasons.append(f"High relevance ({similarity:.0%} match)")

        # Urgency
        if recency == 0.2:
            deadline_str = opp.get("deadline")
            if deadline_str:
                try:
                    parsed = dateparser.parse(
                        deadline_str,
                        settings={"RETURN_AS_TIMEZONE_AWARE": False},
                    )
                    if parsed:
                        days = (parsed.date() - date.today()).days
                        reasons.append(
                            f"Deadline in {days} day(s) — apply soon"
                        )
                except Exception:
                    pass

        # Interest alignment
        user_interests_str = " ".join(user.get("interests") or []).lower()
        opp_category = opp.get("category") or ""
        if opp_category.lower() in user_interests_str:
            reasons.append(f"Matches your interest in {opp_category}")

        if not reasons:
            reasons.append("Recommended based on your profile")

        return reasons

    # ── Full recommendation ──────────────────────────────────────────────────

    def recommend(
        self,
        user: dict,
        opportunities: list[dict],
        top_n: int = 10,
        w1: float = 0.5,
        w2: float = 0.3,
        w3: float = 0.2,
    ) -> list[dict]:
        """
        Full recommendation pass: fit, score, rank, and return top_n results.

        Args:
            user: User profile dict.
            opportunities: List of all available opportunities.
            top_n: Maximum number of results to return.
            w1: Weight for cosine similarity.
            w2: Weight for level match.
            w3: Weight for recency.

        Returns:
            list[dict]: Top-N opportunities with 'final_score' and 'match_reasons' added.
        """
        if not opportunities:
            return []

        self.fit(opportunities)
        similarity_scores = self.compute_similarity_scores(user, opportunities)

        ranked: list[dict] = []
        for opp, sim in zip(opportunities, similarity_scores):
            level_match = self.compute_level_match(
                user.get("level", ""), opp.get("eligibility")
            )
            recency = self.compute_recency_score(opp.get("deadline"))
            final_score = w1 * sim + w2 * level_match + w3 * recency
            reasons = self.generate_match_reasons(
                user, opp, sim, level_match, recency
            )
            enriched = dict(opp)
            enriched["final_score"] = float(final_score)
            enriched["match_reasons"] = reasons
            ranked.append(enriched)

        ranked.sort(key=lambda x: x["final_score"], reverse=True)
        return ranked[:top_n]

    # ── Persistence ──────────────────────────────────────────────────────────

    def save(self, path: str) -> None:
        """
        Save recommender state to a joblib file.

        Args:
            path: File path to save.
        """
        joblib.dump(
            {
                "vectorizer": self.vectorizer,
                "opportunity_matrix": self.opportunity_matrix,
                "is_fitted": self.is_fitted,
            },
            path,
        )
        logger.info(f"OpportunityRecommender saved to {path}")

    def load(self, path: str) -> None:
        """
        Load recommender state from a joblib file.

        Args:
            path: File path to load from.
        """
        state = joblib.load(path)
        self.vectorizer = state["vectorizer"]
        self.opportunity_matrix = state["opportunity_matrix"]
        self.is_fitted = state["is_fitted"]
        logger.info(f"OpportunityRecommender loaded from {path}")
