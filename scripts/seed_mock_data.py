"""
Mock Data Seeder — Intelligent University Observatory
Generates and inserts rich demo data directly via raw SQL (SQLite compatible).
Bypasses SQLAlchemy ARRAY/UUID PostgreSQL-specific types for local dev.

Run: python scripts/seed_mock_data.py
"""

import asyncio
import uuid
import json
import random
import sys
import os
from datetime import datetime, timedelta, timezone, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import aiosqlite

DB_PATH = "test_observatory.db"

NOW = datetime.now(timezone.utc)

def uid(): return str(uuid.uuid4())
def ts(): return NOW.isoformat()
def future(days): return (date.today() + timedelta(days=days)).isoformat()
def past(days): return (date.today() - timedelta(days=days)).isoformat()


# ── OPPORTUNITIES ──────────────────────────────────────────────────────────────

OPPORTUNITIES = [
    # ── Internships ────────────────────────────────────────────────────────────
    {
        "id": uid(), "title": "AI Research Intern — Reinforcement Learning",
        "type": "internship", "category": "AI",
        "description": "Join DeepMind's research team to work on state-of-the-art reinforcement learning algorithms. You'll collaborate with world-class researchers, implement experiments in PyTorch, and contribute to publications. We're looking for someone passionate about AGI safety and multi-agent systems.",
        "skills_required": json.dumps(["Python", "PyTorch", "Reinforcement Learning", "Mathematics"]),
        "location": "London, UK", "eligibility": "Master or PhD",
        "deadline": future(45), "source": "DeepMind Careers",
        "url": "https://mock.deepmind.com/jobs/rl-intern-2026",
        "cluster_id": 0, "cluster_label": "machine learning phd research",
    },
    {
        "id": uid(), "title": "Machine Learning Engineer Intern",
        "type": "internship", "category": "AI",
        "description": "Work alongside Airbus data science teams to develop predictive maintenance models using sensor data from aircraft engines. You'll apply anomaly detection, time-series forecasting, and deploy models using MLOps pipelines. Python, scikit-learn, and Docker required.",
        "skills_required": json.dumps(["Python", "scikit-learn", "MLOps", "Docker", "Time Series"]),
        "location": "Toulouse, France", "eligibility": "Master",
        "deadline": future(30), "source": "Airbus Internship Portal",
        "url": "https://mock.airbus.com/intern/ml-engineer-2026",
        "cluster_id": 0, "cluster_label": "machine learning phd research",
    },
    {
        "id": uid(), "title": "NLP Research Intern",
        "type": "internship", "category": "AI",
        "description": "INRIA Paris is seeking an NLP intern to work on transformer-based models for scientific text understanding. You'll fine-tune large language models, build evaluation pipelines, and prototype a knowledge graph extractor for academic publications.",
        "skills_required": json.dumps(["Python", "Hugging Face", "NLP", "PyTorch", "BERT"]),
        "location": "Paris, France", "eligibility": "Master or PhD",
        "deadline": future(60), "source": "INRIA Open Positions",
        "url": "https://mock.inria.fr/positions/nlp-intern-2026",
        "cluster_id": 0, "cluster_label": "machine learning phd research",
    },
    {
        "id": uid(), "title": "Data Science Intern — Satellite Analytics",
        "type": "internship", "category": "Data Science",
        "description": "Analyze telemetry data from ESA's Earth observation satellites. You'll build data pipelines using Spark, create visualizations for mission operations teams, and apply statistical models to detect anomalies in satellite health data.",
        "skills_required": json.dumps(["Python", "Spark", "pandas", "SQL", "statistics"]),
        "location": "Darmstadt, Germany", "eligibility": "Bachelor or Master",
        "deadline": future(15), "source": "ESA Internships",
        "url": "https://mock.esa.int/internship/data-science-satellite",
        "cluster_id": 1, "cluster_label": "data science statistics analysis",
    },
    {
        "id": uid(), "title": "Cybersecurity Analyst Intern",
        "type": "internship", "category": "Cybersecurity",
        "description": "Join Thales Group's Cyber Defence team. Work on real penetration testing engagements, vulnerability assessments of critical infrastructure, and contribute to threat intelligence reports. You'll learn industry-standard tools like Metasploit, Burp Suite, and Wireshark.",
        "skills_required": json.dumps(["Python", "Penetration Testing", "network security", "cryptography", "Linux"]),
        "location": "Paris, France", "eligibility": "Master",
        "deadline": future(8), "source": "Thales Group",
        "url": "https://mock.thalesgroup.com/careers/cybersec-intern",
        "cluster_id": 2, "cluster_label": "security network cryptography",
    },
    {
        "id": uid(), "title": "Backend Engineer Intern — Cloud Infrastructure",
        "type": "internship", "category": "Software Engineering",
        "description": "Build microservices for Siemens Industrial IoT platform. You'll design REST APIs, work with Kubernetes, implement CI/CD pipelines, and contribute to a real production system serving thousands of industrial clients across Europe.",
        "skills_required": json.dumps(["Python", "Docker", "Kubernetes", "REST APIs", "PostgreSQL"]),
        "location": "Munich, Germany", "eligibility": "Bachelor or Master",
        "deadline": future(50), "source": "Siemens Careers",
        "url": "https://mock.siemens.com/jobs/backend-intern-iot",
        "cluster_id": 3, "cluster_label": "software engineering api backend",
    },
    {
        "id": uid(), "title": "Computer Vision Research Intern",
        "type": "internship", "category": "AI",
        "description": "ETH Zurich Computer Vision Lab is looking for a research intern to work on 3D scene understanding for autonomous systems. You'll implement state-of-the-art SLAM algorithms, work with LiDAR point cloud data, and experiment with NeRF-based representations.",
        "skills_required": json.dumps(["Python", "PyTorch", "computer vision", "OpenCV", "3D geometry"]),
        "location": "Zurich, Switzerland", "eligibility": "Master or PhD",
        "deadline": future(90), "source": "ETH Zurich",
        "url": "https://mock.ethz.ch/cv-lab/intern-2026",
        "cluster_id": 0, "cluster_label": "machine learning phd research",
    },
    {
        "id": uid(), "title": "Data Engineering Intern",
        "type": "internship", "category": "Data Science",
        "description": "TotalEnergies digital team needs a data engineering intern to build robust ETL pipelines for energy consumption forecasting. You'll work with Apache Kafka, Airflow, and dbt to create real-time data streams from oil platform sensors.",
        "skills_required": json.dumps(["Python", "Spark", "Kafka", "Airflow", "SQL", "dbt"]),
        "location": "Remote", "eligibility": "Master",
        "deadline": future(25), "source": "TotalEnergies",
        "url": "https://mock.totalenergies.com/data-engineer-intern",
        "cluster_id": 1, "cluster_label": "data science statistics analysis",
    },
    {
        "id": uid(), "title": "AI Safety Research Intern",
        "type": "internship", "category": "AI",
        "description": "Work with the EPFL AI Safety team on interpretability methods for large language models. Investigate attention mechanisms, develop probing classifiers, and contribute to research on making AI systems more transparent and trustworthy.",
        "skills_required": json.dumps(["Python", "PyTorch", "NLP", "research", "mathematics"]),
        "location": "Lausanne, Switzerland", "eligibility": "Master or PhD",
        "deadline": future(7), "source": "EPFL",
        "url": "https://mock.epfl.ch/research/ai-safety-intern",
        "cluster_id": 0, "cluster_label": "machine learning phd research",
    },
    {
        "id": uid(), "title": "Full-Stack Developer Intern",
        "type": "internship", "category": "Software Engineering",
        "description": "Capgemini's digital innovation lab is looking for a full-stack intern to build enterprise dashboards. You'll develop React front-ends, FastAPI backends, and integrate with SAP systems. Agile methodology, TypeScript, and REST API experience required.",
        "skills_required": json.dumps(["TypeScript", "React", "Python", "FastAPI", "REST APIs", "agile"]),
        "location": "Brussels, Belgium", "eligibility": "Bachelor",
        "deadline": future(35), "source": "Capgemini",
        "url": "https://mock.capgemini.com/jobs/fullstack-intern-be",
        "cluster_id": 3, "cluster_label": "software engineering api backend",
    },

    # ── Scholarships ───────────────────────────────────────────────────────────
    {
        "id": uid(), "title": "DAAD Excellence Scholarship — AI & Machine Learning",
        "type": "scholarship", "category": "AI",
        "description": "The German Academic Exchange Service (DAAD) offers a prestigious scholarship for outstanding international students pursuing Master or PhD studies in AI, machine learning, or data science at German universities. Award includes 1,200 EUR/month stipend, health insurance, travel allowance, and tuition waiver for up to 24 months.",
        "skills_required": json.dumps([]),
        "location": "Germany", "eligibility": "Master or PhD",
        "deadline": future(55), "source": "DAAD",
        "url": "https://mock.daad.de/scholarships/ai-excellence-2026",
        "cluster_id": 4, "cluster_label": "scholarship funding stipend",
    },
    {
        "id": uid(), "title": "Eiffel Excellence Scholarship — Data Science",
        "type": "scholarship", "category": "Data Science",
        "description": "The Eiffel programme awards merit-based scholarships to high-potential international students for Master's and PhD programs in French grandes écoles and universities. Fields prioritized: data science, statistics, mathematics, and computer science. Includes 1,181 EUR/month, housing allowance, and return airfare.",
        "skills_required": json.dumps([]),
        "location": "France", "eligibility": "Master",
        "deadline": future(12), "source": "Campus France",
        "url": "https://mock.campusfrance.org/eiffel/data-science-2026",
        "cluster_id": 4, "cluster_label": "scholarship funding stipend",
    },
    {
        "id": uid(), "title": "Marie Skłodowska-Curie Fellowship — Cybersecurity",
        "type": "scholarship", "category": "Cybersecurity",
        "description": "Horizon Europe's prestigious MSCA Individual Fellowship supports postdoctoral researchers in cybersecurity, cryptography, and network resilience. Fellows receive a living allowance of approximately 3,400 EUR/month, mobility allowance, and family allowance. Collaborate with European research institutions.",
        "skills_required": json.dumps([]),
        "location": "European Union", "eligibility": "Postdoc",
        "deadline": future(80), "source": "Horizon Europe",
        "url": "https://mock.horizoneurope.eu/msca/cybersecurity-2026",
        "cluster_id": 4, "cluster_label": "scholarship funding stipend",
    },
    {
        "id": uid(), "title": "Swiss Government Excellence Scholarship",
        "type": "scholarship", "category": "AI",
        "description": "Fully funded scholarship for international PhD and postdoctoral candidates at Swiss federal institutions (ETH Zurich, EPFL, Swiss universities). Fields: computer science, AI, robotics. Includes full health insurance, living allowance of 1,920 CHF/month, housing, and return flights.",
        "skills_required": json.dumps([]),
        "location": "Switzerland", "eligibility": "PhD",
        "deadline": future(100), "source": "Swiss Government",
        "url": "https://mock.sbfi.admin.ch/scholarships/excellence-2026",
        "cluster_id": 4, "cluster_label": "scholarship funding stipend",
    },
    {
        "id": uid(), "title": "Gates Cambridge Scholarship",
        "type": "scholarship", "category": "AI",
        "description": "One of the most competitive postgraduate scholarships in the world, the Gates Cambridge Scholarship is awarded to exceptional students from outside the UK pursuing full-time PhD programs at the University of Cambridge. Covers full tuition, living allowance, and flight costs.",
        "skills_required": json.dumps([]),
        "location": "Cambridge, UK", "eligibility": "PhD",
        "deadline": future(5), "source": "Gates Cambridge Trust",
        "url": "https://mock.gatescambridge.org/scholarships/2026",
        "cluster_id": 4, "cluster_label": "scholarship funding stipend",
    },
    {
        "id": uid(), "title": "Erasmus+ Scholarship — Software Engineering",
        "type": "scholarship", "category": "Software Engineering",
        "description": "Erasmus+ supports mobility for students in accredited European joint Master programs. This call targets software engineering and systems design students. Includes a monthly scholarship of up to 1,000 EUR, insurance, and university fees waiver for the full duration.",
        "skills_required": json.dumps([]),
        "location": "European Union", "eligibility": "Master",
        "deadline": future(40), "source": "Erasmus+",
        "url": "https://mock.erasmus.eu/scholarships/software-eng-2026",
        "cluster_id": 4, "cluster_label": "scholarship funding stipend",
    },

    # ── Research Projects ──────────────────────────────────────────────────────
    {
        "id": uid(), "title": "Federated Learning for Medical Imaging — Horizon Europe",
        "type": "project", "category": "AI",
        "description": "Funded research project developing privacy-preserving federated learning techniques for distributed medical image analysis across European hospital networks. PhD position available. You'll collaborate with Max Planck Institute, KU Leuven, and Oxford. ANR co-funded, 48 months.",
        "skills_required": json.dumps(["Python", "PyTorch", "federated learning", "research", "medical imaging"]),
        "location": "Remote / Paris", "eligibility": "PhD",
        "deadline": future(70), "source": "Horizon Europe",
        "url": "https://mock.horizoneurope.eu/projects/fedmed-2026",
        "cluster_id": 0, "cluster_label": "machine learning phd research",
    },
    {
        "id": uid(), "title": "Explainable AI for Financial Risk Assessment",
        "type": "project", "category": "AI",
        "description": "ERC-funded research project at Sorbonne University on developing explainable AI methods for credit risk models used by European banks. The project seeks a PhD candidate with strong background in machine learning and statistics. Salary: 2,100 EUR/month for 36 months.",
        "skills_required": json.dumps(["Python", "scikit-learn", "explainable AI", "statistics", "NLP"]),
        "location": "Paris, France", "eligibility": "PhD",
        "deadline": future(20), "source": "ERC / Sorbonne",
        "url": "https://mock.sorbonne.fr/research/xai-finance-phd",
        "cluster_id": 0, "cluster_label": "machine learning phd research",
    },
    {
        "id": uid(), "title": "Cybersecurity Research — Vulnerability Detection in IoT",
        "type": "project", "category": "Cybersecurity",
        "description": "KU Leuven Computer Security and Industrial Cryptography (COSIC) group seeks a PhD researcher to investigate automated vulnerability detection in IoT firmware using symbolic execution and fuzzing techniques. EU-funded, competitive salary.",
        "skills_required": json.dumps(["C/C++", "Python", "fuzzing", "symbolic execution", "reverse engineering"]),
        "location": "Leuven, Belgium", "eligibility": "PhD",
        "deadline": future(45), "source": "KU Leuven COSIC",
        "url": "https://mock.kuleuven.be/cosic/phd-iot-security",
        "cluster_id": 2, "cluster_label": "security network cryptography",
    },
    {
        "id": uid(), "title": "Climate Prediction with Deep Learning — Politecnico",
        "type": "project", "category": "AI",
        "description": "Politecnico di Milano and CNR are seeking a PhD candidate to develop physics-informed deep learning models for multi-decadal climate prediction. The project is part of the Italian National Recovery and Resilience Plan (PNRR), funded for 3 years.",
        "skills_required": json.dumps(["Python", "PyTorch", "physics-informed ML", "climate data", "HPC"]),
        "location": "Milan, Italy", "eligibility": "PhD",
        "deadline": future(35), "source": "Politecnico di Milano",
        "url": "https://mock.polimi.it/research/climate-dl-phd",
        "cluster_id": 0, "cluster_label": "machine learning phd research",
    },
    {
        "id": uid(), "title": "NLP for Scientific Knowledge Graphs — Max Planck",
        "type": "project", "category": "AI",
        "description": "Max Planck Institute for Informatics seeks a postdoctoral or PhD researcher for a project on extracting structured knowledge from scientific literature using transformer models. Collaborate with international partners, publish in top-tier venues (ACL, EMNLP, ICLR).",
        "skills_required": json.dumps(["Python", "NLP", "knowledge graphs", "Hugging Face", "SPARQL"]),
        "location": "Saarbrücken, Germany", "eligibility": "PhD or Postdoc",
        "deadline": future(60), "source": "Max Planck Institute",
        "url": "https://mock.mpi-inf.mpg.de/positions/nlp-kg-2026",
        "cluster_id": 0, "cluster_label": "machine learning phd research",
    },

    # ── Courses / Certifications ───────────────────────────────────────────────
    {
        "id": uid(), "title": "Deep Learning Specialization — Neural Networks & AI",
        "type": "course", "category": "AI",
        "description": "A comprehensive 5-course specialization covering neural networks from scratch to advanced architectures (CNNs, RNNs, Transformers). Learn to build production-ready deep learning models with TensorFlow and PyTorch. Includes certificate of completion recognized by top employers. Self-paced, 40 hours total.",
        "skills_required": json.dumps(["Python", "TensorFlow", "PyTorch", "mathematics"]),
        "location": "Online", "eligibility": "Bachelor or higher",
        "deadline": future(365), "source": "Coursera",
        "url": "https://mock.coursera.org/specializations/deep-learning-2026",
        "cluster_id": 0, "cluster_label": "machine learning phd research",
    },
    {
        "id": uid(), "title": "Applied Data Science with Python — Professional Certificate",
        "type": "course", "category": "Data Science",
        "description": "Master data science workflows from data collection to model deployment. Covers pandas, NumPy, matplotlib, scikit-learn, SQL, and A/B testing. Hands-on projects with real datasets. Certificate recognized by industry partners including IBM, Microsoft, and Google.",
        "skills_required": json.dumps(["Python", "pandas", "statistics", "SQL", "scikit-learn"]),
        "location": "Online", "eligibility": "All levels",
        "deadline": future(365), "source": "Coursera",
        "url": "https://mock.coursera.org/certificates/applied-data-science-python",
        "cluster_id": 1, "cluster_label": "data science statistics analysis",
    },
    {
        "id": uid(), "title": "Ethical Hacking & Penetration Testing Bootcamp",
        "type": "course", "category": "Cybersecurity",
        "description": "Industry-recognized cybersecurity certification covering ethical hacking methodologies, penetration testing frameworks (OWASP, PTES), network security, exploit development, and incident response. Prepares for CEH and OSCP certifications. 60 hours of hands-on labs.",
        "skills_required": json.dumps(["Linux", "network security", "Python", "Metasploit", "Wireshark"]),
        "location": "Online", "eligibility": "Bachelor or higher",
        "deadline": future(365), "source": "Udemy",
        "url": "https://mock.udemy.com/courses/ethical-hacking-complete-2026",
        "cluster_id": 2, "cluster_label": "security network cryptography",
    },
    {
        "id": uid(), "title": "MLOps Engineering — From Notebook to Production",
        "type": "course", "category": "AI",
        "description": "Learn to deploy, monitor, and maintain ML systems in production. Covers MLflow, Docker, Kubernetes, CI/CD for ML, data versioning with DVC, and model monitoring. Industry-relevant certification for ML engineers and data scientists.",
        "skills_required": json.dumps(["Python", "Docker", "Kubernetes", "MLflow", "CI/CD"]),
        "location": "Online", "eligibility": "All levels",
        "deadline": future(365), "source": "Coursera",
        "url": "https://mock.coursera.org/courses/mlops-production-2026",
        "cluster_id": 0, "cluster_label": "machine learning phd research",
    },
    {
        "id": uid(), "title": "Microservices Architecture with FastAPI & Docker",
        "type": "course", "category": "Software Engineering",
        "description": "Build scalable microservices from scratch with Python, FastAPI, PostgreSQL, Redis, and Docker Compose. Learn API design best practices, service discovery, message queues, and deployment automation. Certificate program, 35 hours, self-paced.",
        "skills_required": json.dumps(["Python", "FastAPI", "Docker", "PostgreSQL", "REST APIs"]),
        "location": "Online", "eligibility": "All levels",
        "deadline": future(365), "source": "Udemy",
        "url": "https://mock.udemy.com/courses/microservices-fastapi-docker",
        "cluster_id": 3, "cluster_label": "software engineering api backend",
    },

    # ── Postdocs ───────────────────────────────────────────────────────────────
    {
        "id": uid(), "title": "Postdoctoral Researcher — Trustworthy ML",
        "type": "postdoc", "category": "AI",
        "description": "ETH Zurich AI Center invites applications for a postdoctoral research position in trustworthy machine learning. Research focus: robustness, fairness, and interpretability of deep learning models. Academic contract, 2 years, salary scale IV (100%). Starting date: negotiable.",
        "skills_required": json.dumps(["Python", "PyTorch", "research", "ML theory", "publications"]),
        "location": "Zurich, Switzerland", "eligibility": "Postdoc",
        "deadline": future(120), "source": "ETH Zurich",
        "url": "https://mock.ethz.ch/ai-center/postdoc-trustworthy-ml",
        "cluster_id": 0, "cluster_label": "machine learning phd research",
    },
    {
        "id": uid(), "title": "Research Fellow — NLP & Knowledge Representation",
        "type": "postdoc", "category": "AI",
        "description": "INRIA Paris-Rocquencourt is seeking a Research Fellow (postdoc) to join the ALMAnaCH team working on multilingual NLP and knowledge-graph-based reasoning. 2-year academic contract. Salary: 2,800–3,200 EUR/month depending on experience.",
        "skills_required": json.dumps(["Python", "NLP", "knowledge graphs", "PyTorch", "research"]),
        "location": "Paris, France", "eligibility": "Postdoc",
        "deadline": future(90), "source": "INRIA",
        "url": "https://mock.inria.fr/positions/postdoc-nlp-2026",
        "cluster_id": 0, "cluster_label": "machine learning phd research",
    },
    {
        "id": uid(), "title": "Postdoc — Cybersecurity & Formal Verification",
        "type": "postdoc", "category": "Cybersecurity",
        "description": "University of Amsterdam's security group seeks a postdoc in formal verification of cryptographic protocols. You'll use proof assistants (Coq, Isabelle), analyze real-world TLS implementations, and publish in top security venues (IEEE S&P, CCS, USENIX).",
        "skills_required": json.dumps(["formal verification", "Coq", "cryptography", "C", "research"]),
        "location": "Amsterdam, Netherlands", "eligibility": "Postdoc",
        "deadline": future(75), "source": "University of Amsterdam",
        "url": "https://mock.uva.nl/positions/postdoc-crypto-formal-2026",
        "cluster_id": 2, "cluster_label": "security network cryptography",
    },
]


