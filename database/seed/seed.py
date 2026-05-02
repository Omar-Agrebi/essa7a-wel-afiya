"""
database/seed/seed.py
─────────────────────────────────────────────────────────────────────────────
Seed script for the Intelligent University Observatory.

Populates the database with:
  • 4 test users  (one per academic level)
  • 20 internships, 15 scholarships, 10 projects, 15 certifications
  • Recommendations + notifications wired to the test users

Run modes
---------
  python -m database.seed.seed              # idempotent — skips existing rows
  python -m database.seed.seed --wipe       # drops and re-inserts everything

Requirements
------------
  • DATABASE_URL must be set in .env (or exported as env var)
  • Alembic migrations must already have been applied
  • Python 3.11+, SQLAlchemy 2.0 async, asyncpg

Usage from project root
-----------------------
  python -m database.seed.seed
  python -m database.seed.seed --wipe
"""

from __future__ import annotations

import argparse
import asyncio
import uuid
from datetime import date, datetime, timedelta
from typing import Any

from passlib.context import CryptContext
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ── internal imports ────────────────────────────────────────────────────────
from app.core.config import settings
from app.models.notification import Notification, NotificationStatus
from app.models.opportunity import Opportunity, OpportunityCategory, OpportunityType
from app.models.recommendation import Recommendation
from app.models.user import AcademicLevel, User

# ── helpers ─────────────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TODAY = date.today()


def _days(n: int) -> date:
    """Return a date n days from today (negative = past)."""
    return TODAY + timedelta(days=n)


def _uuid() -> str:
    return str(uuid.uuid4())


# ═══════════════════════════════════════════════════════════════════════════
# USERS
# ═══════════════════════════════════════════════════════════════════════════

USERS: list[dict[str, Any]] = [
    {
        "user_id": "11111111-1111-1111-1111-111111111111",
        "name": "Amira Belhaj",
        "email": "amira@observatory.test",
        "hashed_password": pwd_context.hash("Password123!"),
        "skills": ["Python", "PyTorch", "NLP", "scikit-learn", "Docker"],
        "interests": ["NLP", "AI"],
        "level": AcademicLevel.master,
    },
    {
        "user_id": "22222222-2222-2222-2222-222222222222",
        "name": "Youssef Gharbi",
        "email": "youssef@observatory.test",
        "hashed_password": pwd_context.hash("Password123!"),
        "skills": ["Python", "SQL", "TensorFlow", "R", "Spark"],
        "interests": ["Data Science", "AI"],
        "level": AcademicLevel.phd,
    },
    {
        "user_id": "33333333-3333-3333-3333-333333333333",
        "name": "Sofia Mancini",
        "email": "sofia@observatory.test",
        "hashed_password": pwd_context.hash("Password123!"),
        "skills": ["Python", "computer vision", "PyTorch", "Docker", "Kubernetes"],
        "interests": ["AI", "Software Engineering"],
        "level": AcademicLevel.bachelor,
    },
    {
        "user_id": "44444444-4444-4444-4444-444444444444",
        "name": "Lars Müller",
        "email": "lars@observatory.test",
        "hashed_password": pwd_context.hash("Password123!"),
        "skills": ["Python", "MLOps", "Docker", "Kubernetes", "Hugging Face", "Julia"],
        "interests": ["AI", "Data Science"],
        "level": AcademicLevel.professional,
    },
]

# ═══════════════════════════════════════════════════════════════════════════
# OPPORTUNITIES
# ═══════════════════════════════════════════════════════════════════════════

