"""
Standalone ML classifier for opportunity type and category prediction.
No FastAPI, SQLAlchemy, or agent imports allowed in this module.
"""
import logging
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

logger = logging.getLogger(__name__)


class OpportunityClassifier:
    """
    TF-IDF + Logistic Regression classifier that predicts opportunity type
    (internship, scholarship, project, course, postdoc) and category
    (AI, Data Science, Cybersecurity, Software Engineering, Other).
    Trained entirely on inline synthetic data — no external files required.
    """

    def __init__(self) -> None:
        """Initialize classifier with empty pipelines."""
        self.type_pipeline: Pipeline | None = None
        self.category_pipeline: Pipeline | None = None
        self.is_trained: bool = False

    def _build_training_data(self) -> tuple[list[str], list[str], list[str]]:
        """
        Build inline synthetic training dataset.

        Returns:
            tuple: (texts, type_labels, category_labels)
        """
        data: list[tuple[str, str, str]] = [
            # ── INTERNSHIPS (20) ─────────────────────────────────────────────
            ("Join our team as a software engineer intern at DeepMind working on neural network architectures. Competitive salary and mentoring program.", "internship", "AI"),
            ("Internship opportunity at Airbus for a machine learning engineer. Join our AI research division with a monthly stipend.", "internship", "AI"),
            ("INRIA is hiring a research intern in deep learning for computer vision. Six-month internship with salary.", "internship", "AI"),
            ("Siemens software engineer intern position focusing on Python backend development and API design. Paid internship in Berlin.", "internship", "Software Engineering"),
            ("Capgemini data science intern role. Work on real data pipelines using pandas, SQL and data visualization tools.", "internship", "Data Science"),
            ("Thales internship for a cybersecurity analyst. Penetration testing and vulnerability assessment. Salary offered.", "internship", "Cybersecurity"),
            ("Join ESA as a data science intern. Analyse satellite telemetry data using statistics and machine learning models.", "internship", "Data Science"),
            ("TotalEnergies software intern role. Build microservices and REST APIs in an agile environment. Paid internship in Paris.", "internship", "Software Engineering"),
            ("DeepMind research intern in reinforcement learning. Join our team and collaborate on world-class AI publications.", "internship", "AI"),
            ("Dassault Systèmes machine learning intern. Create artificial intelligence solutions for CAD/CAM software. Salary included.", "internship", "AI"),
            ("CERN software engineering intern. Develop backend systems and APIs for particle physics data pipelines. Monthly salary.", "internship", "Software Engineering"),
            ("TU Berlin internship in NLP research. Work on transformer models and language understanding. Stipend provided.", "internship", "AI"),
            ("WHO data analysis intern. Use statistics, pandas and Python to process health data and create visualizations.", "internship", "Data Science"),
            ("Network security intern at Thales. Hands-on experience in cryptography, network monitoring and penetration testing.", "internship", "Cybersecurity"),
            ("ETH Zurich computer vision research internship. Deep learning, PyTorch, convolutional neural networks. Join our team.", "internship", "AI"),
            ("Capgemini software development intern. Agile methodologies, backend development, API design. Paid position in London.", "internship", "Software Engineering"),
            ("Data engineering intern at TotalEnergies. Build data pipelines with Spark and SQL. Statistics background required.", "internship", "Data Science"),
            ("Cybersecurity intern at Siemens. Vulnerability assessment and network security. Competitive intern salary.", "internship", "Cybersecurity"),
            ("Intern in AI safety research at EPFL. Work with reinforcement learning and artificial intelligence alignment.", "internship", "AI"),
            ("Data science intern at Max Planck Institute. Statistical modelling and data visualization using Python and R.", "internship", "Data Science"),

            # ── SCHOLARSHIPS (20) ────────────────────────────────────────────
            ("DAAD scholarship for master students in AI and machine learning. Monthly stipend of 1200 EUR plus travel allowance. Application deadline in March.", "scholarship", "AI"),
            ("Erasmus+ scholarship funding for eligible candidates in data science programs across Europe. Financial support and tuition coverage.", "scholarship", "Data Science"),
            ("Eiffel Excellence Scholarship for international PhD students in computer science. Monthly stipend, health insurance, and travel funding.", "scholarship", "AI"),
            ("Marie Curie Fellowship funding for postdoctoral researchers in cybersecurity and network security. Competitive financial support.", "scholarship", "Cybersecurity"),
            ("Campus France scholarship for eligible candidates pursuing master programs in software engineering. Application deadline March 31.", "scholarship", "Software Engineering"),
            ("DAAD development scholarship for STEM students in data science. Includes monthly stipend, health insurance, tuition coverage.", "scholarship", "Data Science"),
            ("Horizon Europe scholarship for PhD candidates in artificial intelligence and deep learning. Financial support provided.", "scholarship", "AI"),
            ("Excellence scholarship for bachelor students in cybersecurity and penetration testing. Funding available for eligible candidates.", "scholarship", "Cybersecurity"),
            ("Erasmus Mundus scholarship for master's in data analysis and statistics. Monthly stipend and full tuition coverage.", "scholarship", "Data Science"),
            ("KAAD scholarship for PhD candidates in software development and microservices. Financial support and travel allowance.", "scholarship", "Software Engineering"),
            ("Swiss Government Excellence Scholarship for machine learning researchers. Full funding, monthly stipend, and housing allowance.", "scholarship", "AI"),
            ("Fellowship funding for eligible master students in AI and computer vision. Application deadline in April.", "scholarship", "AI"),
            ("Heinrich Böll Foundation scholarship for PhD students in data science and visualization. Monthly stipend provided.", "scholarship", "Data Science"),
            ("Government of France scholarship for eligible international students in cybersecurity. Financial support and tuition coverage.", "scholarship", "Cybersecurity"),
            ("Volkswagen Foundation scholarship for researchers in artificial intelligence and neural networks. Competitive stipend.", "scholarship", "AI"),
            ("ARES scholarship for master and PhD candidates in software engineering. Application deadline approaching. Full financial support.", "scholarship", "Software Engineering"),
            ("British Council scholarship for eligible students in data analysis and statistics. Monthly stipend and tuition coverage.", "scholarship", "Data Science"),
            ("Gates Cambridge Scholarship for PhD students in machine learning and AI. Full funding with monthly living allowance.", "scholarship", "AI"),
            ("UNESCO-L'Oréal scholarship for women in STEM fields including data science. Financial support for eligible candidates.", "scholarship", "Data Science"),
            ("Fulbright scholarship for AI researchers from North Africa. Monthly stipend, visa support, and travel funding.", "scholarship", "AI"),

            # ── PROJECTS (15) ────────────────────────────────────────────────
            ("Horizon Europe funded research project on federated learning and privacy-preserving AI. PhD position available, collaborate with top institutions.", "project", "AI"),
            ("INRIA research project on deep learning for medical imaging. Funded by ANR, seeking PhD candidates to publish findings in top journals.", "project", "AI"),
            ("Max Planck Institute research project in NLP and large language models. Funded position, collaborate with international teams.", "project", "AI"),
            ("Funded research project in data science and epidemiology at WHO. Collaborate with global researchers to analyze health data pipelines.", "project", "Data Science"),
            ("KU Leuven research project on network security and cryptography. PhD position, funded by EU, publish findings in security conferences.", "project", "Cybersecurity"),
            ("ETH Zurich project on reinforcement learning for robotics. Funded by Swiss NSF. Collaborate with AI labs to publish findings.", "project", "AI"),
            ("Horizon Europe project on AI safety and alignment research. PhD position at EPFL. Collaborate with leading artificial intelligence labs.", "project", "AI"),
            ("Research project on explainable data science and statistical modelling. Funded by European Research Council. PhD or postdoc position.", "project", "Data Science"),
            ("Funded cybersecurity project on vulnerability assessment and penetration testing at KU Leuven. Collaborate with industry partners.", "project", "Cybersecurity"),
            ("Politecnico di Milano project on machine learning for climate prediction. Funded research, seeking PhD candidates to publish findings.", "project", "AI"),
            ("University of Amsterdam funded project in NLP and text mining. Collaborate with data science teams to build analysis pipelines.", "project", "Data Science"),
            ("Sorbonne research project on microservices and software architecture. Funded by ANR, PhD position available.", "project", "Software Engineering"),
            ("EPFL funded project on computer vision and artificial intelligence. Collaborate with international labs, publish findings in top venues.", "project", "AI"),
            ("Research project on data visualization and statistical analysis methods. Funded position at TU Berlin. Collaborate to publish findings.", "project", "Data Science"),
            ("ERC funded project on API design patterns and microservices architectures. Software engineering PhD position at TU Berlin.", "project", "Software Engineering"),

            # ── COURSES (15) ─────────────────────────────────────────────────
            ("Learn deep learning from beginner to advanced. Enroll in this self-paced course covering neural networks and PyTorch. Certificate included.", "course", "AI"),
            ("Machine learning certificate program. 40 hours of content, beginner to advanced. Enroll now and learn Python, scikit-learn, and statistics.", "course", "AI"),
            ("Data science professional certificate. Learn pandas, data visualization, and statistics. Self-paced, beginner friendly. Enroll online.", "course", "Data Science"),
            ("Cybersecurity fundamentals certificate. Learn network security, penetration testing and cryptography. Beginner to advanced. Enroll now.", "course", "Cybersecurity"),
            ("Natural language processing certificate. Learn transformers and NLP techniques. 30 hours of content. Self-paced, enroll anytime.", "course", "AI"),
            ("Statistical data analysis course. Learn R, statistics, and data visualization from beginner level. Certificate awarded on completion.", "course", "Data Science"),
            ("Software engineering best practices. Enroll to learn backend development, APIs and microservices. Certificate program, self-paced.", "course", "Software Engineering"),
            ("Reinforcement learning specialization. Learn from beginner to advanced over 50 hours of content. Certificate of completion included.", "course", "AI"),
            ("Data pipeline engineering course. Learn Spark, SQL, and data analysis. Self-paced with certificate. Beginner to intermediate level.", "course", "Data Science"),
            ("Ethical hacking and penetration testing certificate. Learn vulnerability assessment and network security. Enroll now, self-paced.", "course", "Cybersecurity"),
            ("Computer vision certificate program. Learn PyTorch, CNNs and image processing. Beginner to advanced. Enroll for 60 hours of content.", "course", "AI"),
            ("Agile software development certificate. Learn agile methodologies, backend development, and API design. Self-paced course.", "course", "Software Engineering"),
            ("Data visualization and dashboards course. Learn pandas, matplotlib, and statistics. Certificate program. Beginner friendly, enroll now.", "course", "Data Science"),
            ("Applied machine learning specialization. Enroll to learn scikit-learn and build real models. 45 hours of content. Complete certificate.", "course", "AI"),
            ("Microservices and DevOps certificate. Learn containerization, APIs, and agile. Beginner to advanced. Self-paced, enroll online.", "course", "Software Engineering"),

            # ── POSTDOCS (10) ────────────────────────────────────────────────
            ("Postdoctoral researcher position in machine learning at ETH Zurich. University academic contract, 2 years. Artificial intelligence focus.", "postdoc", "AI"),
            ("Postdoc fellow in natural language processing at INRIA. Academic position at a leading research university. NLP and AI focus.", "postdoc", "AI"),
            ("Research fellow in data science and statistics at University of Amsterdam. University academic contract, postdoctoral level.", "postdoc", "Data Science"),
            ("Postdoctoral position in cybersecurity and network security at KU Leuven. Research fellow in academic university environment.", "postdoc", "Cybersecurity"),
            ("Postdoc researcher in computer vision and deep learning at Max Planck. University academic contract for research fellow position.", "postdoc", "AI"),
            ("Research fellow in software engineering and microservices at TU Berlin. Postdoctoral university position, 18-month academic contract.", "postdoc", "Software Engineering"),
            ("Postdoc in reinforcement learning and AI safety at EPFL. University academic contract for postdoctoral research fellow.", "postdoc", "AI"),
            ("Research fellow in data analysis and visualization at Sorbonne. Postdoctoral university position. Statistics and data science focus.", "postdoc", "Data Science"),
            ("Postdoctoral researcher in cryptography and network security at ETH Zurich. University academic contract, research fellow role.", "postdoc", "Cybersecurity"),
            ("Postdoc fellow in artificial intelligence and deep learning at Politecnico di Milano. University academic research position available.", "postdoc", "AI"),
        ]

        texts = [d[0] for d in data]
        type_labels = [d[1] for d in data]
        category_labels = [d[2] for d in data]
        return texts, type_labels, category_labels

    def train(self) -> None:
        """
        Train TF-IDF + Logistic Regression pipelines for type and category.
        Sets is_trained = True and logs training accuracy.
        """
        texts, type_labels, category_labels = self._build_training_data()

        self.type_pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
            ("clf", LogisticRegression(max_iter=1000, C=1.0, random_state=42)),
        ])
        self.category_pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
            ("clf", LogisticRegression(max_iter=1000, C=1.0, random_state=42)),
        ])

        self.type_pipeline.fit(texts, type_labels)
        self.category_pipeline.fit(texts, category_labels)
        self.is_trained = True

        type_acc = self.type_pipeline.score(texts, type_labels)
        cat_acc = self.category_pipeline.score(texts, category_labels)
        logger.info(
            f"OpportunityClassifier trained — "
            f"type accuracy: {type_acc:.2%}, category accuracy: {cat_acc:.2%}"
        )

    def predict_type(self, text: str) -> str:
        """
        Predict opportunity type for a single text.

        Args:
            text: Combined title + description text.

        Returns:
            str: Predicted type (internship, scholarship, project, course, postdoc).
        """
        assert self.is_trained, "Classifier must be trained before prediction."
        return str(self.type_pipeline.predict([text])[0])

    def predict_category(self, text: str) -> str:
        """
        Predict opportunity category for a single text.

        Args:
            text: Combined title + description text.

        Returns:
            str: Predicted category (AI, Data Science, Cybersecurity, Software Engineering, Other).
        """
        assert self.is_trained, "Classifier must be trained before prediction."
        return str(self.category_pipeline.predict([text])[0])

    def predict_batch(self, texts: list[str]) -> list[dict]:
        """
        Predict type and category for a batch of texts.

        Args:
            texts: List of combined title + description strings.

        Returns:
            list[dict]: Each dict contains 'type' and 'category' keys.
        """
        assert self.is_trained, "Classifier must be trained before prediction."
        type_preds = self.type_pipeline.predict(texts)
        category_preds = self.category_pipeline.predict(texts)
        return [
            {"type": t, "category": c}
            for t, c in zip(type_preds, category_preds)
        ]

    def save(self, path: str) -> None:
        """
        Persist both pipelines to a joblib file.

        Args:
            path: File path to save the model.
        """
        joblib.dump(
            {"type": self.type_pipeline, "category": self.category_pipeline},
            path,
        )
        logger.info(f"OpportunityClassifier saved to {path}")

    def load(self, path: str) -> None:
        """
        Load both pipelines from a joblib file.

        Args:
            path: File path to load the model from.
        """
        state = joblib.load(path)
        self.type_pipeline = state["type"]
        self.category_pipeline = state["category"]
        self.is_trained = True
        logger.info(f"OpportunityClassifier loaded from {path}")
