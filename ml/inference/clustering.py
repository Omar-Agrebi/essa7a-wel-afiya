"""
Standalone ML clustering module for grouping opportunities by topic.
No FastAPI, SQLAlchemy, or agent imports allowed in this module.
"""
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import joblib

logger = logging.getLogger(__name__)


class OpportunityClusterer:
    """
    TF-IDF + KMeans clusterer that groups opportunities into n_clusters clusters.
    Cluster labels are derived from the top TF-IDF terms in each cluster center.
    Must be fitted fresh on each pipeline run since the opportunity set may change.
    """

    def __init__(self, n_clusters: int = 5) -> None:
        """
        Initialize clusterer.

        Args:
            n_clusters: Number of clusters (default 5).
        """
        self.n_clusters = n_clusters
        self.vectorizer: TfidfVectorizer | None = None
        self.kmeans: KMeans | None = None
        self.cluster_labels: dict[int, str] = {}
        self.is_fitted: bool = False

    def fit(self, texts: list[str]) -> None:
        """
        Fit the TF-IDF vectorizer and KMeans on the provided texts.
        Generates human-readable cluster labels from top TF-IDF terms.

        Args:
            texts: List of combined opportunity text strings.

        Raises:
            ValueError: If fewer texts than n_clusters are provided.
        """
        if len(texts) < self.n_clusters:
            raise ValueError(
                f"Need at least {self.n_clusters} texts to fit {self.n_clusters} clusters, "
                f"got {len(texts)}."
            )

        self.vectorizer = TfidfVectorizer(max_features=3000, stop_words="english")
        self.kmeans = KMeans(
            n_clusters=self.n_clusters, random_state=42, n_init=10
        )

        matrix = self.vectorizer.fit_transform(texts)
        self.kmeans.fit(matrix)
        self._generate_labels()
        self.is_fitted = True

        logger.info(
            f"OpportunityClusterer fitted on {len(texts)} texts "
            f"into {self.n_clusters} clusters: {self.cluster_labels}"
        )

    def _generate_labels(self) -> None:
        """
        Generate human-readable labels for each cluster from top TF-IDF terms.
        Stores results in self.cluster_labels.
        """
        assert self.vectorizer is not None and self.kmeans is not None
        feature_names = np.array(self.vectorizer.get_feature_names_out())
        centers = self.kmeans.cluster_centers_

        for cluster_id, center in enumerate(centers):
            top_indices = center.argsort()[-5:][::-1]
            top_terms = feature_names[top_indices].tolist()
            self.cluster_labels[cluster_id] = " ".join(top_terms)

    def predict(self, text: str) -> int:
        """
        Predict cluster id for a single text.

        Args:
            text: Opportunity text string.

        Returns:
            int: Cluster id (0 to n_clusters-1).
        """
        assert self.is_fitted, "Clusterer must be fitted before prediction."
        vec = self.vectorizer.transform([text])
        return int(self.kmeans.predict(vec)[0])

    def predict_batch(self, texts: list[str]) -> list[int]:
        """
        Predict cluster ids for a list of texts.

        Args:
            texts: List of opportunity text strings.

        Returns:
            list[int]: List of cluster ids.
        """
        assert self.is_fitted, "Clusterer must be fitted before prediction."
        matrix = self.vectorizer.transform(texts)
        return [int(cid) for cid in self.kmeans.predict(matrix)]

    def get_cluster_label(self, cluster_id: int) -> str:
        """
        Return the human-readable label for a given cluster id.

        Args:
            cluster_id: Integer cluster id.

        Returns:
            str: Human-readable label derived from top TF-IDF terms.
        """
        return self.cluster_labels.get(cluster_id, f"Cluster {cluster_id}")

    def get_all_labels(self) -> dict[int, str]:
        """
        Return a copy of all cluster labels.

        Returns:
            dict[int, str]: Mapping of cluster_id → label string.
        """
        return dict(self.cluster_labels)

    def save(self, path: str) -> None:
        """
        Persist all clusterer state to a joblib file.

        Args:
            path: File path to save the model.
        """
        joblib.dump(
            {
                "n_clusters": self.n_clusters,
                "vectorizer": self.vectorizer,
                "kmeans": self.kmeans,
                "cluster_labels": self.cluster_labels,
                "is_fitted": self.is_fitted,
            },
            path,
        )
        logger.info(f"OpportunityClusterer saved to {path}")

    def load(self, path: str) -> None:
        """
        Restore all clusterer state from a joblib file.

        Args:
            path: File path to load the model from.
        """
        state = joblib.load(path)
        self.n_clusters = state["n_clusters"]
        self.vectorizer = state["vectorizer"]
        self.kmeans = state["kmeans"]
        self.cluster_labels = state["cluster_labels"]
        self.is_fitted = state["is_fitted"]
        logger.info(f"OpportunityClusterer loaded from {path}")