# fmt: off
OPPORTUNITIES: list[dict[str, Any]] = [

    # ── INTERNSHIPS (20) ──────────────────────────────────────────────────

    {
        "id": _uuid(), "title": "Machine Learning Intern — Computer Vision",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.AI,
        "description": (
            "Join Airbus's AI lab in Toulouse to develop computer vision models "
            "for satellite image analysis. You will work on object detection pipelines "
            "using PyTorch and integrate models into production inference services."
        ),
        "skills_required": ["Python", "PyTorch", "computer vision", "Docker"],
        "location": "Toulouse, France",
        "eligibility": "Master or PhD students in Computer Science or AI",
        "deadline": _days(45),
        "source": "LinkedIn",
        "url": "https://jobs.airbus.com/intern-cv-2025",
        "cluster_id": 0, "cluster_label": "Computer Vision & Robotics",
    },
    {
        "id": _uuid(), "title": "NLP Research Intern",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.AI,
        "description": (
            "Work with INRIA's NLP team on large language model fine-tuning and "
            "evaluation benchmarks. Involves dataset curation, model training, and "
            "scientific writing."
        ),
        "skills_required": ["Python", "NLP", "PyTorch", "Hugging Face"],
        "location": "Paris, France",
        "eligibility": "Master students — AI or Computational Linguistics",
        "deadline": _days(30),
        "source": "Indeed",
        "url": "https://jobs.inria.fr/nlp-intern-2025",
        "cluster_id": 1, "cluster_label": "NLP & Language Models",
    },
    {
        "id": _uuid(), "title": "Data Science Intern — Energy Forecasting",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.data_science,
        "description": (
            "TotalEnergies is looking for a data science intern to build predictive "
            "models for energy demand forecasting using time-series analysis and "
            "regression techniques."
        ),
        "skills_required": ["Python", "scikit-learn", "SQL", "R"],
        "location": "Paris, France",
        "eligibility": "Bachelor or Master students — Data Science or Statistics",
        "deadline": _days(60),
        "source": "LinkedIn",
        "url": "https://careers.totalenergies.com/ds-intern-2025",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "AI Software Engineer Intern",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.software_engineering,
        "description": (
            "Dassault Systèmes seeks a software engineering intern to integrate AI "
            "modules into 3D simulation software. Python, REST APIs, and Docker "
            "experience required."
        ),
        "skills_required": ["Python", "Docker", "scikit-learn", "SQL"],
        "location": "Vélizy-Villacoublay, France",
        "eligibility": "Bachelor or Master — Software Engineering or CS",
        "deadline": _days(55),
        "source": "LinkedIn",
        "url": "https://careers.3ds.com/ai-swe-intern-2025",
        "cluster_id": 3, "cluster_label": "Software Engineering & MLOps",
    },
    {
        "id": _uuid(), "title": "Reinforcement Learning Research Intern",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.AI,
        "description": (
            "DeepMind London opens a research internship in reinforcement learning "
            "for game environments and robotics. Strong background in RL algorithms "
            "and Python required."
        ),
        "skills_required": ["Python", "reinforcement learning", "PyTorch", "TensorFlow"],
        "location": "London, UK",
        "eligibility": "PhD or advanced Master students",
        "deadline": _days(90),
        "source": "LinkedIn",
        "url": "https://deepmind.com/careers/intern-rl-2025",
        "cluster_id": 0, "cluster_label": "Computer Vision & Robotics",
    },
    {
        "id": _uuid(), "title": "MLOps Intern — Production AI Systems",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.AI,
        "description": (
            "Capgemini Engineering offers an MLOps internship focused on building "
            "CI/CD pipelines for machine learning models. Kubernetes, Docker, and "
            "monitoring tools are key technologies."
        ),
        "skills_required": ["Python", "MLOps", "Docker", "Kubernetes"],
        "location": "Paris, France",
        "eligibility": "Master students — AI, MLOps, or DevOps",
        "deadline": _days(40),
        "source": "Indeed",
        "url": "https://capgemini.jobs/mlops-intern-2025",
        "cluster_id": 3, "cluster_label": "Software Engineering & MLOps",
    },
    {
        "id": _uuid(), "title": "Data Engineering Intern — Big Data Pipelines",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.data_science,
        "description": (
            "Siemens AG offers a data engineering internship in Berlin building "
            "scalable ETL pipelines using Apache Spark and cloud storage. "
            "SQL and Python fluency required."
        ),
        "skills_required": ["Python", "Spark", "SQL", "Docker"],
        "location": "Berlin, Germany",
        "eligibility": "Bachelor or Master — Data Engineering or CS",
        "deadline": _days(50),
        "source": "LinkedIn",
        "url": "https://siemens.com/careers/data-eng-intern-2025",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "Computer Vision Intern — Space Imaging",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.AI,
        "description": (
            "The European Space Agency (ESA) is recruiting a CV intern to work on "
            "satellite image segmentation. PyTorch, OpenCV, and Python required."
        ),
        "skills_required": ["Python", "computer vision", "PyTorch", "scikit-learn"],
        "location": "Noordwijk, Netherlands",
        "eligibility": "Master or PhD — AI, Remote Sensing, or CS",
        "deadline": _days(35),
        "source": "LinkedIn",
        "url": "https://esa.int/careers/cv-intern-2025",
        "cluster_id": 0, "cluster_label": "Computer Vision & Robotics",
    },
    {
        "id": _uuid(), "title": "Research Intern — Knowledge Graphs and NLP",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.AI,
        "description": (
            "Max Planck Institute for Intelligent Systems seeks an intern to build "
            "knowledge graph extraction pipelines from scientific text using spaCy "
            "and transformer-based NER models."
        ),
        "skills_required": ["Python", "NLP", "PyTorch", "Hugging Face"],
        "location": "Tübingen, Germany",
        "eligibility": "Master or PhD students",
        "deadline": _days(70),
        "source": "ResearchGate",
        "url": "https://mpi-is.mpg.de/intern-kg-nlp-2025",
        "cluster_id": 1, "cluster_label": "NLP & Language Models",
    },
    {
        "id": _uuid(), "title": "AI Intern — Healthcare Diagnostics",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.AI,
        "description": (
            "WHO Innovation Lab invites an AI intern to build diagnostic support tools "
            "using medical imaging datasets and deep learning classification models."
        ),
        "skills_required": ["Python", "TensorFlow", "computer vision", "scikit-learn"],
        "location": "Geneva, Switzerland",
        "eligibility": "Master or PhD — AI, Biomedical Informatics",
        "deadline": _days(80),
        "source": "LinkedIn",
        "url": "https://who.int/careers/ai-intern-2025",
        "cluster_id": 0, "cluster_label": "Computer Vision & Robotics",
    },
    {
        "id": _uuid(), "title": "Data Science Intern — Climate Analytics",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.data_science,
        "description": (
            "UNESCO World Heritage Centre is looking for a data science intern to "
            "analyse climate risk data and build predictive dashboards for heritage "
            "site protection decisions."
        ),
        "skills_required": ["Python", "R", "SQL", "scikit-learn"],
        "location": "Paris, France",
        "eligibility": "Master students — Data Science or Environmental Science",
        "deadline": _days(25),
        "source": "Indeed",
        "url": "https://unesco.org/careers/ds-intern-2025",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "Backend ML Intern — Recommendation Systems",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.software_engineering,
        "description": (
            "Thales Group offers a backend engineering internship to build and evaluate "
            "recommendation system APIs using FastAPI and collaborative filtering models."
        ),
        "skills_required": ["Python", "scikit-learn", "SQL", "Docker"],
        "location": "Paris, France",
        "eligibility": "Bachelor or Master — CS or Software Engineering",
        "deadline": _days(6),  # near expiry — for notification testing
        "source": "LinkedIn",
        "url": "https://thalesgroup.com/careers/recsys-intern-2025",
        "cluster_id": 3, "cluster_label": "Software Engineering & MLOps",
    },
    {
        "id": _uuid(), "title": "AI Ethics & Policy Research Intern",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.AI,
        "description": (
            "KU Leuven Centre for AI & Society is hiring a research intern to assess "
            "fairness, bias, and transparency in machine learning systems used in "
            "public sector decision-making."
        ),
        "skills_required": ["Python", "scikit-learn", "NLP"],
        "location": "Leuven, Belgium",
        "eligibility": "Master or PhD — AI, Law, or Political Science",
        "deadline": _days(120),
        "source": "University Portal",
        "url": "https://kuleuven.be/careers/ai-ethics-intern-2025",
        "cluster_id": 1, "cluster_label": "NLP & Language Models",
    },
    {
        "id": _uuid(), "title": "NLP Engineer Intern — Multilingual Systems",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.AI,
        "description": (
            "CERN's knowledge management team needs an NLP intern to develop "
            "multilingual information retrieval and summarisation tools for scientific "
            "literature."
        ),
        "skills_required": ["Python", "NLP", "Hugging Face", "PyTorch"],
        "location": "Geneva, Switzerland",
        "eligibility": "Master or PhD — CS, Computational Linguistics",
        "deadline": _days(75),
        "source": "LinkedIn",
        "url": "https://careers.cern.ch/nlp-intern-2025",
        "cluster_id": 1, "cluster_label": "NLP & Language Models",
    },
    {
        "id": _uuid(), "title": "Cybersecurity ML Intern — Threat Detection",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.cybersecurity,
        "description": (
            "Thales Cybersecurity division recruits an ML intern to develop anomaly "
            "detection models for network intrusion detection using Python and "
            "scikit-learn."
        ),
        "skills_required": ["Python", "scikit-learn", "SQL"],
        "location": "Paris, France",
        "eligibility": "Master students — Cybersecurity or Data Science",
        "deadline": _days(48),
        "source": "Indeed",
        "url": "https://thalesgroup.com/careers/cyber-ml-intern-2025",
        "cluster_id": 4, "cluster_label": "Cybersecurity & Anomaly Detection",
    },
    {
        "id": _uuid(), "title": "Full-Stack ML Intern — Explainable AI",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.AI,
        "description": (
            "ETH Zurich AI Center opens a full-stack research internship developing "
            "web interfaces for exploring explainable AI model outputs, using React "
            "and FastAPI with SHAP/LIME visualisations."
        ),
        "skills_required": ["Python", "scikit-learn", "Docker", "SQL"],
        "location": "Zurich, Switzerland",
        "eligibility": "Master or PhD — CS or AI",
        "deadline": _days(62),
        "source": "University Portal",
        "url": "https://ai.ethz.ch/careers/xai-intern-2025",
        "cluster_id": 3, "cluster_label": "Software Engineering & MLOps",
    },
    {
        "id": _uuid(), "title": "Speech & Audio ML Intern",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.AI,
        "description": (
            "University of Amsterdam Deep Learning Lab seeks an intern to develop "
            "speech recognition and audio classification models using PyTorch and "
            "torchaudio."
        ),
        "skills_required": ["Python", "PyTorch", "TensorFlow"],
        "location": "Amsterdam, Netherlands",
        "eligibility": "Master or PhD — AI or Signal Processing",
        "deadline": _days(88),
        "source": "ResearchGate",
        "url": "https://uva.nl/careers/speech-intern-2025",
        "cluster_id": 0, "cluster_label": "Computer Vision & Robotics",
    },
    {
        "id": _uuid(), "title": "Data Analytics Intern — Supply Chain",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.data_science,
        "description": (
            "Capgemini Invent Brussels offers a data analytics internship to optimise "
            "supply chain decisions using SQL, Python, and business intelligence tools."
        ),
        "skills_required": ["Python", "SQL", "R"],
        "location": "Brussels, Belgium",
        "eligibility": "Bachelor or Master — Data Analytics or Business Informatics",
        "deadline": _days(5),  # near expiry
        "source": "Indeed",
        "url": "https://capgemini.com/careers/analytics-intern-2025",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "Scientific Computing Intern — Julia & ML",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.AI,
        "description": (
            "EPFL Computational Science Lab offers an internship in scientific ML "
            "using Julia and Python for physics-informed neural networks."
        ),
        "skills_required": ["Julia", "Python", "PyTorch"],
        "location": "Lausanne, Switzerland",
        "eligibility": "Master or PhD — Applied Mathematics, CS, or Physics",
        "deadline": _days(100),
        "source": "University Portal",
        "url": "https://epfl.ch/labs/csml-intern-2025",
        "cluster_id": 0, "cluster_label": "Computer Vision & Robotics",
    },
    {
        "id": _uuid(), "title": "Generative AI Intern — Text-to-Image Research",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.AI,
        "description": (
            "Sorbonne University & CNRS joint internship on diffusion model training "
            "and evaluation for text-to-image generation. PyTorch and Hugging Face "
            "experience expected."
        ),
        "skills_required": ["Python", "PyTorch", "Hugging Face", "computer vision"],
        "location": "Paris, France",
        "eligibility": "Master or PhD — Deep Learning or AI",
        "deadline": _days(-10),  # expired — for robustness testing
        "source": "LinkedIn",
        "url": "https://sorbonne.fr/careers/genai-intern-2025",
        "cluster_id": 0, "cluster_label": "Computer Vision & Robotics",
    },

    # ── SCHOLARSHIPS (15) ─────────────────────────────────────────────────

    {
        "id": _uuid(), "title": "DAAD Research Grant — AI & Data Science",
        "type": OpportunityType.scholarship,
        "category": OpportunityCategory.AI,
        "description": (
            "DAAD offers research scholarships for international students and researchers "
            "to pursue AI and Data Science projects at German universities. Covers tuition, "
            "monthly stipend, and travel costs."
        ),
        "skills_required": ["Python", "scikit-learn", "SQL"],
        "location": "Germany",
        "eligibility": "Bachelor, Master, or PhD — any STEM field",
        "deadline": _days(90),
        "source": "DAAD",
        "url": "https://daad.de/scholarships/ai-data-science-2025",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "Erasmus+ Scholarship — Digital Innovation Track",
        "type": OpportunityType.scholarship,
        "category": OpportunityCategory.AI,
        "description": (
            "Erasmus+ digital innovation mobility grants for students pursuing "
            "semester or full-degree programmes in AI, Data Science, or Cybersecurity "
            "across EU member states."
        ),
        "skills_required": ["Python"],
        "location": "Europe (multiple)",
        "eligibility": "Bachelor or Master students enrolled in EU universities",
        "deadline": _days(60),
        "source": "Erasmus+",
        "url": "https://erasmus-plus.ec.europa.eu/scholarships/digital-2025",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "Eiffel Excellence Scholarship — France",
        "type": OpportunityType.scholarship,
        "category": OpportunityCategory.AI,
        "description": (
            "French government scholarship for high-achieving international students "
            "from partner countries including Tunisia. Funds Master and PhD studies "
            "in French institutions. Full stipend + accommodation."
        ),
        "skills_required": [],
        "location": "France",
        "eligibility": "Students from partner countries — Master or PhD",
        "deadline": _days(45),
        "source": "Campus France",
        "url": "https://campusfrance.org/eiffel-scholarship-2025",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "Marie Curie Individual Fellowship — AI Research",
        "type": OpportunityType.scholarship,
        "category": OpportunityCategory.AI,
        "description": (
            "Marie Skłodowska-Curie Actions individual fellowships for postdoctoral "
            "AI researchers to conduct research at European host institutions. "
            "Prestigious and highly competitive EU funding."
        ),
        "skills_required": ["Python", "PyTorch", "TensorFlow"],
        "location": "Europe (any country)",
        "eligibility": "Postdoctoral researchers — up to 8 years post-PhD",
        "deadline": _days(120),
        "source": "Horizon Europe",
        "url": "https://marie-sklodowska-curie-actions.ec.europa.eu/calls/2025",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "EPFL Excellence Fellowship — Master's Programme",
        "type": OpportunityType.scholarship,
        "category": OpportunityCategory.AI,
        "description": (
            "Full merit scholarship for outstanding Bachelor graduates to pursue "
            "an EPFL Master's programme in Computer Science, Data Science, or AI. "
            "Covers tuition and living allowance."
        ),
        "skills_required": ["Python", "mathematics"],
        "location": "Lausanne, Switzerland",
        "eligibility": "Bachelor graduates — top academic record required",
        "deadline": _days(150),
        "source": "ScholarshipPortal",
        "url": "https://epfl.ch/education/master/excellence-fellowship-2025",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "ETH Zurich Excellence Scholarship",
        "type": OpportunityType.scholarship,
        "category": OpportunityCategory.AI,
        "description": (
            "ETH Zurich awards excellence scholarships to top international "
            "Master's students in CS, AI, and Data Science. Competitive stipend "
            "and mentorship programme included."
        ),
        "skills_required": ["Python"],
        "location": "Zurich, Switzerland",
        "eligibility": "Bachelor graduates applying for ETH Master's programmes",
        "deadline": _days(75),
        "source": "ScholarshipPortal",
        "url": "https://ethz.ch/students/en/masters/excellence-scholarship-2025.html",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "DAAD EPOS Scholarship — Tunisia Priority",
        "type": OpportunityType.scholarship,
        "category": OpportunityCategory.data_science,
        "description": (
            "DAAD EPOS development-related postgraduate courses scholarship, "
            "prioritising applicants from Tunisia and other North African countries "
            "for studies in Data Science and IT management in Germany."
        ),
        "skills_required": ["Python", "SQL"],
        "location": "Germany",
        "eligibility": "Bachelor graduates from Tunisia, Morocco, or Algeria",
        "deadline": _days(55),
        "source": "DAAD",
        "url": "https://daad.de/epos-scholarship-north-africa-2025",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "Sorbonne University International Scholarship",
        "type": OpportunityType.scholarship,
        "category": OpportunityCategory.AI,
        "description": (
            "Sorbonne offers partial tuition scholarships to international Master's "
            "students in Artificial Intelligence and Cognitive Science. Includes "
            "French language support and integration programme."
        ),
        "skills_required": ["Python", "NLP"],
        "location": "Paris, France",
        "eligibility": "Bachelor graduates worldwide",
        "deadline": _days(6),  # near expiry
        "source": "University Portal",
        "url": "https://sorbonne.fr/scholarships/international-ai-2025",
        "cluster_id": 1, "cluster_label": "NLP & Language Models",
    },
    {
        "id": _uuid(), "title": "KU Leuven Doctoral Fellowship — Machine Learning",
        "type": OpportunityType.scholarship,
        "category": OpportunityCategory.AI,
        "description": (
            "Fully funded PhD fellowship at KU Leuven in the area of interpretable "
            "machine learning and Bayesian methods. Four-year stipend, travel, and "
            "publication budget included."
        ),
        "skills_required": ["Python", "scikit-learn", "R", "TensorFlow"],
        "location": "Leuven, Belgium",
        "eligibility": "Master graduates — GPA ≥ 3.5/4.0",
        "deadline": _days(100),
        "source": "ResearchGate",
        "url": "https://kuleuven.be/research/phd-ml-fellowship-2025",
        "cluster_id": 0, "cluster_label": "Computer Vision & Robotics",
    },
    {
        "id": _uuid(), "title": "Google PhD Fellowship — Machine Learning",
        "type": OpportunityType.scholarship,
        "category": OpportunityCategory.AI,
        "description": (
            "Google's PhD fellowship programme supports outstanding PhD students "
            "doing exceptional and innovative research in ML, NLP, and related "
            "fields. Comes with a stipend and Google mentorship."
        ),
        "skills_required": ["Python", "PyTorch", "TensorFlow", "NLP"],
        "location": "Remote / International",
        "eligibility": "PhD students in CS, AI, or Statistics — any country",
        "deadline": _days(85),
        "source": "Google Research",
        "url": "https://research.google/outreach/phd-fellowship-2025",
        "cluster_id": 1, "cluster_label": "NLP & Language Models",
    },
    {
        "id": _uuid(), "title": "TU Berlin International Master's Scholarship",
        "type": OpportunityType.scholarship,
        "category": OpportunityCategory.data_science,
        "description": (
            "TU Berlin awards merit-based scholarships for international Master's "
            "students in Data Science and Computer Engineering. Monthly stipend "
            "and housing allowance included."
        ),
        "skills_required": ["Python", "SQL", "mathematics"],
        "location": "Berlin, Germany",
        "eligibility": "Bachelor graduates — strong academic record",
        "deadline": _days(40),
        "source": "ScholarshipPortal",
        "url": "https://tu.berlin/scholarships/master-ds-2025",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "Amsterdam UvA Data Science Fellowship",
        "type": OpportunityType.scholarship,
        "category": OpportunityCategory.data_science,
        "description": (
            "University of Amsterdam doctoral research fellowship in data science, "
            "focusing on probabilistic methods and causal inference. Full funding "
            "for four years."
        ),
        "skills_required": ["Python", "R", "scikit-learn", "Spark"],
        "location": "Amsterdam, Netherlands",
        "eligibility": "Master graduates in statistics, CS, or AI",
        "deadline": _days(110),
        "source": "University Portal",
        "url": "https://uva.nl/research/fellowships/ds-causal-2025",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "Politecnico di Milano AI Doctoral Scholarship",
        "type": OpportunityType.scholarship,
        "category": OpportunityCategory.AI,
        "description": (
            "Fully funded PhD scholarship at Politecnico di Milano in Artificial "
            "Intelligence applied to industrial automation and smart manufacturing. "
            "Collaboration with Siemens Italy."
        ),
        "skills_required": ["Python", "TensorFlow", "Docker"],
        "location": "Milan, Italy",
        "eligibility": "Master graduates — AI, Robotics, or Control Systems",
        "deadline": _days(130),
        "source": "ResearchGate",
        "url": "https://polimi.it/dottorato/ai-phd-scholarship-2025",
        "cluster_id": 0, "cluster_label": "Computer Vision & Robotics",
    },
    {
        "id": _uuid(), "title": "Campus France — Maghreb Excellence Award",
        "type": OpportunityType.scholarship,
        "category": OpportunityCategory.AI,
        "description": (
            "Campus France's excellence programme for top students from Tunisia, "
            "Morocco, and Algeria to pursue Master's degrees in AI and Data Science "
            "at selected French universities."
        ),
        "skills_required": ["Python"],
        "location": "France",
        "eligibility": "Bachelor graduates from Tunisia, Morocco, Algeria — top 10%",
        "deadline": _days(50),
        "source": "Campus France",
        "url": "https://campusfrance.org/maghreb-excellence-2025",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "Horizon Europe — MSCA Doctoral Network Grant",
        "type": OpportunityType.scholarship,
        "category": OpportunityCategory.AI,
        "description": (
            "Horizon Europe Marie Curie Doctoral Network on Trustworthy AI invites "
            "applications for 12 fully funded PhD positions across 8 European "
            "universities. Focus: explainability, robustness, fairness."
        ),
        "skills_required": ["Python", "scikit-learn", "PyTorch"],
        "location": "Europe (multiple countries)",
        "eligibility": "Master graduates — max 4 years since degree",
        "deadline": _days(95),
        "source": "Horizon Europe",
        "url": "https://horizon-europe.eu/msca-doctoral-trustworthy-ai-2025",
        "cluster_id": 0, "cluster_label": "Computer Vision & Robotics",
    },

    # ── PROJECTS (10) ─────────────────────────────────────────────────────

    {
        "id": _uuid(), "title": "Horizon Europe — RESILIENT AI for Smart Grids",
        "type": OpportunityType.project,
        "category": OpportunityCategory.AI,
        "description": (
            "Collaborative H2020/Horizon Europe project developing resilient AI "
            "for smart energy grid management. Open call for university partners "
            "to contribute ML and optimisation components."
        ),
        "skills_required": ["Python", "TensorFlow", "reinforcement learning", "Julia"],
        "location": "Remote / Europe",
        "eligibility": "University research groups or postdoc researchers",
        "deadline": _days(180),
        "source": "Horizon Europe",
        "url": "https://ec.europa.eu/info/horizon/resilient-ai-smartgrid-2025",
        "cluster_id": 0, "cluster_label": "Computer Vision & Robotics",
    },
    {
        "id": _uuid(), "title": "Google Research — Open Source NLP Benchmark Project",
        "type": OpportunityType.project,
        "category": OpportunityCategory.AI,
        "description": (
            "Google Research invites academic collaborators for an open-source NLP "
            "benchmark development initiative. Participants contribute dataset "
            "curation, evaluation scripts, and model baselines."
        ),
        "skills_required": ["Python", "NLP", "PyTorch", "Hugging Face"],
        "location": "Remote",
        "eligibility": "PhD students or postdocs in NLP or ML",
        "deadline": _days(60),
        "source": "Google Research",
        "url": "https://research.google/programs/nlp-benchmark-2025",
        "cluster_id": 1, "cluster_label": "NLP & Language Models",
    },
    {
        "id": _uuid(), "title": "ResearchGate — Federated Learning for Healthcare",
        "type": OpportunityType.project,
        "category": OpportunityCategory.AI,
        "description": (
            "EU-funded collaborative project building federated learning infrastructure "
            "for privacy-preserving medical data analysis across six European hospitals."
        ),
        "skills_required": ["Python", "TensorFlow", "PyTorch", "Docker"],
        "location": "Remote / Europe",
        "eligibility": "PhD or postdoc researchers — AI, Privacy, Healthcare IT",
        "deadline": _days(90),
        "source": "ResearchGate",
        "url": "https://researchgate.net/project/federated-learning-healthcare-2025",
        "cluster_id": 3, "cluster_label": "Software Engineering & MLOps",
    },
    {
        "id": _uuid(), "title": "Horizon Europe — CyberAI: ML-Driven Threat Intelligence",
        "type": OpportunityType.project,
        "category": OpportunityCategory.cybersecurity,
        "description": (
            "Horizon Europe CyberAI project developing machine learning models for "
            "real-time cyber threat intelligence. Seeking researchers in anomaly "
            "detection and graph neural networks."
        ),
        "skills_required": ["Python", "scikit-learn", "PyTorch"],
        "location": "Remote / Europe",
        "eligibility": "PhD researchers or industry R&D teams",
        "deadline": _days(120),
        "source": "Horizon Europe",
        "url": "https://ec.europa.eu/info/horizon/cyberai-threat-2025",
        "cluster_id": 4, "cluster_label": "Cybersecurity & Anomaly Detection",
    },
    {
        "id": _uuid(), "title": "INRIA — Open Research Project: Multimodal AI",
        "type": OpportunityType.project,
        "category": OpportunityCategory.AI,
        "description": (
            "INRIA opens collaborative research positions within its multimodal AI "
            "project combining vision and language for robotics navigation. "
            "Welcomes visiting researchers and PhD co-supervisors."
        ),
        "skills_required": ["Python", "PyTorch", "computer vision", "NLP"],
        "location": "Paris, France",
        "eligibility": "Postdoc researchers or senior PhD students",
        "deadline": _days(75),
        "source": "ResearchGate",
        "url": "https://inria.fr/research/multimodal-ai-project-2025",
        "cluster_id": 0, "cluster_label": "Computer Vision & Robotics",
    },
    {
        "id": _uuid(), "title": "Horizon Europe — DATATRUST: Data Governance for AI",
        "type": OpportunityType.project,
        "category": OpportunityCategory.data_science,
        "description": (
            "DATATRUST is a Horizon Europe project designing data governance frameworks "
            "for trustworthy AI systems in the public sector. Seeking researchers "
            "in data law, NLP, and policy analysis."
        ),
        "skills_required": ["Python", "SQL", "NLP"],
        "location": "Brussels, Belgium",
        "eligibility": "PhD or postdoc researchers — CS, Law, Policy",
        "deadline": _days(150),
        "source": "Horizon Europe",
        "url": "https://ec.europa.eu/info/horizon/datatrust-2025",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "Max Planck — Causal ML for Scientific Discovery",
        "type": OpportunityType.project,
        "category": OpportunityCategory.AI,
        "description": (
            "Max Planck Institute for Intelligent Systems opens a collaborative "
            "research project in causal representation learning applied to drug "
            "discovery and protein structure prediction."
        ),
        "skills_required": ["Python", "PyTorch", "R", "scikit-learn"],
        "location": "Tübingen, Germany",
        "eligibility": "Postdoc researchers — ML or Computational Biology",
        "deadline": _days(200),
        "source": "ResearchGate",
        "url": "https://mpi-is.mpg.de/projects/causal-ml-science-2025",
        "cluster_id": 0, "cluster_label": "Computer Vision & Robotics",
    },
    {
        "id": _uuid(), "title": "ESA — AI for Earth Observation Data Mining",
        "type": OpportunityType.project,
        "category": OpportunityCategory.data_science,
        "description": (
            "European Space Agency collaborative project using AI and big data tools "
            "to mine ESA's Earth observation archive for climate and disaster "
            "monitoring insights. Open call for academic partners."
        ),
        "skills_required": ["Python", "TensorFlow", "Spark", "SQL"],
        "location": "Remote / Noordwijk",
        "eligibility": "University research groups — RS, CS, or Environmental Science",
        "deadline": _days(110),
        "source": "Horizon Europe",
        "url": "https://esa.int/research/ai-earth-observation-2025",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "Horizon Europe — RobustNLP: Adversarial Robustness",
        "type": OpportunityType.project,
        "category": OpportunityCategory.AI,
        "description": (
            "RobustNLP is a multi-institution project studying adversarial robustness "
            "in large language models, with evaluation datasets and benchmark suites. "
            "Open to PhD and postdoc collaborators."
        ),
        "skills_required": ["Python", "NLP", "PyTorch", "Hugging Face"],
        "location": "Remote / Europe",
        "eligibility": "PhD students or postdocs — NLP or Security",
        "deadline": _days(85),
        "source": "Horizon Europe",
        "url": "https://ec.europa.eu/info/horizon/robustnlp-2025",
        "cluster_id": 1, "cluster_label": "NLP & Language Models",
    },
    {
        "id": _uuid(), "title": "CERN — Open Science ML Infrastructure Project",
        "type": OpportunityType.project,
        "category": OpportunityCategory.AI,
        "description": (
            "CERN invites research partners to contribute to its open science ML "
            "infrastructure project, building scalable ML pipelines for particle "
            "physics data analysis using Julia, Python, and HPC resources."
        ),
        "skills_required": ["Python", "Julia", "Docker", "Spark"],
        "location": "Geneva, Switzerland",
        "eligibility": "PhD or postdoc researchers — Physics, HPC, or ML",
        "deadline": _days(160),
        "source": "ResearchGate",
        "url": "https://research.cern.ch/open-science-ml-2025",
        "cluster_id": 3, "cluster_label": "Software Engineering & MLOps",
    },

    # ── CERTIFICATIONS (15) ───────────────────────────────────────────────
    # These supplement live Coursera API results.

    {
        "id": _uuid(), "title": "Deep Learning Specialisation — Coursera (deeplearning.ai)",
        "type": OpportunityType.course,
        "category": OpportunityCategory.AI,
        "description": (
            "Andrew Ng's flagship specialisation covering neural networks, CNNs, "
            "RNNs, and practical deep learning in TensorFlow. Industry gold standard "
            "for AI practitioners."
        ),
        "skills_required": ["Python", "TensorFlow", "scikit-learn"],
        "location": "Remote",
        "eligibility": None,
        "deadline": None,
        "source": "Coursera",
        "url": "https://coursera.org/specializations/deep-learning",
        "cluster_id": 0, "cluster_label": "Computer Vision & Robotics",
    },
    {
        "id": _uuid(), "title": "Natural Language Processing Specialisation — Coursera",
        "type": OpportunityType.course,
        "category": OpportunityCategory.AI,
        "description": (
            "Four-course NLP specialisation by deeplearning.ai covering sequence "
            "models, attention mechanisms, transformers, and real-world NLP applications."
        ),
        "skills_required": ["Python", "NLP", "TensorFlow"],
        "location": "Remote",
        "eligibility": None,
        "deadline": None,
        "source": "Coursera",
        "url": "https://coursera.org/specializations/natural-language-processing",
        "cluster_id": 1, "cluster_label": "NLP & Language Models",
    },
    {
        "id": _uuid(), "title": "MLOps Specialisation — Coursera (deeplearning.ai)",
        "type": OpportunityType.course,
        "category": OpportunityCategory.AI,
        "description": (
            "Covers ML project lifecycle, data management, model deployment, "
            "monitoring, and CI/CD for ML. Ideal for practitioners moving into "
            "production AI engineering."
        ),
        "skills_required": ["Python", "MLOps", "Docker"],
        "location": "Remote",
        "eligibility": None,
        "deadline": None,
        "source": "Coursera",
        "url": "https://coursera.org/specializations/machine-learning-engineering-for-production-mlops",
        "cluster_id": 3, "cluster_label": "Software Engineering & MLOps",
    },
    {
        "id": _uuid(), "title": "IBM Data Science Professional Certificate",
        "type": OpportunityType.course,
        "category": OpportunityCategory.data_science,
        "description": (
            "Comprehensive 10-course programme covering data analysis, SQL, Python, "
            "ML, and data visualisation. Designed for career starters in data science."
        ),
        "skills_required": ["Python", "SQL", "scikit-learn"],
        "location": "Remote",
        "eligibility": None,
        "deadline": None,
        "source": "Coursera",
        "url": "https://coursera.org/professional-certificates/ibm-data-science",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "Computer Vision with PyTorch — edX",
        "type": OpportunityType.course,
        "category": OpportunityCategory.AI,
        "description": (
            "Hands-on course on building computer vision systems using PyTorch: "
            "image classification, object detection, segmentation, and deployment "
            "on edge devices."
        ),
        "skills_required": ["Python", "PyTorch", "computer vision"],
        "location": "Remote",
        "eligibility": None,
        "deadline": None,
        "source": "edX",
        "url": "https://edx.org/course/computer-vision-pytorch",
        "cluster_id": 0, "cluster_label": "Computer Vision & Robotics",
    },
    {
        "id": _uuid(), "title": "Reinforcement Learning Specialisation — Coursera",
        "type": OpportunityType.course,
        "category": OpportunityCategory.AI,
        "description": (
            "University of Alberta specialisation on RL fundamentals: Markov Decision "
            "Processes, dynamic programming, temporal difference, and function "
            "approximation with Python."
        ),
        "skills_required": ["Python", "reinforcement learning", "scikit-learn"],
        "location": "Remote",
        "eligibility": None,
        "deadline": None,
        "source": "Coursera",
        "url": "https://coursera.org/specializations/reinforcement-learning",
        "cluster_id": 0, "cluster_label": "Computer Vision & Robotics",
    },
    {
        "id": _uuid(), "title": "Google Cloud Professional ML Engineer Certificate",
        "type": OpportunityType.course,
        "category": OpportunityCategory.AI,
        "description": (
            "Prepares for Google's Professional Machine Learning Engineer certification. "
            "Covers ML pipeline design, data preprocessing, training, evaluation, "
            "and deployment on Google Cloud."
        ),
        "skills_required": ["Python", "TensorFlow", "MLOps", "Docker"],
        "location": "Remote",
        "eligibility": None,
        "deadline": None,
        "source": "Coursera",
        "url": "https://coursera.org/professional-certificates/google-cloud-machine-learning-engineer",
        "cluster_id": 3, "cluster_label": "Software Engineering & MLOps",
    },
    {
        "id": _uuid(), "title": "Apache Spark and Big Data Processing — Coursera",
        "type": OpportunityType.course,
        "category": OpportunityCategory.data_science,
        "description": (
            "Covers distributed data processing with Apache Spark, including Spark SQL, "
            "streaming, and integration with ML pipelines. Python (PySpark) focused."
        ),
        "skills_required": ["Python", "Spark", "SQL"],
        "location": "Remote",
        "eligibility": None,
        "deadline": None,
        "source": "Coursera",
        "url": "https://coursera.org/learn/apache-spark-big-data",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "Cybersecurity and AI — Emerging Threats — edX",
        "type": OpportunityType.course,
        "category": OpportunityCategory.cybersecurity,
        "description": (
            "Applied course on using machine learning for cybersecurity: intrusion "
            "detection, malware classification, phishing detection, and adversarial "
            "ML attack defences."
        ),
        "skills_required": ["Python", "scikit-learn", "SQL"],
        "location": "Remote",
        "eligibility": None,
        "deadline": None,
        "source": "edX",
        "url": "https://edx.org/course/cybersecurity-ai-emerging-threats",
        "cluster_id": 4, "cluster_label": "Cybersecurity & Anomaly Detection",
    },
    {
        "id": _uuid(), "title": "Hugging Face NLP Course — Free Certification",
        "type": OpportunityType.course,
        "category": OpportunityCategory.AI,
        "description": (
            "Free official course from Hugging Face covering Transformers library, "
            "fine-tuning LLMs, building NLP pipelines, and deploying models to "
            "the Hub. Comes with a certificate of completion."
        ),
        "skills_required": ["Python", "NLP", "PyTorch", "Hugging Face"],
        "location": "Remote",
        "eligibility": None,
        "deadline": None,
        "source": "Hugging Face",
        "url": "https://huggingface.co/learn/nlp-course",
        "cluster_id": 1, "cluster_label": "NLP & Language Models",
    },
    {
        "id": _uuid(), "title": "Data Engineering Zoomcamp — DataTalks.Club",
        "type": OpportunityType.course,
        "category": OpportunityCategory.data_science,
        "description": (
            "Free intensive data engineering bootcamp covering containerisation, "
            "workflow orchestration, data warehousing, Spark, and Kafka. "
            "Hands-on projects and certificate on completion."
        ),
        "skills_required": ["Python", "Docker", "SQL", "Spark"],
        "location": "Remote",
        "eligibility": None,
        "deadline": _days(20),
        "source": "DataTalks.Club",
        "url": "https://datatalks.club/courses/data-engineering-zoomcamp.html",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "AWS Machine Learning Specialty Certificate — Udemy Prep",
        "type": OpportunityType.course,
        "category": OpportunityCategory.AI,
        "description": (
            "Comprehensive preparation course for the AWS Certified Machine Learning "
            "Specialty exam. Covers SageMaker, data engineering, model training, "
            "and evaluation on AWS."
        ),
        "skills_required": ["Python", "scikit-learn", "MLOps"],
        "location": "Remote",
        "eligibility": None,
        "deadline": None,
        "source": "Udemy",
        "url": "https://udemy.com/course/aws-machine-learning-a-complete-guide-with-labs",
        "cluster_id": 3, "cluster_label": "Software Engineering & MLOps",
    },
    {
        "id": _uuid(), "title": "Fast.ai Practical Deep Learning — Free Course",
        "type": OpportunityType.course,
        "category": OpportunityCategory.AI,
        "description": (
            "Top-down deep learning course teaching practitioners to train models "
            "on real-world tasks. Covers vision, NLP, and tabular data using the "
            "fastai library built on PyTorch."
        ),
        "skills_required": ["Python", "PyTorch"],
        "location": "Remote",
        "eligibility": None,
        "deadline": None,
        "source": "fast.ai",
        "url": "https://course.fast.ai",
        "cluster_id": 0, "cluster_label": "Computer Vision & Robotics",
    },
    {
        "id": _uuid(), "title": "Julia for Data Science — JuliaAcademy",
        "type": OpportunityType.course,
        "category": OpportunityCategory.data_science,
        "description": (
            "Official JuliaAcademy course on using Julia for high-performance "
            "numerical computing, data manipulation, and scientific ML. Free with "
            "certificate."
        ),
        "skills_required": ["Julia", "Python"],
        "location": "Remote",
        "eligibility": None,
        "deadline": None,
        "source": "JuliaAcademy",
        "url": "https://juliaacademy.com/p/julia-for-data-science",
        "cluster_id": 2, "cluster_label": "Data Science & Analytics",
    },
    {
        "id": _uuid(), "title": "Kubernetes for ML Engineers — Linux Foundation",
        "type": OpportunityType.course,
        "category": OpportunityCategory.software_engineering,
        "description": (
            "Linux Foundation training on deploying and scaling ML workloads using "
            "Kubernetes, Helm, and Kubeflow. Practical labs on GPU clusters and "
            "model serving."
        ),
        "skills_required": ["Docker", "Kubernetes", "Python", "MLOps"],
        "location": "Remote",
        "eligibility": None,
        "deadline": None,
        "source": "Linux Foundation",
        "url": "https://training.linuxfoundation.org/training/kubernetes-for-ml-engineers",
        "cluster_id": 3, "cluster_label": "Software Engineering & MLOps",
    },
]
# fmt: on

