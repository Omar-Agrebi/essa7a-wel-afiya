from agents.scrapers.base_scraper import BaseScraper
import uuid
import random
from datetime import datetime, timedelta

class AgentInternshipScraper(BaseScraper):
    name = "AgentInternshipScraper"

    async def fetch_live(self) -> list[dict]:
        """Structured as if calling LinkedIn/Indeed job search."""
        resp = self._safe_get("https://example.com/linkedin-jobs")
        if not resp:
            self.logger.warning("Failed to fetch live internships, returning empty list.")
            return []
        html = self._parse_html(resp.text)
        if not html:
            return []
        return []

    async def fetch_mock(self) -> list[dict]:
        """Returns exactly 20 mock internship dicts."""
        companies = ["Airbus", "CERN", "Thales", "DeepMind", "INRIA", 
                     "Siemens", "Capgemini", "ESA", "TotalEnergies", "Dassault Systèmes"]
        locations = ["Paris", "Berlin", "London", "Remote", "Brussels", "Zurich", "Amsterdam"]
        skills_pool = ["Python", "PyTorch", "scikit-learn", "SQL", "NLP", 
                       "computer vision", "MLOps", "Docker", "Hugging Face", "Spark"]
        
        mocks = []
        now = datetime.now()
        deadlines = (
            [now + timedelta(days=random.randint(5, 10)) for _ in range(5)] +
            [now + timedelta(days=random.randint(30, 90)) for _ in range(10)] +
            [now + timedelta(days=random.randint(120, 180)) for _ in range(3)] +
            [now - timedelta(days=random.randint(1, 10)) for _ in range(2)]
        )
        random.shuffle(deadlines)

        for i in range(20):
            comp = random.choice(companies)
            loc = random.choice(locations)
            skills = random.sample(skills_pool, k=random.randint(3, 5))
            dl = deadlines[i].strftime("%b %d %Y")
            
            mocks.append({
                "title": f"AI/Data Internship ({', '.join(skills[:2])})",
                "description": f"We are looking for an intern passionate about Data Science and AI. Must know {', '.join(skills)}. Join {comp} to build amazing things.",
                "skills_required": skills,
                "location": loc,
                "eligibility": "Bachelor or Master",
                "deadline": dl,
                "source": "LinkedIn Mock",
                "url": f"https://mock.linkedin.com/jobs/{uuid.uuid4()}"
            })
        return mocks

    def normalize(self, raw: dict) -> dict:
        desc = raw.get("description", "").lower()
        
        category = "Other"
        if any(kw in desc for kw in ["neural", "deep learning", "ml", "artificial intelligence"]):
            category = "AI"
        elif any(kw in desc for kw in ["pandas", "statistics", "data analysis"]):
            category = "Data Science"
        elif any(kw in desc for kw in ["security", "cryptography", "penetration"]):
            category = "Cybersecurity"

        return {
            "title": raw.get("title", ""),
            "type": "internship",
            "category": category,
            "description": raw.get("description", ""),
            "skills_required": raw.get("skills_required", []),
            "location": raw.get("location"),
            "eligibility": raw.get("eligibility"),
            "deadline": raw.get("deadline"),
            "source": raw.get("source", "Unknown"),
            "url": raw.get("url", "")
        }
