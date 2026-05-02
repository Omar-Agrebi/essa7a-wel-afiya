import asyncio
from datetime import date
import dateparser
import mesa
from agents.base_agent import BaseAgent

class AgentAdvisor(BaseAgent):
    name = "AgentAdvisor"

    def __init__(self, unique_id: int, model: mesa.Model):
        super().__init__(unique_id, model)
        self.matcher = None  # Injected after instantiation
        self.w1 = getattr(self.model.settings, "RECOMMENDATION_W1", 0.5)
        self.w2 = getattr(self.model.settings, "RECOMMENDATION_W2", 0.3)
        self.w3 = getattr(self.model.settings, "RECOMMENDATION_W3", 0.2)

    async def run(self) -> dict:
        start = self._timestamp()
        users = self.model.shared_data.get("users", [])
        opps = self.model.shared_data.get("clustered_opportunities", [])

        if not users or not opps:
            self.model.shared_data["recommendations"] = []
            return self._make_report(True, 0, [], self._duration(start))

        all_recommendations = []
        rec_service = self.model.services.get("recommendation")
        errors = []

        if not self.matcher:
            errors.append("AgentRelevanceMatcher not injected into AgentAdvisor.")
            return self._make_report(False, 0, errors, self._duration(start))

        for user in users:
            try:
                scored = await self.matcher.score_opportunities(user, opps)
                recommendations = []
                
                for opp in scored:
                    level_match = self.compute_level_match(
                        user.get("level", ""),
                        opp.get("eligibility")
                    )
                    recency = self.compute_recency_score(
                        opp.get("deadline")
                    )
                    sim = opp.get("similarity_score", 0.0)
                    
                    final_score = (self.w1 * sim + 
                                   self.w2 * level_match + 
                                   self.w3 * recency)
                                   
                    reasons = self.generate_match_reasons(
                        user, opp, sim, level_match, recency
                    )
                    
                    recommendations.append({
                        "user_id": user.get("user_id"),
                        "opportunity_id": opp.get("id"),
                        "opportunity": opp,
                        "final_score": final_score,
                        "match_reasons": reasons
                    })
                
                recommendations.sort(key=lambda x: x["final_score"], reverse=True)
                top_n = recommendations[:10]
                all_recommendations.extend(top_n)
                
                if rec_service:
                    await rec_service.refresh_recommendations(
                        user_id=user["user_id"],
                        scored_opps=top_n
                    )
            except Exception as e:
                errors.append(f"User {user.get('user_id')}: {str(e)}")

        self.model.shared_data["recommendations"] = all_recommendations
        
        return self._make_report(
            success=True,
            items=len(all_recommendations),
            errors=errors,
            duration=self._duration(start)
        )

    def compute_level_match(self, user_level: str, eligibility: str | None) -> float:
        if eligibility is None:
            return 0.5
            
        user_level_lower = user_level.lower()
        eligibility_lower = eligibility.lower()
        
        if user_level_lower in eligibility_lower:
            return 1.0
            
        adjacent_pairs = {
            ("bachelor", "master"): 0.4,
            ("master", "bachelor"): 0.3,
            ("master", "phd"): 0.5,
            ("phd", "master"): 0.4,
            ("phd", "postdoc"): 0.5,
            ("postdoc", "phd"): 0.4,
        }
        
        for (lvl1, lvl2), score in adjacent_pairs.items():
            if user_level_lower == lvl1 and lvl2 in eligibility_lower:
                return score
                
        return 0.0

    def compute_recency_score(self, deadline: str | None) -> float:
        if deadline is None:
            return 0.3
            
        parsed_date = dateparser.parse(deadline)
        if not parsed_date:
            return 0.3
            
        days_left = (parsed_date.date() - date.today()).days
        if days_left > 30:
            return 1.0
        elif 10 < days_left <= 30:
            return 0.5
        elif 0 <= days_left <= 10:
            return 0.2
            
        return 0.0

    def generate_match_reasons(self, user: dict, opp: dict, similarity: float, level_match: float, recency: float) -> list[str]:
        reasons = []
        user_skills = {s.lower() for s in user.get("skills", [])}
        opp_skills = {s.lower() for s in opp.get("skills_required", [])}
        overlap = user_skills & opp_skills
        
        if overlap:
            top = list(overlap)[:3]
            reasons.append(f"{len(overlap)} skill(s) match: {', '.join(top)}")
            
        if level_match == 1.0:
            reasons.append(f"{user.get('level', '').title()} level compatible")
            
        if similarity > 0.3:
            reasons.append(f"Strong relevance ({similarity:.0%} match)")
            
        if 0.0 < recency <= 0.2:
            deadline_date = dateparser.parse(opp.get("deadline", ""))
            if deadline_date:
                days = (deadline_date.date() - date.today()).days
                reasons.append(f"Deadline in {days} days — apply soon")
                
        user_interests = [i.lower() for i in user.get("interests", [])]
        opp_category = opp.get("category", "").lower()
        if any(opp_category in interest for interest in user_interests):
            reasons.append(f"Matches your interest in {opp.get('category')}")
            
        if not reasons:
            reasons.append("Recommended based on your profile")
            
        return reasons

    def recommend(self) -> None:
        """Synchronous bridge for step activation."""
        asyncio.run(self.run_safe())