# ═══════════════════════════════════════════════════════════════════════════
# SEEDING LOGIC
# ═══════════════════════════════════════════════════════════════════════════


async def _wipe(session: AsyncSession) -> None:
    """Delete all seeded rows in dependency order."""
    print("  Wiping existing data…")
    for table in ("notifications", "recommendations", "opportunities", "users"):
        await session.execute(text(f"DELETE FROM {table}"))
    await session.commit()
    print("  Done.")


async def _seed_users(session: AsyncSession) -> dict[str, User]:
    """Insert users, skip if email already exists. Returns {email: User}."""
    inserted: dict[str, User] = {}
    for data in USERS:
        existing = await session.execute(
            select(User).where(User.email == data["email"])
        )
        user = existing.scalar_one_or_none()
        if user:
            print(f"  [skip] user {data['email']} already exists")
            inserted[data["email"]] = user
            continue
        user = User(**data)
        session.add(user)
        await session.flush()
        inserted[data["email"]] = user
        print(f"  [add]  user {data['email']}")
    return inserted


async def _seed_opportunities(session: AsyncSession) -> list[Opportunity]:
    """Insert opportunities, skip if url already exists. Returns inserted list."""
    inserted: list[Opportunity] = []
    for data in OPPORTUNITIES:
        existing = await session.execute(
            select(Opportunity).where(Opportunity.url == data["url"])
        )
        opp = existing.scalar_one_or_none()
        if opp:
            print(f"  [skip] opportunity {data['url'][:60]}…")
            inserted.append(opp)
            continue
        opp = Opportunity(**data)
        session.add(opp)
        await session.flush()
        inserted.append(opp)
        print(f"  [add]  {data['type'].value:14s}  {data['title'][:55]}")
    return inserted


