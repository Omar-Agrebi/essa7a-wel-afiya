import mesa
from agents.base_agent import BaseAgent

# ML module implemented in Prompt 6 — must exist before running
from ml.inference.recommender import OpportunityRecommender

class AgentRelevanceMatcher(BaseAgent):
    name = "AgentRelevanceMatcher"

    def __init__(self, unique_id: int, model: mesa.Model):
        super().__init__(unique_id, model)
        self.recommender = OpportunityRecommender()

    def build_user_text(self, user: dict) -> str:
        """Joins user's skills and interests into a single string for TF-IDF."""
        skills = user.get("skills", [])
        interests = user.get("interests", [])
        return " ".join(skills + interests)

    async def score_opportunities(self, user: dict, opportunities: list[dict]) -> list[dict]:
        """
        Calculates similarity score for each opportunity against the user profile.
        Orders by similarity score descending.
        """
        if not opportunities:
            return []
            
        self.recommender.fit(opportunities)
        scores = self.recommender.compute_similarity_scores(user, opportunities)
        
        result = []
        for opp, score in zip(opportunities, scores):
            enriched = dict(opp)
            enriched["similarity_score"] = float(score)
            result.append(enriched)
            
        return sorted(result, key=lambda x: x["similarity_score"], reverse=True)

    async def run(self) -> dict:
        raise NotImplementedError("AgentRelevanceMatcher is a utility agent. Call score_opportunities() directly.")