# ── USERS ──────────────────────────────────────────────────────────────────────

# Hashed password for "Password123!" (argon2id)
# We use bcrypt hash for simplicity: "Password123!"
HASHED_PASSWORD = "$2b$12$JuvhpRuj0bwZqsrXgQscIu/Z8Rb0LKnbTO9ZHpElUqgajSYDXS6GG"

USER_ALICE_ID = uid()
USER_BOB_ID = uid()
USER_CAROL_ID = uid()
USER_DIANA_ID = uid()

USERS = [
    {
        "user_id": USER_ALICE_ID,
        "name": "Alice Martin",
        "email": "alice@example.com",
        "hashed_password": HASHED_PASSWORD,
        "skills": json.dumps(["Python", "PyTorch", "NLP", "Hugging Face", "scikit-learn", "Docker"]),
        "interests": json.dumps(["AI", "deep learning", "natural language processing", "research"]),
        "level": "master",
    },
    {
        "user_id": USER_BOB_ID,
        "name": "Bob Chen",
        "email": "bob@example.com",
        "hashed_password": HASHED_PASSWORD,
        "skills": json.dumps(["Python", "pandas", "SQL", "statistics", "R", "Spark", "Tableau"]),
        "interests": json.dumps(["Data Science", "visualization", "machine learning", "analytics"]),
        "level": "phd",
    },
    {
        "user_id": USER_CAROL_ID,
        "name": "Carol Ndiaye",
        "email": "carol@example.com",
        "hashed_password": HASHED_PASSWORD,
        "skills": json.dumps(["Python", "network security", "cryptography", "Linux", "Metasploit", "Wireshark"]),
        "interests": json.dumps(["Cybersecurity", "ethical hacking", "network defense"]),
        "level": "master",
    },
    {
        "user_id": USER_DIANA_ID,
        "name": "Diana Kowalski",
        "email": "diana@example.com",
        "hashed_password": HASHED_PASSWORD,
        "skills": json.dumps(["Python", "FastAPI", "Docker", "PostgreSQL", "REST APIs", "TypeScript", "React"]),
        "interests": json.dumps(["Software Engineering", "backend development", "microservices"]),
        "level": "bachelor",
    },
]