async def _seed_recommendations(
    session: AsyncSession,
    users: dict[str, User],
    opportunities: list[Opportunity],
) -> None:
    """
    Create a small set of hand-crafted recommendations so the dashboard
    has data to display immediately without running the full ML pipeline.

    Wiring:
      amira   (master, NLP/AI)     → top NLP + AI internships / scholarships
      youssef (phd, Data Science)  → DS + research projects
      sofia   (bachelor, CV)       → CV internships + courses
      lars    (professional, MLOps)→ MLOps courses + projects
    """
    amira = users["amira@observatory.test"]
    youssef = users["youssef@observatory.test"]
    sofia = users["sofia@observatory.test"]
    lars = users["lars@observatory.test"]

    # Build url-keyed lookup
    opp_by_url: dict[str, Opportunity] = {o.url: o for o in opportunities}

    def _pick(url: str) -> Opportunity | None:
        return opp_by_url.get(url)

    seed_recs: list[dict[str, Any]] = [
        # amira
        {
            "recommendation_id": _uuid(),
            "user_id": str(amira.user_id),
            "opportunity_id": str(_pick("https://jobs.inria.fr/nlp-intern-2025").id),
            "score": 0.91,
            "match_reasons": [
                "4 of your skills match (Python, NLP, PyTorch)",
                "Master level compatible",
                "Deadline in 30 days — apply soon",
                "Matches your interest in NLP",
            ],
        },
        {
            "recommendation_id": _uuid(),
            "user_id": str(amira.user_id),
            "opportunity_id": str(_pick("https://careers.cern.ch/nlp-intern-2025").id),
            "score": 0.87,
            "match_reasons": [
                "3 of your skills match (Python, NLP, Hugging Face)",
                "Master level compatible",
                "Matches your interest in NLP",
            ],
        },
        {
            "recommendation_id": _uuid(),
            "user_id": str(amira.user_id),
            "opportunity_id": str(
                _pick("https://campusfrance.org/eiffel-scholarship-2025").id
            ),
            "score": 0.82,
            "match_reasons": [
                "Priority scholarship for Tunisia",
                "Master level compatible",
                "Deadline in 45 days — plan ahead",
            ],
        },
        # youssef
        {
            "recommendation_id": _uuid(),
            "user_id": str(youssef.user_id),
            "opportunity_id": str(
                _pick("https://research.google/programs/nlp-benchmark-2025").id
            ),
            "score": 0.89,
            "match_reasons": [
                "3 of your skills match (Python, PyTorch, NLP)",
                "PhD level compatible",
                "Matches your interest in AI",
            ],
        },
        {
            "recommendation_id": _uuid(),
            "user_id": str(youssef.user_id),
            "opportunity_id": str(
                _pick("https://daad.de/scholarships/ai-data-science-2025").id
            ),
            "score": 0.84,
            "match_reasons": [
                "PhD level compatible",
                "Matches your interest in Data Science",
                "Deadline in 90 days",
            ],
        },
        {
            "recommendation_id": _uuid(),
            "user_id": str(youssef.user_id),
            "opportunity_id": str(
                _pick(
                    "https://researchgate.net/project/federated-learning-healthcare-2025"
                ).id
            ),
            "score": 0.78,
            "match_reasons": [
                "2 of your skills match (Python, TensorFlow)",
                "PhD level compatible",
                "Research project matches your profile",
            ],
        },
        # sofia
        {
            "recommendation_id": _uuid(),
            "user_id": str(sofia.user_id),
            "opportunity_id": str(_pick("https://jobs.airbus.com/intern-cv-2025").id),
            "score": 0.93,
            "match_reasons": [
                "4 of your skills match (Python, PyTorch, computer vision, Docker)",
                "Bachelor level compatible",
                "Matches your interest in AI",
                "Deadline in 45 days",
            ],
        },
        {
            "recommendation_id": _uuid(),
            "user_id": str(sofia.user_id),
            "opportunity_id": str(_pick("https://esa.int/careers/cv-intern-2025").id),
            "score": 0.88,
            "match_reasons": [
                "4 of your skills match (Python, computer vision, PyTorch, scikit-learn)",
                "Deadline in 35 days — apply soon",
                "Matches your interest in AI",
            ],
        },
        {
            "recommendation_id": _uuid(),
            "user_id": str(sofia.user_id),
            "opportunity_id": str(
                _pick("https://edx.org/course/computer-vision-pytorch").id
            ),
            "score": 0.80,
            "match_reasons": [
                "3 of your skills match (Python, PyTorch, computer vision)",
                "Recommended to strengthen your CV skills",
            ],
        },
        # lars
        {
            "recommendation_id": _uuid(),
            "user_id": str(lars.user_id),
            "opportunity_id": str(
                _pick(
                    "https://coursera.org/specializations/"
                    "machine-learning-engineering-for-production-mlops"
                ).id
            ),
            "score": 0.92,
            "match_reasons": [
                "3 of your skills match (Python, MLOps, Docker)",
                "Professional level compatible",
                "Matches your interest in AI",
            ],
        },
        {
            "recommendation_id": _uuid(),
            "user_id": str(lars.user_id),
            "opportunity_id": str(
                _pick("https://capgemini.jobs/mlops-intern-2025").id
            ),
            "score": 0.85,
            "match_reasons": [
                "4 of your skills match (Python, MLOps, Docker, Kubernetes)",
                "Matches your interest in AI",
                "Deadline in 40 days",
            ],
        },
        {
            "recommendation_id": _uuid(),
            "user_id": str(lars.user_id),
            "opportunity_id": str(
                _pick("https://research.cern.ch/open-science-ml-2025").id
            ),
            "score": 0.76,
            "match_reasons": [
                "3 of your skills match (Python, Docker, Julia)",
                "Professional-grade research project",
            ],
        },
    ]

    for rec_data in seed_recs:
        if rec_data["opportunity_id"] is None:
            print(f"  [warn] recommendation references missing opportunity — skipped")
            continue
        existing = await session.execute(
            select(Recommendation).where(
                Recommendation.user_id == rec_data["user_id"],
                Recommendation.opportunity_id == rec_data["opportunity_id"],
            )
        )
        if existing.scalar_one_or_none():
            print(f"  [skip] recommendation already exists")
            continue
        session.add(Recommendation(**rec_data))
        print(f"  [add]  recommendation score={rec_data['score']}")


