import sys
import os
import asyncio
import time
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, AsyncMock

# --- Path Setup ---
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Mocking Utilities ---
class MockSettings:
    SCRAPER_MODE = "mock"
    ENVIRONMENT = "development"

import mesa

class MockModel(mesa.Model):
    def __init__(self):
        super().__init__()
        self.settings = MockSettings()
        self.shared_data = {}
        self.services = {
            "opportunity": AsyncMock(),
            "user": AsyncMock(),
            "notification": AsyncMock()
        }
        self.logger = MagicMock()

    def collect_agent_report(self, report):
        pass

# --- Test Runner ---
results = []

def test_case(name):
    def decorator(fn):
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                print(f"Running: {name}...", end="", flush=True)
                await fn(*args, **kwargs)
                duration = time.time() - start
                print(f" [PASS] ({duration:.3f}s)")
                results.append({"name": name, "status": "PASS", "duration": duration})
            except Exception as e:
                import traceback
                traceback.print_exc()
                duration = time.time() - start
                print(f" [FAIL] ({duration:.3f}s)")
                print(f"    Error: {str(e)}")
                results.append({"name": name, "status": "FAIL", "duration": duration, "error": str(e)})
        return wrapper
    return decorator

# --- Agent Imports ---
from agents.scrapers.internship_scraper import AgentInternshipScraper
from agents.scrapers.scholarship_scraper import AgentScholarshipScraper
from agents.scrapers.project_scraper import AgentProjectScraper
from agents.scrapers.certification_scraper import AgentCertificationScraper
from agents.processing.data_cleaner_agent import AgentDataCleaner
from agents.processing.classifier_agent import AgentClassifier
from agents.processing.cluster_agent import AgentCluster
from agents.recommendation.relevance_matcher_agent import AgentRelevanceMatcher
from agents.recommendation.advisor_agent import AgentAdvisor
from agents.system.store_agent import AgentStore
from agents.system.notification_agent import AgentNotification

# --- Individual Tests ---

@test_case("Internship Scraper")
async def test_internship_scraper():
    model = MockModel()
    agent = AgentInternshipScraper(1, model)
    report = await agent.run()
    assert report["success"] is True
    assert report["items_processed"] > 0
    assert "data" in report

@test_case("Scholarship Scraper")
async def test_scholarship_scraper():
    model = MockModel()
    agent = AgentScholarshipScraper(2, model)
    report = await agent.run()
    assert report["success"] is True
    assert report["items_processed"] > 0

@test_case("Project Scraper")
async def test_project_scraper():
    model = MockModel()
    agent = AgentProjectScraper(3, model)
    report = await agent.run()
    assert report["success"] is True
    assert report["items_processed"] > 0

@test_case("Certification Scraper")
async def test_certification_scraper():
    model = MockModel()
    agent = AgentCertificationScraper(4, model)
    report = await agent.run()
    assert report["success"] is True
    assert report["items_processed"] > 0

@test_case("Data Cleaner Agent")
async def test_data_cleaner():
    model = MockModel()
    model.shared_data["raw_opportunities"] = [
        {"title": "Test Opp", "description": "Desc", "url": "https://example.com", "deadline": "Jan 01 2025", "location": "paris"}
    ]
    agent = AgentDataCleaner(5, model)
    report = await agent.run()
    assert report["success"] is True
    assert len(model.shared_data["cleaned_opportunities"]) == 1
    assert model.shared_data["cleaned_opportunities"][0]["location"] == "Paris"

@test_case("Classifier Agent")
async def test_classifier():
    model = MockModel()
    model.shared_data["cleaned_opportunities"] = [
        {"title": "AI Internship", "description": "Deep learning project", "type": "internship"}
    ]
    agent = AgentClassifier(6, model)
    report = await agent.run()
    assert report["success"] is True
    assert len(model.shared_data["classified_opportunities"]) == 1

@test_case("Cluster Agent")
async def test_cluster():
    model = MockModel()
    # Need at least a few items for clustering to work or skip gracefully
    model.shared_data["classified_opportunities"] = [
        {"title": f"Opp {i}", "description": "Some description text for clustering"} for i in range(10)
    ]
    agent = AgentCluster(7, model)
    report = await agent.run()
    assert report["success"] is True

@test_case("Relevance Matcher Agent")
async def test_relevance_matcher():
    model = MockModel()
    agent = AgentRelevanceMatcher(8, model)
    user = {"skills": ["Python"], "interests": ["AI"], "level": "Master"}
    opps = [{"title": "AI Dev", "description": "Python role", "skills_required": ["Python"], "eligibility": "Master"}]
    results = await agent.score_opportunities(user, opps)
    assert len(results) == 1
    assert results[0]["similarity_score"] >= 0

@test_case("Advisor Agent")
async def test_advisor():
    model = MockModel()
    model.shared_data["clustered_opportunities"] = [
        {"id": "opp1", "title": "AI Role", "description": "Python", "type": "internship", "category": "AI", "skills_required": ["Python"]}
    ]
    model.shared_data["users"] = [
        {"user_id": "u1", "skills": ["Python"], "interests": ["AI"], "level": "Master"}
    ]
    agent = AgentAdvisor(9, model)
    agent.matcher = AgentRelevanceMatcher(99, model)
    report = await agent.run()
    assert report["success"] is True
    assert len(model.shared_data["recommendations"]) > 0

@test_case("Store Agent")
async def test_store_agent():
    model = MockModel()
    model.shared_data["clustered_opportunities"] = [{"title": "Saved Opp"}]
    model.services["opportunity"].bulk_upsert_opportunities.return_value = {"inserted": 1, "updated": 0, "errors": []}
    agent = AgentStore(10, model)
    report = await agent.run()
    assert report["success"] is True
    assert report["items_processed"] == 1

@test_case("Notification Agent")
async def test_notification_agent():
    model = MockModel()
    
    # Mocking data objects
    mock_opp = MagicMock()
    mock_opp.id = "opp1"
    mock_opp.title = "Expiring Opp"
    mock_opp.category = "AI"
    mock_opp.deadline = date.today() + timedelta(days=2)
    
    mock_user = MagicMock()
    mock_user.user_id = "u1"
    mock_user.interests = ["AI"]
    
    model.services["opportunity"].get_expiring_soon.return_value = [mock_opp]
    model.services["user"].get_all_users.return_value = [mock_user]
    
    agent = AgentNotification(11, model)
    report = await agent.run()
    assert report["success"] is True
    assert report["notifications_created"] == 1

# --- Main Execution ---
async def main():
    print("\n" + "="*50)
    print("      INTELLIGENT OBSERVATORY: AGENT UNIT TESTS")
    print("="*50 + "\n")
    
    await test_internship_scraper()
    await test_scholarship_scraper()
    await test_project_scraper()
    await test_certification_scraper()
    await test_data_cleaner()
    await test_classifier()
    await test_cluster()
    await test_relevance_matcher()
    await test_advisor()
    await test_store_agent()
    await test_notification_agent()
    
    print("\n" + "="*50)
    print("                  SUMMARY")
    print("="*50)
    passed_list = [r for r in results if r["status"] == "PASS"]
    failed_list = [r for r in results if r["status"] == "FAIL"]
    print(f"Total: {len(results)} | Passed: {len(passed_list)} | Failed: {len(failed_list)}")
    if failed_list:
        print("\nFailed Tests:")
        for f in failed_list:
            print(f" - {f['name']}")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
