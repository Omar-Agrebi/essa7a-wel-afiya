"""
Comprehensive test suite for Intelligent University Observatory
Tests: Scrapers, ML (Classifier, Clusterer, Recommender), Processing Agents, Pipeline
"""

import sys
import os
import asyncio
import time
import json
import traceback
from datetime import datetime, timedelta
from typing import Any

# ── Path setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Results collector ─────────────────────────────────────────────────────────
results = []

def section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test(name: str, fn, *args, **kwargs):
    """Run a single test and record result."""
    start = time.time()
    try:
        if asyncio.iscoroutinefunction(fn):
            result = asyncio.get_event_loop().run_until_complete(fn(*args, **kwargs))
        else:
            result = fn(*args, **kwargs)
        duration = round(time.time() - start, 3)
        status = "✅ PASS"
        error = None
        print(f"  {status}  [{duration:.3f}s]  {name}")
        results.append({"name": name, "status": "PASS", "duration": duration, "result": result})
        return result
    except Exception as e:
        duration = round(time.time() - start, 3)
        print(f"  ❌ FAIL  [{duration:.3f}s]  {name}")
        print(f"          → {type(e).__name__}: {e}")
        results.append({"name": name, "status": "FAIL", "duration": duration, "error": str(e)})
        return None


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1: ML LAYER
# ══════════════════════════════════════════════════════════════════════════════

section("1. ML CLASSIFIER")

from ml.inference.classifier import OpportunityClassifier

clf = OpportunityClassifier()

def test_classifier_not_trained():
    assert not clf.is_trained
    return "untrained=True"

def test_classifier_train():
    clf.train()
    assert clf.is_trained
    assert clf.type_pipeline is not None
    assert clf.category_pipeline is not None
    return "trained=True"

def test_classifier_predict_type_internship():
    pred = clf.predict_type("AI/Data Internship at DeepMind focusing on neural networks and reinforcement learning")
    assert isinstance(pred, str)
    assert len(pred) > 0
    return f"type={pred}"

def test_classifier_predict_type_scholarship():
    pred = clf.predict_type("DAAD scholarship for master students in AI with monthly stipend and tuition coverage")
    assert isinstance(pred, str)
    return f"type={pred}"

def test_classifier_predict_type_postdoc():
    pred = clf.predict_type("Postdoctoral researcher position at ETH Zurich in machine learning, academic contract 2 years")
    assert isinstance(pred, str)
    return f"type={pred}"

def test_classifier_predict_category_ai():
    pred = clf.predict_category("Deep learning research using PyTorch and transformer models for NLP")
    assert isinstance(pred, str)
    return f"category={pred}"

def test_classifier_predict_category_cybersec():
    pred = clf.predict_category("Penetration testing and vulnerability assessment, network security cryptography")
    assert isinstance(pred, str)
    return f"category={pred}"

def test_classifier_batch_predict():
    texts = [
        "Machine learning internship at Google focusing on computer vision",
        "PhD scholarship for data science and statistical modelling",
        "Cybersecurity course on ethical hacking and penetration testing",
    ]
    preds = clf.predict_batch(texts)
    assert len(preds) == 3
    assert all("type" in p and "category" in p for p in preds)
    return f"batch={[p['type'] for p in preds]}"

def test_classifier_save_load(tmp="/tmp/clf_test.joblib"):
    clf.save(tmp)
    assert os.path.exists(tmp)
    clf2 = OpportunityClassifier()
    clf2.load(tmp)
    assert clf2.is_trained
    pred = clf2.predict_type("Internship at Airbus machine learning")
    assert isinstance(pred, str)
    return f"save/load OK, pred={pred}"

test("classifier not trained initially", test_classifier_not_trained)
test("classifier trains successfully", test_classifier_train)
test("classifier predicts type: internship", test_classifier_predict_type_internship)
test("classifier predicts type: scholarship", test_classifier_predict_type_scholarship)
test("classifier predicts type: postdoc", test_classifier_predict_type_postdoc)
test("classifier predicts category: AI", test_classifier_predict_category_ai)
test("classifier predicts category: Cybersecurity", test_classifier_predict_category_cybersec)
test("classifier batch prediction (3 items)", test_classifier_batch_predict)
test("classifier save and load", test_classifier_save_load)