async def _seed_notifications(
    session: AsyncSession,
    users: dict[str, User],
    opportunities: list[Opportunity],
) -> None:
    """Create deadline-alert notifications for near-expiry opportunities."""
    opp_by_url: dict[str, Opportunity] = {o.url: o for o in opportunities}

    near_expiry = [
        ("https://thalesgroup.com/careers/recsys-intern-2025", "amira@observatory.test"),
        ("https://capgemini.com/careers/analytics-intern-2025", "youssef@observatory.test"),
        ("https://sorbonne.fr/scholarships/international-ai-2025", "amira@observatory.test"),
    ]

    for url, email in near_expiry:
        opp = opp_by_url.get(url)
        user = users.get(email)
        if not opp or not user:
            continue

        days_left = (opp.deadline - TODAY).days if opp.deadline else None
        msg = (
            f"⏰ Deadline alert: '{opp.title}' expires in {days_left} days."
            if days_left is not None
            else f"⏰ Deadline alert: '{opp.title}' is expiring soon."
        )

        existing = await session.execute(
            select(Notification).where(
                Notification.user_id == str(user.user_id),
                Notification.opportunity_id == str(opp.id),
            )
        )
        if existing.scalar_one_or_none():
            print(f"  [skip] notification already exists for {email}")
            continue

        session.add(
            Notification(
                notification_id=_uuid(),
                user_id=str(user.user_id),
                opportunity_id=str(opp.id),
                message=msg,
                status=NotificationStatus.unread,
                timestamp=datetime.utcnow(),
            )
        )
        print(f"  [add]  notification → {email}: {msg[:60]}…")


