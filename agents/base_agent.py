import time
import asyncio
import traceback
import mesa
from app.core.logging import get_logger

class BaseAgent(mesa.Agent):
    """
    Base class for all agents in the Observatory system.
    Extends mesa.Agent with standardized reporting and pipeline stage execution.
    """
    name: str = "BaseAgent"

    def __init__(self, unique_id: int, model: mesa.Model):
        """
        Initialize the agent.
        
        Args:
            unique_id (int): A unique identifier for the agent.
            model (mesa.Model): The model the agent is attached to.
        """
        super().__init__(unique_id, model)
        self.logger = get_logger(self.name)
        self._last_report: dict = {}

    async def run(self) -> dict:
        """
        Core asynchronous execution method. Subclasses must override this.
        
        Raises:
            NotImplementedError: If not overridden by the subclass.
        """
        raise NotImplementedError("Subclasses must implement run()")

    def step(self) -> None:
        """
        Synchronous MESA bridge.
        Usually called by the MESA scheduler. Pipeline stages define specific methods
        which call `run_safe` instead. So this is kept generic.
        """
        # We assume the scheduler might call step() natively. If it does, we bridge it.
        result = asyncio.run(self.run_safe())
        self._last_report = result
        if hasattr(self.model, "collect_agent_report"):
            self.model.collect_agent_report(self._last_report)

    async def run_safe(self) -> dict:
        """
        Wraps run() in try/except block. Logs full traceback on exception
        and returns an error-shaped dict on failure. Never raises.
        
        Returns:
            dict: The execution report or error dictionary.
        """
        start = self._timestamp()
        try:
            result = await self.run()
            self._last_report = result
            return result
        except Exception as e:
            err_msg = str(e)
            self.logger.error(f"Agent execution failed: {err_msg}")
            self.logger.debug(traceback.format_exc())
            result = self._make_report(
                success=False,
                items=0,
                errors=[err_msg],
                duration=self._duration(start)
            )
            self._last_report = result
            return result

    def get_last_report(self) -> dict:
        """
        Returns the last report dict.
        
        Returns:
            dict: The last execution report.
        """
        return self._last_report

    def _timestamp(self) -> float:
        """
        Returns current timestamp.
        """
        return time.time()

    def _duration(self, start: float) -> float:
        """
        Returns the duration since the given start time.
        
        Args:
            start (float): The start timestamp.
            
        Returns:
            float: Duration in seconds.
        """
        return time.time() - start

    def _make_report(self, success: bool, items: int, errors: list[str], duration: float, **extra) -> dict:
        """
        Constructs a standard report dict.
        
        Args:
            success (bool): Whether the execution was successful.
            items (int): Number of items processed.
            errors (list[str]): List of error messages.
            duration (float): Execution duration in seconds.
            **extra: Any extra info to include in the report.
            
        Returns:
            dict: Standardized report dictionary.
        """
        return {
            "success": success,
            "agent": self.name,
            "items_processed": items,
            "errors": errors,
            "duration_sec": duration,
            **extra
        }

    # Pipeline stage methods
    def scrape(self) -> None:
        """Execute the scrape phase."""
        pass

    def clean(self) -> None:
        """Execute the clean phase."""
        pass

    def classify(self) -> None:
        """Execute the classify phase."""
        pass

    def cluster(self) -> None:
        """Execute the cluster phase."""
        pass

    def store(self) -> None:
        """Execute the store phase."""
        pass

    def recommend(self) -> None:
        """Execute the recommend phase."""
        pass

    def notify(self) -> None:
        """Execute the notify phase."""
        pass