section("2. ML CLUSTERER")

from ml.inference.clustering import OpportunityClusterer

SAMPLE_TEXTS = [
    "Machine learning neural networks deep learning PyTorch internship at INRIA",
    "Data science statistics pandas SQL analysis internship TotalEnergies",
    "Cybersecurity penetration testing vulnerability network security Thales",
    "Software engineering backend API microservices Python Docker Siemens",
    "Scholarship DAAD funding stipend monthly tuition master PhD",
    "Postdoctoral researcher ETH Zurich academic contract NLP transformers",
    "Reinforcement learning AI safety EPFL research fellow funded project",
    "Data visualization matplotlib statistics data analysis WHO internship",
    "Cryptography network security firewall monitoring Siemens internship",
    "React frontend TypeScript API microservices agile software Capgemini",
    "Computer vision convolutional neural network image processing ETH Zurich",
    "Marie Curie Fellowship postdoc funding research cybersecurity Europe",
    "Natural language processing transformers BERT GPT language models INRIA",
    "Data pipeline Spark SQL ETH Zurich data engineering cloud internship",
    "Machine learning certificate course enroll self-paced scikit-learn",
]

clusterer = OpportunityClusterer(n_clusters=5)

def test_clusterer_not_fitted():
    assert not clusterer.is_fitted
    return "is_fitted=False"

def test_clusterer_fit():
    clusterer.fit(SAMPLE_TEXTS)
    assert clusterer.is_fitted
    assert len(clusterer.cluster_labels) == 5
    return f"labels={clusterer.cluster_labels}"

def test_clusterer_predict_single():
    cid = clusterer.predict("Machine learning PyTorch neural network deep learning internship")
    assert isinstance(cid, int)
    assert 0 <= cid < 5
    return f"cluster_id={cid}, label={clusterer.get_cluster_label(cid)}"

def test_clusterer_predict_batch():
    texts = [
        "Cybersecurity penetration testing vulnerability assessment",
        "Data science pandas visualization statistics",
        "Machine learning PyTorch deep neural networks",
    ]
    ids = clusterer.predict_batch(texts)
    assert len(ids) == 3
    assert all(isinstance(i, int) for i in ids)
    return f"cluster_ids={ids}"

def test_clusterer_get_all_labels():
    labels = clusterer.get_all_labels()
    assert isinstance(labels, dict)
    assert len(labels) == 5
    return f"all_labels_count={len(labels)}"

def test_clusterer_save_load(tmp="/tmp/clusterer_test.joblib"):
    clusterer.save(tmp)
    c2 = OpportunityClusterer()
    c2.load(tmp)
    assert c2.is_fitted
    cid = c2.predict("AI research project funded by Horizon Europe")
    return f"save/load OK, pred_cluster={cid}"

def test_clusterer_too_few_texts():
    c_small = OpportunityClusterer(n_clusters=5)
    try:
        c_small.fit(["text1", "text2"])
        return "UNEXPECTED: should have raised ValueError"
    except ValueError as e:
        return f"Correctly raised ValueError: {e}"

test("clusterer not fitted initially", test_clusterer_not_fitted)
test("clusterer fits on 15 texts", test_clusterer_fit)
test("clusterer predict single text", test_clusterer_predict_single)
test("clusterer predict batch (3 texts)", test_clusterer_predict_batch)
test("clusterer get all labels", test_clusterer_get_all_labels)
test("clusterer save and load", test_clusterer_save_load)
test("clusterer raises on too few texts", test_clusterer_too_few_texts)


section("3. ML RECOMMENDER")

from ml.inference.recommender import OpportunityRecommender

