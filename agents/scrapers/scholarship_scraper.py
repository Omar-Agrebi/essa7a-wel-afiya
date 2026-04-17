from agents.scrapers.base_scraper import BaseScraper
import uuid
import random
from datetime import datetime, timedelta

class AgentScholarshipScraper(BaseScraper):
    name = "AgentScholarshipScraper"

    async def fetch_live(self) -> list[dict]:
        """Structured as if calling DAAD or Erasmus+ API."""
        resp = self._safe_get("https://example.com/api/scholarships")
        if not resp:
            self.logger.warning("Failed to fetch live scholarships, returning empty list.")
            return []
        html = self._parse_html(resp.text)
        if not html:
            return []
        return []

    async def fetch_mock(self) -> list[dict]:
        """Return exactly 15 mock scholarship dicts."""
        bodies = ["DAAD", "Erasmus+", "Campus France", "Eiffel Scholarship", 
                  "Marie Curie Fellowship", "Horizon Europe"]
        locations = ["Germany", "France", "Belgium", "Netherlands", "Remote"]
        levels = ["Bachelor", "Master", "PhD"]
        
        mocks = []
        now = datetime.now()
        deadlines = (
            [now + timedelta(days=random.randint(5, 10)) for _ in range(4)] +
            [now + timedelta(days=random.randint(30, 90)) for _ in range(7)] +
            [now + timedelta(days=random.randint(120, 180)) for _ in range(2)] +
            [now - timedelta(days=random.randint(1, 10)) for _ in range(2)]
        )
        random.shuffle(deadlines)

        for i in range(15):
            body = random.choice(bodies)
            loc = random.choice(locations)
            lvl = random.choice(levels)
            dl = deadlines[i].strftime("%b %d %Y")
            stipend = random.randint(800, 2500)
            
            mocks.append({
                "title": f"Excellence Scholarship ({lvl})",
                "description": f"Funding for {lvl} students in AI. Includes {stipend} EUR monthly stipend, travel allowance, and tuition coverage.",
                "skills_required": [],
                "location": loc,
                "eligibility": lvl,
                "deadline": dl,
                "source": body,
                "url": f"https://mock.scholarships.org/fund/{uuid.uuid4()}"
            })
        return mocks

    def normalize(self, raw: dict) -> dict:
        return {
            "title": raw.get("title", ""),
            "type": "scholarship",
            "category": "Other",
            "description": raw.get("description", ""),
            "skills_required": raw.get("skills_required", []),
            "location": raw.get("location"),
            "eligibility": raw.get("eligibility"),
            "deadline": raw.get("deadline"),
            "source": raw.get("source", "Unknown"),
            "url": raw.get("url", "")
        }