# ═══════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════


async def main(wipe: bool = False) -> None:
    """Run the seed script."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        if wipe:
            await _wipe(session)

        print("\n── Seeding users ──────────────────────────────────────────")
        users = await _seed_users(session)

        print("\n── Seeding opportunities ───────────────────────────────────")
        opportunities = await _seed_opportunities(session)

        print("\n── Seeding recommendations ─────────────────────────────────")
        await _seed_recommendations(session, users, opportunities)

        print("\n── Seeding notifications ───────────────────────────────────")
        await _seed_notifications(session, users, opportunities)

        await session.commit()

    await engine.dispose()
    print("\n✅  Seed complete.\n")
    _print_summary()


def _print_summary() -> None:
    """Print test credentials for quick reference."""
    print("────────────────────────────────────────────────────────────────")
    print("  TEST ACCOUNTS  (all passwords: Password123!)")
    print("────────────────────────────────────────────────────────────────")
    print("  amira@observatory.test    — Master  — NLP/AI skills")
    print("  youssef@observatory.test  — PhD     — Data Science skills")
    print("  sofia@observatory.test    — Bachelor — CV/AI skills")
    print("  lars@observatory.test     — Professional — MLOps skills")
    print("────────────────────────────────────────────────────────────────")
    counts = {
        "internship": 20,
        "scholarship": 15,
        "project": 10,
        "course": 15,
    }
    total = sum(counts.values())
    print(f"  Opportunities: {total} total  " + " | ".join(f"{k}={v}" for k, v in counts.items()))
    print("────────────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the Observatory database.")
    parser.add_argument(
        "--wipe",
        action="store_true",
        help="Wipe existing seeded rows before inserting.",
    )
    args = parser.parse_args()
    asyncio.run(main(wipe=args.wipe))