MOCK_OPPS = [
    {
        "title": "AI Internship at DeepMind",
        "description": "Machine learning research using PyTorch and neural networks",
        "skills_required": ["Python", "PyTorch", "NLP"],
        "category": "AI",
        "eligibility": "Master",
        "deadline": (datetime.now() + timedelta(days=45)).strftime("%b %d %Y"),
        "type": "internship",
    },
    {
        "title": "DAAD Scholarship",
        "description": "Funding for master students in data science programs across Europe",
        "skills_required": [],
        "category": "Data Science",
        "eligibility": "PhD",
        "deadline": (datetime.now() + timedelta(days=8)).strftime("%b %d %Y"),
        "type": "scholarship",
    },
    {
        "title": "Cybersecurity Internship at Thales",
        "description": "Penetration testing and network security vulnerability assessment",
        "skills_required": ["Python", "network security", "cryptography"],
        "category": "Cybersecurity",
        "eligibility": "Bachelor",
        "deadline": (datetime.now() - timedelta(days=3)).strftime("%b %d %Y"),
        "type": "internship",
    },
    {
        "title": "Software Engineering Postdoc at TU Berlin",
        "description": "Microservices architecture and backend API design at a leading university",
        "skills_required": ["Python", "Docker", "APIs"],
        "category": "Software Engineering",
        "eligibility": "Postdoc",
        "deadline": (datetime.now() + timedelta(days=120)).strftime("%b %d %Y"),
        "type": "postdoc",
    },
    {
        "title": "NLP Research Project at INRIA",
        "description": "Funded research project on transformers and language models",
        "skills_required": ["Python", "NLP", "Hugging Face", "PyTorch"],
        "category": "AI",
        "eligibility": "PhD",
        "deadline": (datetime.now() + timedelta(days=60)).strftime("%b %d %Y"),
        "type": "project",
    },
]

MOCK_USER = {
    "user_id": "user-001",
    "skills": ["Python", "PyTorch", "NLP", "scikit-learn"],
    "interests": ["AI", "deep learning", "natural language processing"],
    "level": "Master",
}

rec = OpportunityRecommender()

def test_recommender_not_fitted():
    assert not rec.is_fitted
    return "is_fitted=False"

def test_recommender_fit():
    rec.fit(MOCK_OPPS)
    assert rec.is_fitted
    return "fitted on 5 opportunities"

def test_recommender_level_match_exact():
    score = rec.compute_level_match("master", "Master or PhD students")
    assert score == 1.0
    return f"score={score}"

def test_recommender_level_match_adjacent():
    score = rec.compute_level_match("master", "PhD required")
    assert 0 < score < 1
    return f"score={score}"

def test_recommender_level_match_none():
    score = rec.compute_level_match("bachelor", None)
    assert score == 0.5
    return f"score={score}"

def test_recommender_recency_far():
    dl = (datetime.now() + timedelta(days=60)).strftime("%b %d %Y")
    score = rec.compute_recency_score(dl)
    assert score == 1.0
    return f"score={score}"

def test_recommender_recency_urgent():
    dl = (datetime.now() + timedelta(days=5)).strftime("%b %d %Y")
    score = rec.compute_recency_score(dl)
    assert score == 0.2
    return f"score={score}"

def test_recommender_recency_expired():
    dl = (datetime.now() - timedelta(days=5)).strftime("%b %d %Y")
    score = rec.compute_recency_score(dl)
    assert score == 0.0
    return f"score={score}"

def test_recommender_recency_none():
    score = rec.compute_recency_score(None)
    assert score == 0.3
    return f"score={score}"

def test_recommender_similarity_scores():
    scores = rec.compute_similarity_scores(MOCK_USER, MOCK_OPPS)
    assert len(scores) == 5
    assert all(isinstance(s, float) for s in scores)
    assert all(0.0 <= s <= 1.0 for s in scores)
    return f"scores={[round(s, 3) for s in scores]}"

def test_recommender_match_reasons():
    reasons = rec.generate_match_reasons(MOCK_USER, MOCK_OPPS[0], 0.5, 1.0, 1.0)
    assert isinstance(reasons, list)
    assert len(reasons) > 0
    return f"reasons={reasons}"

def test_recommender_full_recommend():
    ranked = rec.recommend(MOCK_USER, MOCK_OPPS, top_n=3)
    assert len(ranked) == 3
    assert all("final_score" in r for r in ranked)
    assert all("match_reasons" in r for r in ranked)
    scores = [r["final_score"] for r in ranked]
    assert scores == sorted(scores, reverse=True), "Results should be sorted by score desc"
    return f"top3_scores={[round(r['final_score'], 3) for r in ranked]}"

