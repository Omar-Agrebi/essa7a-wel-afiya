import asyncio
import uuid
from datetime import date, timedelta
from app.models.opportunity import Opportunity
from app.core.constants import OpportunityType, OpportunityCategory
from database.session import AsyncSessionLocal

mock_opportunities = [
    {
        "title": "Google AI Research Internship",
        "type": OpportunityType.internship,
        "category": OpportunityCategory.AI,
        "description": "Join Google's foundational AI research team to work on large language models and multi-modal generative networks.",
        "skills_required": ["Python", "PyTorch", "TensorFlow", "Deep Learning"],
        "location": "London, UK (Hybrid)",
        "eligibility": "Must be pursuing a PhD in Computer Science or related fields.",
        "deadline": date.today() + timedelta(days=30),
        "source": "Google Careers",
        "url": "https://careers.google.com/jobs/results/mock-ai-internship",
    },
    {
        "title": "Oxford DeepMind Scholarship",
        "type": OpportunityType.scholarship,
        "category": OpportunityCategory.AI,
        "description": "Full scholarship for underrepresented students pursuing a Master's in Artificial Intelligence at the University of Oxford.",
        "skills_required": ["Mathematics", "Programming", "Machine Learning"],
        "location": "Oxford, UK",
        "eligibility": "Open to prospective Master's students.",
        "deadline": date.today() + timedelta(days=60),
        "source": "DeepMind Scholarships",
        "url": "https://deepmind.google/discover/mock-scholarship",
    },
    {
        "title": "Cybersecurity Graduate Project",
        "type": OpportunityType.project,
        "category": OpportunityCategory.Cybersecurity,
        "description": "Collaborate with industry leading professionals to penetration-test modern distributed systems.",
        "skills_required": ["Networking", "Linux", "Penetration Testing", "Go"],
        "location": "Remote",
        "eligibility": "Undergraduate students in their final year.",
        "deadline": date.today() + timedelta(days=15),
        "source": "University Portal",
        "url": "https://university.edu/projects/cyber-security-mock",
    },
    {
        "title": "Data Science Postdoctoral Fellowship",
        "type": OpportunityType.postdoc,
        "category": OpportunityCategory.Data_Science,
        "description": "Two-year postdoctoral fellowship analyzing planetary scale geospatial datasets.",
        "skills_required": ["Python", "R", "Geospatial Analysis", "PostGIS"],
        "location": "MIT, Cambridge, MA",
        "eligibility": "Recent PhD graduates (within the last 3 years).",
        "deadline": date.today() + timedelta(days=90),
        "source": "Nature Careers",
        "url": "https://nature.careers.com/job/data-science-postdoc-mock",
    },
    {
        "title": "Stanford Open Course: Advanced NLP",
        "type": OpportunityType.course,
        "category": OpportunityCategory.Software_Engineering,
        "description": "Free open course introducing the fundamentals of Natural Language Processing and Transformer architectures.",
        "skills_required": ["Python", "Linear Algebra"],
        "location": "Online",
        "eligibility": "Open to everyone.",
        "deadline": None,
        "source": "Stanford Online",
        "url": "https://online.stanford.edu/courses/nlp-mock",
    }
]

async def seed_opportunities():
    async with AsyncSessionLocal() as session:
        print("Seeding opportunities...")
        for opp_data in mock_opportunities:
            opp = Opportunity(**opp_data)
            session.add(opp)
        
        try:
            await session.commit()
            print(f"Successfully added {len(mock_opportunities)} mock opportunities to the database!")
        except Exception as e:
            await session.rollback()
            print("Failed to seed database. They might already exist.")
            print(e)

if __name__ == "__main__":
    asyncio.run(seed_opportunities())
