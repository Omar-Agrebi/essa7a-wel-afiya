import sys
import os
import asyncio
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# --- Path Setup ---
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.inference.classifier import OpportunityClassifier
from ml.inference.clustering import OpportunityClusterer
from ml.inference.recommender import OpportunityRecommender
from agents.scrapers.internship_scraper import AgentInternshipScraper
from agents.scrapers.scholarship_scraper import AgentScholarshipScraper

# --- 1. ML Classifier Accuracy ---
def evaluate_classifier():
    print("\n" + "="*60)
    print("  SECTION 1: ML CLASSIFIER ACCURACY & PERFORMANCE")
    print("="*60)
    
    clf = OpportunityClassifier()
    texts, type_labels, cat_labels = clf._build_training_data()
    
    # Initialize pipelines (usually done in train(), but we do it manually for split testing)
    from sklearn.pipeline import Pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    clf.type_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
        ("clf", LogisticRegression(max_iter=1000, C=1.0, random_state=42)),
    ])
    clf.category_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
        ("clf", LogisticRegression(max_iter=1000, C=1.0, random_state=42)),
    ])
    
    # Split for "real" validation
    X_train, X_test, y_train_type, y_test_type = train_test_split(texts, type_labels, test_size=0.2, random_state=42)
    _, _, y_train_cat, y_test_cat = train_test_split(texts, cat_labels, test_size=0.2, random_state=42)
    
    # Train on training set only
    clf.type_pipeline.fit(X_train, y_train_type)
    clf.category_pipeline.fit(X_train, y_train_cat)
    clf.is_trained = True
    
    # Predict
    type_preds = clf.type_pipeline.predict(X_test)
    cat_preds = clf.category_pipeline.predict(X_test)
    
    print("\n--- [TYPE CLASSIFICATION REPORT] ---")
    print(classification_report(y_test_type, type_preds))
    
    print("\n--- [CATEGORY CLASSIFICATION REPORT] ---")
    print(classification_report(y_test_cat, cat_preds))
    
    # Unseen real-world test cases
    print("\n--- [UNSEEN TEST SAMPLES] ---")
    unseen_samples = [
        ("Looking for a PhD position in Switzerland focusing on deep learning and neural networks for autonomous driving.", "postdoc", "AI"),
        ("Scholarship for African students to study Data Science in France. Covers tuition and living expenses.", "scholarship", "Data Science"),
        ("Junior developer role focusing on React and Node.js. Join a fast-growing startup in Berlin.", "internship", "Software Engineering"), # Might be classified as internship based on training data
        ("Free online course about ethical hacking and network security by Google.", "course", "Cybersecurity"),
    ]
    
    correct = 0
    for text, expected_type, expected_cat in unseen_samples:
        pred_type = clf.predict_type(text)
        pred_cat = clf.predict_category(text)
        is_correct = (pred_type == expected_type and pred_cat == expected_cat)
        if is_correct: correct += 1
        status = "PASS" if is_correct else "FAIL"
        print(f"[{status}] Sample: {text[:50]}...")
        print(f"       Expected: {expected_type}/{expected_cat} | Predicted: {pred_type}/{pred_cat}")
    
    print(f"\nUnseen Generalization: {correct/len(unseen_samples):.1%}")

# --- 2. Clusterer Results ---
def evaluate_clusterer():
    print("\n" + "="*60)
    print("  SECTION 2: CLUSTERER TOPIC MODELING RESULTS")
    print("="*60)
    
    clusterer = OpportunityClusterer(n_clusters=5)
    clf = OpportunityClassifier()
    texts, _, _ = clf._build_training_data()
    
    clusterer.fit(texts)
    
    print("\nGenerated Clusters and their 'Topic Labels':")
    for cid, label in clusterer.get_all_labels().items():
        print(f"Cluster {cid}: {label}")
        
    # Sample items in clusters
    preds = clusterer.predict_batch(texts)
    print("\nCluster Sample Content:")
    for i in range(5):
        cid = preds[i]
        print(f" - [{clusterer.get_cluster_label(cid)}] {texts[i][:60]}...")

# --- 3. Recommender Results ---
def evaluate_recommender():
    print("\n" + "="*60)
    print("  SECTION 3: RECOMMENDER PERSONALIZATION TEST")
    print("="*60)
    
    rec = OpportunityRecommender()
    
    # Mock user
    user = {
        "user_id": "real-user-42",
        "skills": ["Python", "Machine Learning", "PyTorch"],
        "interests": ["AI", "Deep Learning"],
        "level": "Master"
    }
    
    # Mock opportunities (including some irrelevant ones)
    opps = [
        {"id": "o1", "title": "AI Research Internship", "description": "Work with neural networks and PyTorch", "skills_required": ["Python", "PyTorch"], "category": "AI", "eligibility": "Master", "deadline": "Dec 31 2026"},
        {"id": "o2", "title": "Web Dev Role", "description": "React and CSS development", "skills_required": ["Javascript", "CSS"], "category": "Software Engineering", "eligibility": "Bachelor", "deadline": "Jun 15 2026"},
        {"id": "o3", "title": "Data Science Course", "description": "Learn statistics and pandas", "skills_required": ["Python"], "category": "Data Science", "eligibility": "All", "deadline": "Sep 01 2026"},
        {"id": "o4", "title": "Scholarship for Master in AI", "description": "Funding for AI students", "skills_required": [], "category": "AI", "eligibility": "Master", "deadline": "Jan 10 2025"}, # Very soon
    ]
    
    results = rec.recommend(user, opps, top_n=3)
    
    print(f"\nUser Profile: {user['skills']} | Interests: {user['interests']}")
    print("\nTop 3 Recommendations:")
    for i, r in enumerate(results):
        print(f"{i+1}. {r['title']} (Score: {r['final_score']:.3f})")
        print(f"   Reasons: {', '.join(r['match_reasons'])}")

# --- 4. Scraper Live Simulation ---
async def evaluate_scrapers():
    print("\n" + "="*60)
    print("  SECTION 4: SCRAPER DATA EXTRACTION (MOCK-LIVE)")
    print("="*60)
    
    # We mock the model for the agent
    import mesa
    class MockModel(mesa.Model):
        def __init__(self):
            super().__init__()
            class Settings: SCRAPER_MODE = "mock"
            self.settings = Settings()
    
    model = MockModel()
    s1 = AgentInternshipScraper(1, model)
    s2 = AgentScholarshipScraper(2, model)
    
    print("\nFetching data...")
    r1 = await s1.run()
    r2 = await s2.run()
    
    print(f"Internships found: {r1['items_processed']}")
    print(f"Scholarships found: {r2['items_processed']}")
    
    print("\nSample Extracted Item:")
    if r1['data']:
        item = r1['data'][0]
        for k, v in item.items():
            print(f" - {k}: {v}")

# --- Main ---
async def main():
    evaluate_classifier()
    evaluate_clusterer()
    evaluate_recommender()
    await evaluate_scrapers()

if __name__ == "__main__":
    asyncio.run(main())