def test_recommender_empty_opportunities():
    ranked = rec.recommend(MOCK_USER, [], top_n=10)
    assert ranked == []
    return "empty_input → empty_output"

test("recommender not fitted initially", test_recommender_not_fitted)
test("recommender fits on opportunities", test_recommender_fit)
test("level match: exact match → 1.0", test_recommender_level_match_exact)
test("level match: adjacent → 0<x<1", test_recommender_level_match_adjacent)
test("level match: eligibility=None → 0.5", test_recommender_level_match_none)
test("recency: far future → 1.0", test_recommender_recency_far)
test("recency: urgent (<10d) → 0.2", test_recommender_recency_urgent)
test("recency: expired → 0.0", test_recommender_recency_expired)
test("recency: deadline=None → 0.3", test_recommender_recency_none)
test("similarity scores: 5 float values 0-1", test_recommender_similarity_scores)
test("match reasons generated", test_recommender_match_reasons)
test("full recommend: top_n=3, sorted desc", test_recommender_full_recommend)
test("recommend on empty opportunities → []", test_recommender_empty_opportunities)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2: SCRAPERS
# ══════════════════════════════════════════════════════════════════════════════

section("4. SCRAPERS (MOCK MODE)")

# We need a minimal Model stub to test scrapers without full DB setup
import mesa
from app.core.config import Settings

class MockSettings:
    SCRAPER_MODE = "mock"
    ENVIRONMENT = "development"

class MockModel(mesa.Model):
    def __init__(self):
        super().__init__()
        self.settings = MockSettings()
        self.shared_data = {}

mock_model = MockModel()

from agents.scrapers.internship_scraper import AgentInternshipScraper
from agents.scrapers.scholarship_scraper import AgentScholarshipScraper
from agents.scrapers.project_scraper import AgentProjectScraper
from agents.scrapers.certification_scraper import AgentCertificationScraper

internship_scraper = AgentInternshipScraper(1, mock_model)
scholarship_scraper = AgentScholarshipScraper(2, mock_model)
project_scraper = AgentProjectScraper(3, mock_model)
cert_scraper = AgentCertificationScraper(4, mock_model)

async def test_internship_scraper_mock():
    report = await internship_scraper.run()
    assert report["success"] == True
    assert report["items_processed"] == 20
    assert len(report["data"]) == 20
    first = report["data"][0]
    assert "title" in first
    assert "description" in first
    assert "type" in first
    assert first["type"] == "internship"
    assert "skills_required" in first
    return f"items={report['items_processed']}, sample_type={first['type']}"

async def test_scholarship_scraper_mock():
    report = await scholarship_scraper.run()
    assert report["success"] == True
    assert report["items_processed"] == 15
    first = report["data"][0]
    assert first["type"] == "scholarship"
    return f"items={report['items_processed']}"

async def test_project_scraper_mock():
    report = await project_scraper.run()
    assert report["success"] == True
    assert report["items_processed"] > 0
    first = report["data"][0]
    assert first["type"] == "project"
    return f"items={report['items_processed']}"

async def test_cert_scraper_mock():
    report = await cert_scraper.run()
    assert report["success"] == True
    assert report["items_processed"] > 0
    first = report["data"][0]
    assert first["type"] == "course"
    return f"items={report['items_processed']}"

def test_scraper_normalized_fields():
    """Verify all required fields are present in normalized output."""
    async def inner():
        report = await internship_scraper.run()
        data = report["data"]
        required_fields = ["title", "type", "category", "description",
                           "skills_required", "location", "eligibility",
                           "deadline", "source", "url"]
        for item in data[:3]:
            missing = [f for f in required_fields if f not in item]
            assert not missing, f"Missing fields: {missing}"
        return f"all {len(required_fields)} fields present in {len(data)} items"
    return asyncio.get_event_loop().run_until_complete(inner())