# ── RECOMMENDATIONS ────────────────────────────────────────────────────────────

def build_recommendations(opps: list[dict], users: list[dict]) -> list[dict]:
    """Generate realistic recommendations for each user."""
    recs = []
    from ml.inference.recommender import OpportunityRecommender

    recommender = OpportunityRecommender()

    for user in users:
        user_dict = {
            "user_id": user["user_id"],
            "skills": json.loads(user["skills"]),
            "interests": json.loads(user["interests"]),
            "level": user["level"],
        }
        opp_dicts = []
        for o in opps:
            opp_dicts.append({
                "id": o["id"],
                "title": o["title"],
                "type": o["type"],
                "category": o["category"],
                "description": o["description"],
                "skills_required": json.loads(o["skills_required"]),
                "eligibility": o["eligibility"],
                "deadline": o["deadline"],
                "cluster_id": o["cluster_id"],
                "cluster_label": o["cluster_label"],
            })

        scored = recommender.recommend(user_dict, opp_dicts, top_n=8)

        for item in scored:
            recs.append({
                "recommendation_id": uid(),
                "user_id": user["user_id"],
                "opportunity_id": item["id"],
                "score": round(item["final_score"], 4),
                "match_reasons": json.dumps(item["match_reasons"]),
                "created_at": ts(),
            })

    return recs


