from agents.scrapers.base_scraper import BaseScraper
import uuid
import random
from datetime import datetime, timedelta

class AgentProjectScraper(BaseScraper):
    name = "AgentProjectScraper"

    async def fetch_live(self) -> list[dict]:
        """Structured as if calling Horizon Europe open data API."""
        resp = self._safe_get("https://example.com/api/projects")
        if not resp:
            self.logger.warning("Failed to fetch live projects, returning empty list.")
            return []
        html = self._parse_html(resp.text)
        if not html:
            return []
        return []

    async def fetch_mock(self) -> list[dict]:
        """Return exactly 10 mock research project dicts."""
        institutions = ["INRIA", "Max Planck Institute", "ETH Zurich", 
                        "EPFL", "KU Leuven", "Politecnico di Milano", 
                        "University of Amsterdam"]
        domains = ["AI safety", "computer vision", "NLP", 
                   "federated learning", "reinforcement learning", 
                   "medical AI", "climate AI"]
        
        mocks = []
        now = datetime.now()
        deadlines = (
            [now + timedelta(days=random.randint(5, 10)) for _ in range(2)] +
            [now + timedelta(days=random.randint(30, 90)) for _ in range(5)] +
            [now + timedelta(days=random.randint(120, 180)) for _ in range(2)] +
            [now - timedelta(days=random.randint(1, 10)) for _ in range(1)]
        )
        random.shuffle(deadlines)

        for i in range(10):
            inst = random.choice(institutions)
            dom = random.choice(domains)
            dl = deadlines[i].strftime("%b %d %Y")
            funding = random.randint(1, 5)
            
            mocks.append({
                "title": f"Horizon Project: {dom.title()}",
                "description": f"Research project led by {inst} in the field of {dom}. Funding amount: {funding}M EUR.",
                "skills_required": [],
                "location": "Europe",
                "eligibility": "PhD or Postdoc",
                "deadline": dl,
                "source": "Horizon Europe",
                "url": f"https://mock.projects.eu/id/{uuid.uuid4()}"
            })
        return mocks

    def normalize(self, raw: dict) -> dict:
        return {
            "title": raw.get("title", ""),
            "type": "project",
            "category": "Other",
            "description": raw.get("description", ""),
            "skills_required": raw.get("skills_required", []),
            "location": raw.get("location"),
            "eligibility": raw.get("eligibility"),
            "deadline": raw.get("deadline"),
            "source": raw.get("source", "Unknown"),
            "url": raw.get("url", "")
        }