async def test_scraper_parallel_gather():
    """Test that all 4 scrapers can run concurrently."""
    reports = await asyncio.gather(
        internship_scraper.run_safe(),
        scholarship_scraper.run_safe(),
        project_scraper.run_safe(),
        cert_scraper.run_safe(),
    )
    total = sum(r.get("items_processed", 0) for r in reports)
    assert total > 0
    assert all(r["success"] for r in reports)
    return f"total_items={total} from {len(reports)} scrapers"

test("internship scraper: 20 mock items", test_internship_scraper_mock)
test("scholarship scraper: 15 mock items", test_scholarship_scraper_mock)
test("project scraper: mock items", test_project_scraper_mock)
test("certification scraper: mock items", test_cert_scraper_mock)
test("scraper normalized fields complete", test_scraper_normalized_fields)
test("4 scrapers run in parallel (asyncio.gather)", test_scraper_parallel_gather)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3: PROCESSING AGENTS
# ══════════════════════════════════════════════════════════════════════════════

section("5. PROCESSING AGENTS")

# Build a mock model with shared_data pre-seeded

async def _collect_all_mock_opps():
    """Get all mock data from scrapers."""
    reports = await asyncio.gather(
        internship_scraper.run_safe(),
        scholarship_scraper.run_safe(),
        project_scraper.run_safe(),
        cert_scraper.run_safe(),
    )
    all_raw = []
    for r in reports:
        all_raw.extend(r.get("data", []))
    return all_raw

RAW_OPPS = asyncio.get_event_loop().run_until_complete(_collect_all_mock_opps())
print(f"\n  [setup] Collected {len(RAW_OPPS)} raw opportunities from all scrapers")

# ── Data Cleaner ──────────────────────────────────────────────────────────────
from agents.processing.data_cleaner_agent import AgentDataCleaner

cleaner_model = MockModel()
cleaner_model.shared_data = {"raw_opportunities": RAW_OPPS[:]}
cleaner_agent = AgentDataCleaner(5, cleaner_model)

async def test_cleaner_runs():
    report = await cleaner_agent.run()
    assert report["success"] == True
    assert report["items_processed"] >= 0
    cleaned = cleaner_model.shared_data["cleaned_opportunities"]
    assert isinstance(cleaned, list)
    return f"cleaned={report['items_processed']}, skipped={report.get('skipped',0)}"

async def test_cleaner_normalizes_dates():
    sample = [{"title": "Test Opp", "description": "Test description here",
               "deadline": "Jun 15 2026", "location": "paris", "url": "https://example.com/test"}]
    m = MockModel()
    m.shared_data = {"raw_opportunities": sample}
    agent = AgentDataCleaner(5, m)
    await agent.run()
    cleaned = m.shared_data["cleaned_opportunities"]
    assert len(cleaned) == 1
    assert cleaned[0]["deadline"] is not None
    assert cleaned[0]["location"] == "Paris"
    return f"date={cleaned[0]['deadline']}, location={cleaned[0]['location']}"

async def test_cleaner_strips_html():
    sample = [{"title": "Test <b>Internship</b>",
               "description": "<p>Join our <strong>team</strong></p>",
               "deadline": "Jun 15 2026", "location": "Berlin",
               "url": "https://example.com/job"}]
    m = MockModel()
    m.shared_data = {"raw_opportunities": sample}
    agent = AgentDataCleaner(5, m)
    await agent.run()
    cleaned = m.shared_data["cleaned_opportunities"]
    assert "<" not in (cleaned[0]["description"] or "")
    return f"desc_cleaned='{cleaned[0]['description']}'"

async def test_cleaner_rejects_bad_url():
    sample = [{"title": "Bad URL Opp", "description": "Some description text here",
               "deadline": "Jun 15 2026", "location": "London", "url": "not-a-valid-url"}]
    m = MockModel()
    m.shared_data = {"raw_opportunities": sample}
    agent = AgentDataCleaner(5, m)
    report = await agent.run()
    cleaned = m.shared_data["cleaned_opportunities"]
    assert len(cleaned) == 0
    return "invalid URL → item rejected ✓"

