import asyncio
import mesa
from agents.base_agent import BaseAgent

# ML module implemented in Prompt 6 — must exist before running
from ml.inference.clustering import OpportunityClusterer

class AgentCluster(BaseAgent):
    name = "AgentCluster"

    def __init__(self, unique_id: int, model: mesa.Model):
        super().__init__(unique_id, model)
        self.clusterer = OpportunityClusterer(n_clusters=5)

    async def run(self) -> dict:
        start = self._timestamp()
        opps = self.model.shared_data.get("classified_opportunities", [])
        
        if len(opps) < 5:
            self.logger.warning(
                f"Too few opportunities ({len(opps)}) to cluster. "
                "Skipping. cluster_id and cluster_label will be None."
            )
            self.model.shared_data["clustered_opportunities"] = opps
            return self._make_report(
                True, 0, ["Too few items to cluster"], self._duration(start)
            )

        texts = [
            (o.get("title") or "") + " " + (o.get("description") or "")
            for o in opps
        ]
        
        self.clusterer.fit(texts)
        cluster_ids = self.clusterer.predict_batch(texts)
        clustered = []
        
        for opp, cid in zip(opps, cluster_ids):
            enriched = dict(opp)
            enriched["cluster_id"] = int(cid)
            enriched["cluster_label"] = self.clusterer.get_cluster_label(cid)
            clustered.append(enriched)
            
        self.model.shared_data["clustered_opportunities"] = clustered
        
        return self._make_report(
            success=True,
            items=len(clustered),
            errors=[],
            duration=self._duration(start),
            cluster_labels=self.clusterer.get_all_labels()
        )

    def cluster(self) -> None:
        """Synchronous bridge for step activation."""
        asyncio.run(self.run_safe())
