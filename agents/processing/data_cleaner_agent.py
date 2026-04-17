import asyncio
import re
from datetime import date
import dateparser
from bs4 import BeautifulSoup

from agents.base_agent import BaseAgent

class AgentDataCleaner(BaseAgent):
    name = "AgentDataCleaner"

    async def run(self) -> dict:
        start = self._timestamp()
        raw = self.model.shared_data.get("raw_opportunities", [])
        cleaned = []
        errors = []
        skipped = 0
        
        for opp in raw:
            try:
                result = self.clean_opportunity(opp)
                if result is None:
                    skipped += 1
                    continue
                cleaned.append(result)
            except Exception as e:
                errors.append(str(e))
                skipped += 1
                
        self.model.shared_data["cleaned_opportunities"] = cleaned
        return self._make_report(
            success=True,
            items=len(cleaned),
            errors=errors,
            duration=self._duration(start),
            skipped=skipped
        )

    def clean_text(self, text: str | None) -> str | None:
        if not text:
            return None
        text_without_html = BeautifulSoup(text, "html.parser").get_text(separator=" ", strip=True)
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text_without_html)
        cleaned = ' '.join(cleaned.split())
        return cleaned if cleaned else None

    def normalize_date(self, raw_date: str | None) -> str | None:
        if not raw_date:
            return None
        parsed = dateparser.parse(raw_date, settings={
            "RETURN_AS_TIMEZONE_AWARE": False,
            "PREFER_FUTURE_DATES": True
        })
        if parsed:
            return parsed.date().isoformat()
        return None

    def normalize_location(self, loc: str | None) -> str | None:
        if not loc:
            return None
        loc_clean = loc.strip().title()
        return loc_clean if loc_clean else None

    def validate_url(self, url: str) -> bool:
        if not url:
            return False
        if not (url.startswith("http://") or url.startswith("https://")):
            return False
        if "." not in url.split("://")[1]:
            return False
        return True

    def clean_opportunity(self, opp: dict) -> dict | None:
        opp["description"] = self.clean_text(opp.get("description"))
        opp["deadline"] = self.normalize_date(opp.get("deadline"))
        opp["location"] = self.normalize_location(opp.get("location"))
        
        url = opp.get("url", "")
        if not self.validate_url(url):
            self.logger.warning(f"Invalid url '{url}' for opportunity '{opp.get('title')}'")
            return None
            
        opp["title"] = self.clean_text(opp.get("title"))
        if not opp.get("title"):
            return None
            
        return opp

    def clean(self) -> None:
        """Runs the clean stage via sync bridge."""
        asyncio.run(self.run_safe())