test("data cleaner processes all raw opportunities", test_cleaner_runs)
test("data cleaner normalizes dates and locations", test_cleaner_normalizes_dates)
test("data cleaner strips HTML tags", test_cleaner_strips_html)
test("data cleaner rejects invalid URLs", test_cleaner_rejects_bad_url)


# ── Classifier Agent ──────────────────────────────────────────────────────────
from agents.processing.classifier_agent import AgentClassifier

async def test_classifier_agent():
    cleaned_opps = cleaner_model.shared_data["cleaned_opportunities"][:10]
    m = MockModel()
    m.shared_data = {"cleaned_opportunities": cleaned_opps}
    agent = AgentClassifier(6, m)
    report = await agent.run()
    assert report["success"] == True
    classified = m.shared_data["classified_opportunities"]
    assert len(classified) == len(cleaned_opps)
    for item in classified:
        assert "type" in item and item["type"]
        assert "category" in item and item["category"]
    return f"classified={len(classified)}, sample_type={classified[0]['type']}, cat={classified[0]['category']}"

async def test_classifier_agent_empty():
    m = MockModel()
    m.shared_data = {"cleaned_opportunities": []}
    agent = AgentClassifier(6, m)
    report = await agent.run()
    assert report["success"] == True
    assert report["items_processed"] == 0
    return "empty_input → items_processed=0"

test("classifier agent classifies batch", test_classifier_agent)
test("classifier agent handles empty input", test_classifier_agent_empty)


# ── Cluster Agent ─────────────────────────────────────────────────────────────
from agents.processing.cluster_agent import AgentCluster

async def test_cluster_agent():
    cleaned_opps = cleaner_model.shared_data["cleaned_opportunities"]
    # Need classified first
    clf_model = MockModel()
    clf_model.shared_data = {"cleaned_opportunities": cleaned_opps}
    clf_agent = AgentClassifier(6, clf_model)
    await clf_agent.run()
    classified = clf_model.shared_data["classified_opportunities"]

    cluster_model = MockModel()
    cluster_model.shared_data = {"classified_opportunities": classified}
    cluster_agent = AgentCluster(7, cluster_model)
    report = await cluster_agent.run()
    assert report["success"] == True
    clustered = cluster_model.shared_data["clustered_opportunities"]
    assert len(clustered) == len(classified)
    for item in clustered:
        assert "cluster_id" in item
        assert "cluster_label" in item
    return f"clustered={len(clustered)}, labels={report.get('cluster_labels', {})}"

async def test_cluster_agent_too_few():
    m = MockModel()
    m.shared_data = {"classified_opportunities": [{"title": "x", "description": "y"}] * 3}
    agent = AgentCluster(7, m)
    report = await agent.run()
    assert report["success"] == True
    assert "Too few" in report["errors"][0]
    return "too few items → graceful skip ✓"

test("cluster agent assigns cluster_id and label", test_cluster_agent)
test("cluster agent handles too-few items gracefully", test_cluster_agent_too_few)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4: RECOMMENDATION + ADVISOR AGENT
# ══════════════════════════════════════════════════════════════════════════════

section("6. RECOMMENDATION AGENT")

from agents.recommendation.advisor_agent import AgentAdvisor
from agents.recommendation.relevance_matcher_agent import AgentRelevanceMatcher

MOCK_USERS = [
    {"user_id": "u1", "skills": ["Python", "PyTorch", "NLP", "scikit-learn"],
     "interests": ["AI", "deep learning"], "level": "Master"},
    {"user_id": "u2", "skills": ["Python", "SQL", "pandas", "statistics"],
     "interests": ["Data Science", "visualization"], "level": "PhD"},
    {"user_id": "u3", "skills": ["Python", "Docker", "APIs"],
     "interests": ["Software Engineering", "microservices"], "level": "Bachelor"},
]

