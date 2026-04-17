import asyncio
from agents.base_agent import BaseAgent
import mesa

# ML module implemented in Prompt 6 — must exist before running pipeline
from ml.inference.classifier import OpportunityClassifier

class AgentClassifier(BaseAgent):
    name = "AgentClassifier"

    def __init__(self, unique_id: int, model: mesa.Model):
        super().__init__(unique_id, model)
        self.classifier = OpportunityClassifier()
        self.classifier.train()
        self.logger.info("OpportunityClassifier trained and ready")

    async def run(self) -> dict:
        start = self._timestamp()
        opps = self.model.shared_data.get("cleaned_opportunities", [])
        
        if not opps:
            return self._make_report(True, 0, [], self._duration(start))
            
        texts = [
            (o.get("title") or "") + " " + (o.get("description") or "")
            for o in opps
        ]
        
        predictions = self.classifier.predict_batch(texts)
        classified = []
        
        for opp, pred in zip(opps, predictions):
            enriched = dict(opp)
            if not enriched.get("type"):
                enriched["type"] = pred["type"]
            if not enriched.get("category"):
                enriched["category"] = pred["category"]
            classified.append(enriched)
            
        self.model.shared_data["classified_opportunities"] = classified
        return self._make_report(
            success=True,
            items=len(classified),
            errors=[],
            duration=self._duration(start)
        )

    def classify(self) -> None:
        """Synchronous bridge for step activation."""
        asyncio.run(self.run_safe())