# ── NOTIFICATIONS ──────────────────────────────────────────────────────────────

def build_notifications(opps: list[dict], users: list[dict]) -> list[dict]:
    """Generate deadline and recommendation notifications."""
    notifs = []
    urgent_opps = [o for o in opps if o["deadline"] and (
        date.fromisoformat(o["deadline"]) - date.today()
    ).days <= 10 and (
        date.fromisoformat(o["deadline"]) - date.today()
    ).days >= 0]

    for user in users:
        for opp in urgent_opps[:3]:
            days = (date.fromisoformat(opp["deadline"]) - date.today()).days
            notifs.append({
                "notification_id": uid(),
                "user_id": user["user_id"],
                "opportunity_id": opp["id"],
                "message": f"⏰ Deadline in {days} day(s): \"{opp['title']}\" — don't miss it!",
                "status": "unread" if random.random() > 0.4 else "read",
                "timestamp": (NOW - timedelta(hours=random.randint(1, 48))).isoformat(),
            })

        # Generic recommendation notification
        notifs.append({
            "notification_id": uid(),
            "user_id": user["user_id"],
            "opportunity_id": random.choice(opps)["id"],
            "message": f"🎯 New opportunities matching your profile are available — check your dashboard!",
            "status": "unread",
            "timestamp": (NOW - timedelta(hours=random.randint(1, 6))).isoformat(),
        })

    return notifs