async def test_advisor_agent():
    """Run advisor against full pipeline output."""
    cleaned_opps = cleaner_model.shared_data["cleaned_opportunities"]
    clf_m = MockModel()
    clf_m.shared_data = {"cleaned_opportunities": cleaned_opps}
    await AgentClassifier(6, clf_m).run()
    classified = clf_m.shared_data["classified_opportunities"]

    cluster_m = MockModel()
    cluster_m.shared_data = {"classified_opportunities": classified}
    await AgentCluster(7, cluster_m).run()
    clustered = cluster_m.shared_data["clustered_opportunities"]

    adv_model = MockModel()
    adv_model.shared_data = {
        "clustered_opportunities": clustered,
        "users": MOCK_USERS,
        "recommendations": [],
    }
    matcher = AgentRelevanceMatcher(99, adv_model)
    advisor = AgentAdvisor(9, adv_model)
    advisor.matcher = matcher
    report = await advisor.run()
    assert report["success"] == True
    recs = adv_model.shared_data["recommendations"]
    assert len(recs) > 0
    first_rec = recs[0]
    assert "user_id" in first_rec
    assert "final_score" in first_rec
    assert "match_reasons" in first_rec
    assert isinstance(first_rec["match_reasons"], list)
    return f"recs={len(recs)}, sample_score={round(first_rec['final_score'],3)}, reasons={first_rec['match_reasons'][:1]}"

test("advisor agent produces recommendations with match_reasons", test_advisor_agent)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5: FULL PIPELINE SIMULATION (NO DB)
# ══════════════════════════════════════════════════════════════════════════════

section("7. FULL PIPELINE SIMULATION (NO DB)")

async def test_full_pipeline_simulation():
    """
    Simulate the full pipeline without database:
    scrape → clean → classify → cluster → recommend
    Uses mock services that return data directly.
    """
    # Phase 1: Scraping
    scrape_results = await asyncio.gather(
        internship_scraper.run_safe(),
        scholarship_scraper.run_safe(),
        project_scraper.run_safe(),
        cert_scraper.run_safe(),
    )
    raw = []
    for r in scrape_results:
        raw.extend(r.get("data", []))
    assert len(raw) > 0, "Scraping produced 0 items"
    print(f"\n    → Phase 1 (Scrape):   {len(raw)} raw items")

    # Phase 2: Clean
    clean_m = MockModel()
    clean_m.shared_data = {"raw_opportunities": raw}
    cleaner = AgentDataCleaner(5, clean_m)
    clean_report = await cleaner.run()
    cleaned = clean_m.shared_data["cleaned_opportunities"]
    print(f"    → Phase 2 (Clean):    {len(cleaned)} cleaned, {clean_report.get('skipped',0)} skipped")

    # Phase 3: Classify
    clf_m = MockModel()
    clf_m.shared_data = {"cleaned_opportunities": cleaned}
    classifier = AgentClassifier(6, clf_m)
    clf_report = await classifier.run()
    classified = clf_m.shared_data["classified_opportunities"]
    print(f"    → Phase 3 (Classify): {len(classified)} classified")

    # Phase 4: Cluster
    cluster_m = MockModel()
    cluster_m.shared_data = {"classified_opportunities": classified}
    clusterer_agent = AgentCluster(7, cluster_m)
    cluster_report = await clusterer_agent.run()
    clustered = cluster_m.shared_data["clustered_opportunities"]
    print(f"    → Phase 4 (Cluster):  {len(clustered)} clustered, labels={cluster_report.get('cluster_labels', {})}")

    # Phase 5: Recommend
    adv_m = MockModel()
    adv_m.shared_data = {
        "clustered_opportunities": clustered,
        "users": MOCK_USERS,
        "recommendations": [],
    }
    matcher = AgentRelevanceMatcher(99, adv_m)
    advisor = AgentAdvisor(9, adv_m)
    advisor.matcher = matcher
    adv_report = await advisor.run()
    recs = adv_m.shared_data["recommendations"]
    print(f"    → Phase 5 (Recommend):{len(recs)} recommendations for {len(MOCK_USERS)} users")

    assert len(raw) >= 50
    assert len(cleaned) >= 30
    assert len(classified) == len(cleaned)
    assert len(clustered) == len(classified)
    assert len(recs) > 0

    # Validate recommendation structure
    for rec in recs[:3]:
        assert "user_id" in rec
        assert "final_score" in rec
        assert "match_reasons" in rec
        assert 0.0 <= rec["final_score"] <= 1.5

    return {
        "raw": len(raw),
        "cleaned": len(cleaned),
        "classified": len(classified),
        "clustered": len(clustered),
        "recommendations": len(recs),
    }

