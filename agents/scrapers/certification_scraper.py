from agents.scrapers.base_scraper import BaseScraper
import uuid
import random

class AgentCertificationScraper(BaseScraper):
    name = "AgentCertificationScraper"

    async def fetch_live(self) -> list[dict]:
        """
        Live implementation consuming Coursera public API.
        Falls back to mock if API unreachable or returns error.
        """
        url = "https://api.coursera.org/api/courses.v1"
        params = {
            "fields": "name,description,slug,domainTypes,primaryLanguages",
            "limit": 100
        }
        resp = self._safe_get(url, params=params)
        
        if not resp or resp.status_code != 200:
            self.logger.warning("Coursera API failed or unreachable. Falling back to mock data.")
            return await self.fetch_mock()

        try:
            data = resp.json()
            elements = data.get("elements", [])
            kept = []
            
            for course in elements:
                langs = course.get("primaryLanguages", [])
                domains = course.get("domainTypes", [])
                
                # Filter: keep where "en" in primaryLanguages
                if "en" not in langs:
                    continue
                    
                # Filter: keep where domain matches data-science or computer-science
                valid_domains = [d for d in domains if d.get("domainId") in ["data-science", "computer-science"]]
                if not valid_domains:
                    continue
                    
                kept.append(course)

            if not kept:
                self.logger.warning("Coursera API returned 0 matching courses. Falling back to mock data.")
                return await self.fetch_mock()
                
            return kept
            
        except Exception as e:
            self.logger.warning(f"Error parsing Coursera API response: {str(e)}. Falling back to mock data.")
            return await self.fetch_mock()

    async def fetch_mock(self) -> list[dict]:
        """Returns exactly 15 mock certification dicts."""
        providers = ["Coursera", "edX", "DeepLearning.AI", "fast.ai", "Udacity"]
        titles = [
            "Deep Learning Specialization", 
            "Machine Learning with Python", 
            "NLP with Transformers",
            "AI for Everyone",
            "Data Science Professional Certificate"
        ]
        levels = ["Beginner", "Intermediate", "Advanced"]
        
        mocks = []
        for i in range(15):
            prov = random.choice(providers)
            t = random.choice(titles)
            lvl = random.choice(levels)
            dur = random.randint(2, 6)
            
            mocks.append({
                "name": f"{t} ({prov})",
                "description": f"Comprehensive {lvl.lower()} course covering practical aspects of the field. Duration estimate: {dur} months.",
                "slug": f"mock-course-cert-{i}",
                "domainTypes": [{"domainId": random.choice(["data-science", "computer-science"])}],
                "level_mock": lvl
            })
        return mocks

    def normalize(self, raw: dict) -> dict:
        skills_pool = ["python", "pytorch", "tensorflow", "scikit-learn", "sql", "r", 
                       "nlp", "computer vision", "reinforcement learning", "mlops", 
                       "docker", "kubernetes", "julia", "spark", "hugging face"]
        
        desc = raw.get("description", "")
        if desc:
            desc = desc[:1000]
            
        slug = raw.get("slug", "")
        url = f"https://www.coursera.org/learn/{slug}" if slug else f"https://www.coursera.org/learn/cert-{hash(raw.get('name', ''))}"
        
        domains = raw.get("domainTypes", [])
        domain_ids = [d.get("domainId") for d in domains if isinstance(d, dict)]
        
        category = "Other"
        if "data-science" in domain_ids:
            category = "Data Science"
        elif "computer-science" in domain_ids:
            category = "AI"

        desc_lower = desc.lower()
        extracted_skills = [s for s in skills_pool if s in desc_lower]

        return {
            "title": raw.get("name", ""),
            "type": "course",
            "category": category,
            "description": desc,
            "skills_required": extracted_skills,
            "location": "Online",
            "eligibility": raw.get("level_mock", "Open"),
            "deadline": None,
            "source": "Coursera",
            "url": url
        }
