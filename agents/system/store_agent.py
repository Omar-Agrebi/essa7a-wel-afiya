import asyncio
from agents.base_agent import BaseAgent

class AgentStore(BaseAgent):
    name = "AgentStore"

    async def run(self) -> dict:
        start = self._timestamp()
        opps = self.model.shared_data.get("clustered_opportunities", [])
        
        if not opps:
            return self._make_report(True, 0, [], self._duration(start))
            
        opp_service = self.model.services["opportunity"]
        try:
            result = await opp_service.bulk_upsert_opportunities(opps)
        except Exception as e:
            self.logger.error(f"Error during bulk upsert: {e}")
            return self._make_report(False, 0, [str(e)], self._duration(start))
            
        inserted = result.get("inserted", 0)
        updated = result.get("updated", 0)
        
        return self._make_report(
            success=True,
            items=inserted + updated,
            errors=result.get("errors", []),
            duration=self._duration(start),
            inserted=inserted,
            updated=updated
        )

    def store(self) -> None:
        """Synchronous bridge for step activation."""
        asyncio.run(self.run_safe())