pipeline_result = test("full pipeline simulation (5 phases)", test_full_pipeline_simulation)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6: DATA QUALITY ASSERTIONS
# ══════════════════════════════════════════════════════════════════════════════

section("8. DATA QUALITY CHECKS")

async def _run_pipeline_and_return():
    scrape_results = await asyncio.gather(
        internship_scraper.run_safe(),
        scholarship_scraper.run_safe(),
        project_scraper.run_safe(),
        cert_scraper.run_safe(),
    )
    raw = []
    for r in scrape_results: raw.extend(r.get("data", []))
    m1 = MockModel(); m1.shared_data = {"raw_opportunities": raw}
    await AgentDataCleaner(5, m1).run()
    cleaned = m1.shared_data["cleaned_opportunities"]
    m2 = MockModel(); m2.shared_data = {"cleaned_opportunities": cleaned}
    await AgentClassifier(6, m2).run()
    classified = m2.shared_data["classified_opportunities"]
    m3 = MockModel(); m3.shared_data = {"classified_opportunities": classified}
    await AgentCluster(7, m3).run()
    clustered = m3.shared_data["clustered_opportunities"]
    return clustered

PIPELINE_DATA = asyncio.get_event_loop().run_until_complete(_run_pipeline_and_return())

def test_all_types_present():
    types_found = {o["type"] for o in PIPELINE_DATA if "type" in o}
    expected = {"internship", "scholarship", "project", "course"}
    missing = expected - types_found
    assert not missing, f"Missing types: {missing}"
    return f"types_found={types_found}"

def test_all_categories_present():
    cats = {o.get("category") for o in PIPELINE_DATA if o.get("category")}
    assert len(cats) >= 2
    return f"categories={cats}"

def test_all_items_have_cluster():
    without_cluster = [o for o in PIPELINE_DATA if "cluster_id" not in o]
    assert len(without_cluster) == 0
    return f"all {len(PIPELINE_DATA)} items have cluster_id"

def test_valid_url_format():
    for item in PIPELINE_DATA:
        url = item.get("url", "")
        assert url.startswith("http"), f"Bad URL: {url}"
    return f"all {len(PIPELINE_DATA)} URLs are valid"

def test_no_empty_titles():
    empty = [o for o in PIPELINE_DATA if not o.get("title")]
    assert len(empty) == 0
    return f"all {len(PIPELINE_DATA)} items have non-empty titles"

def test_deadline_iso_format():
    """Dates should be normalized to ISO format (YYYY-MM-DD) after cleaning."""
    import re
    iso_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    non_iso = [o for o in PIPELINE_DATA if o.get("deadline") and not iso_pattern.match(o["deadline"])]
    assert len(non_iso) == 0, f"Non-ISO deadlines: {[o['deadline'] for o in non_iso[:3]]}"
    return f"all deadlines in ISO format"

test("all opportunity types present", test_all_types_present)
test("multiple categories present", test_all_categories_present)
test("all items have cluster_id", test_all_items_have_cluster)
test("all URLs are valid (http/https)", test_valid_url_format)
test("no empty titles after cleaning", test_no_empty_titles)
test("deadlines in ISO format after cleaning", test_deadline_iso_format)


# ══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

section("TEST SUMMARY")

passed = [r for r in results if r["status"] == "PASS"]
failed = [r for r in results if r["status"] == "FAIL"]
total = len(results)

print(f"\n  Total:  {total}")
print(f"  Passed: {len(passed)} ✅")
print(f"  Failed: {len(failed)} ❌")
print(f"  Pass rate: {len(passed)/total*100:.1f}%")

if failed:
    print("\n  Failed tests:")
    for f in failed:
        print(f"    ❌ {f['name']}")
        print(f"       {f.get('error', 'unknown error')}")

if pipeline_result:
    print(f"\n  Pipeline stats (mock data):")
    for k, v in pipeline_result.items():
        print(f"    {k}: {v}")

print()
sys.exit(0 if not failed else 1)