# ── DATABASE SEEDER ────────────────────────────────────────────────────────────

async def seed():
    print("\n🌱  Seeding mock data into:", DB_PATH)
    print("=" * 55)

    async with aiosqlite.connect(DB_PATH) as db:

        # ── 1. Create tables (SQLite-compatible DDL) ────────────────────────
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            skills_required TEXT DEFAULT '[]',
            location TEXT,
            eligibility TEXT,
            deadline TEXT,
            source TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            cluster_id INTEGER,
            cluster_label TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            skills TEXT DEFAULT '[]',
            interests TEXT DEFAULT '[]',
            level TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS recommendations (
            recommendation_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            opportunity_id TEXT NOT NULL,
            score REAL NOT NULL,
            match_reasons TEXT DEFAULT '[]',
            created_at TEXT NOT NULL,
            UNIQUE(user_id, opportunity_id)
        );

        CREATE TABLE IF NOT EXISTS notifications (
            notification_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            opportunity_id TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'unread',
            timestamp TEXT NOT NULL
        );
        """)

        # ── 2. Clear existing data ──────────────────────────────────────────
        for table in ["notifications", "recommendations", "opportunities", "users"]:
            await db.execute(f"DELETE FROM {table}")
        await db.commit()
        print("✅  Cleared existing data")

        # ── 3. Insert opportunities ─────────────────────────────────────────
        for opp in OPPORTUNITIES:
            await db.execute("""
                INSERT INTO opportunities VALUES
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                opp["id"], opp["title"], opp["type"], opp["category"],
                opp["description"], opp["skills_required"],
                opp["location"], opp["eligibility"], opp["deadline"],
                opp["source"], opp["url"],
                opp.get("cluster_id"), opp.get("cluster_label"),
                ts(), ts()
            ))
        await db.commit()
        print(f"✅  Inserted {len(OPPORTUNITIES)} opportunities")

        # ── 4. Insert users ─────────────────────────────────────────────────
        for user in USERS:
            await db.execute("""
                INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                user["user_id"], user["name"], user["email"],
                user["hashed_password"], user["skills"],
                user["interests"], user["level"], ts(), ts()
            ))
        await db.commit()
        print(f"✅  Inserted {len(USERS)} users")
        for u in USERS:
            print(f"    👤 {u['name']} ({u['email']}) — level: {u['level']}")

        # ── 5. Generate and insert recommendations ──────────────────────────
        print("\n🤖  Running ML recommender to generate personalized recommendations...")
        recs = build_recommendations(OPPORTUNITIES, USERS)
        for rec in recs:
            try:
                await db.execute("""
                    INSERT OR IGNORE INTO recommendations VALUES (?,?,?,?,?,?)
                """, (
                    rec["recommendation_id"], rec["user_id"],
                    rec["opportunity_id"], rec["score"],
                    rec["match_reasons"], rec["created_at"]
                ))
            except Exception as e:
                pass
        await db.commit()
        print(f"✅  Generated {len(recs)} recommendations across {len(USERS)} users")

        # ── 6. Insert notifications ─────────────────────────────────────────
        notifs = build_notifications(OPPORTUNITIES, USERS)
        for notif in notifs:
            await db.execute("""
                INSERT INTO notifications VALUES (?,?,?,?,?,?)
            """, (
                notif["notification_id"], notif["user_id"],
                notif["opportunity_id"], notif["message"],
                notif["status"], notif["timestamp"]
            ))
        await db.commit()
        print(f"✅  Generated {len(notifs)} notifications")

        # ── 7. Summary stats ────────────────────────────────────────────────
        print("\n📊  Database summary:")
        for table in ["opportunities", "users", "recommendations", "notifications"]:
            row = await db.execute(f"SELECT COUNT(*) FROM {table}")
            count = (await row.fetchone())[0]
            print(f"    {table:20s}: {count:3d} rows")

        # Stats by type
        row = await db.execute("SELECT type, COUNT(*) FROM opportunities GROUP BY type")
        print("\n    Opportunities by type:")
        for r in await row.fetchall():
            print(f"      {r[0]:20s}: {r[1]} items")

    print("\n🎉  Seeding complete!")
    print(f"    DB: {DB_PATH}")
    print("\n    Demo login credentials:")
    print("    ┌────────────────────────────────────────────────────┐")
    for u in USERS:
        print(f"    │  {u['email']:30s}  Password123!  │")
    print("    └────────────────────────────────────────────────────┘\n")


if __name__ == "__main__":
    asyncio.run(seed())
