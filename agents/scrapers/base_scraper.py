import asyncio
import requests
from bs4 import BeautifulSoup
import mesa
from agents.base_agent import BaseAgent

class BaseScraper(BaseAgent):
    """
    Base class for all scraper agents.
    Provides mock/live mode reading, basic HTTP client, and unified run loop.
    """
    def __init__(self, unique_id: int, model: mesa.Model):
        super().__init__(unique_id, model)
        self.mode: str = getattr(self.model.settings, "SCRAPER_MODE", "mock")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; Observatory/1.0)"
        })

    async def fetch_live(self) -> list[dict]:
        """
        Makes real HTTP requests to live source.
        Returns list of raw source-format dicts.
        Returns [] on any failure.
        """
        raise NotImplementedError

    async def fetch_mock(self) -> list[dict]:
        """
        Returns hardcoded realistic mock data.
        Same dict structure as fetch_live output.
        """
        raise NotImplementedError

    def normalize(self, raw: dict) -> dict:
        """
        Maps source-specific field names to unified schema.
        """
        raise NotImplementedError

    async def run(self) -> dict:
        start = self._timestamp()
        
        if self.mode == "live":
            raw = await self.fetch_live()
        else:
            raw = await self.fetch_mock()
            
        normalized = []
        errors = []
        for item in raw:
            try:
                normalized.append(self.normalize(item))
            except Exception as e:
                errors.append(str(e))
                
        return self._make_report(
            success=True,
            items=len(normalized),
            errors=errors,
            duration=self._duration(start),
            data=normalized
        )

    def _safe_get(self, url: str, params: dict | None = None, timeout: int = 10) -> requests.Response | None:
        """Wraps requests.get with timeout and error handling."""
        try:
            resp = self.session.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp
        except Exception as e:
            self.logger.warning(f"Failed to fetch {url}: {str(e)}")
            return None

    def _parse_html(self, html: str) -> BeautifulSoup:
        """Returns parsed BeautifulSoup object."""
        return BeautifulSoup(html, "html.parser")

    def scrape(self) -> None:
        """Scrapers run via asyncio.gather, not via scheduler."""
        pass
