import numpy as np
from collections import defaultdict
from typing import List, Tuple, Callable, Dict, Any, Optional, Union
from aimakerspace.openai_utils.embedding import EmbeddingModel
import asyncio


def cosine_similarity(vector_a: np.array, vector_b: np.array) -> float:
    """Computes the cosine similarity between two vectors."""
    dot_product = np.dot(vector_a, vector_b)
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)
    return dot_product / (norm_a * norm_b)


class VectorDatabase:
    def __init__(self, embedding_model: Optional[EmbeddingModel] = None):
        self.vectors = defaultdict(np.array)
        self.metadata = defaultdict(dict)  # Store metadata for each vector
        self.embedding_model = embedding_model

    def insert(self, key: str, vector: np.array, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Insert a vector with optional metadata."""
        self.vectors[key] = vector
        if metadata is not None:
            self.metadata[key] = metadata

    def insert_with_metadata(self, key: str, vector: np.array, **metadata) -> None:
        """Insert a vector with metadata as keyword arguments."""
        self.vectors[key] = vector
        self.metadata[key] = metadata

    def search(
        self,
        query_vector: np.array,
        k: int,
        distance_measure: Callable = cosine_similarity,
        include_metadata: bool = False,
    ) -> List[Union[Tuple[str, float], Tuple[str, float, Dict[str, Any]]]]:
        """Search for similar vectors with optional metadata inclusion."""
        scores = [
            (key, distance_measure(query_vector, vector))
            for key, vector in self.vectors.items()
        ]
        results = sorted(scores, key=lambda x: x[1], reverse=True)[:k]
        
        if include_metadata:
            return [(key, score, self.metadata.get(key, {})) for key, score in results]
        return results

    def search_by_text(
        self,
        query_text: str,
        k: int,
        distance_measure: Callable = cosine_similarity,
        return_as_text: bool = False,
        include_metadata: bool = False,
    ) -> List[Union[str, Tuple[str, float], Tuple[str, float, Dict[str, Any]]]]:
        """Search for similar vectors by text query with optional metadata inclusion."""
        if self.embedding_model is None:
            raise ValueError("No embedding model available. Cannot convert text to vector.")
        query_vector = self.embedding_model.get_embedding(query_text)
        results = self.search(query_vector, k, distance_measure, include_metadata)
        return [result[0] for result in results] if return_as_text else results

    def retrieve_from_key(self, key: str) -> np.array:
        return self.vectors.get(key, None)

    def get_metadata(self, key: str) -> Dict[str, Any]:
        """Get metadata for a specific vector key."""
        return self.metadata.get(key, {})

    def update_metadata(self, key: str, metadata: Dict[str, Any]) -> None:
        """Update metadata for an existing vector key."""
        if key in self.vectors:
            self.metadata[key].update(metadata)
        else:
            raise KeyError(f"Vector with key '{key}' not found")

    def filter_by_metadata(self, **filters) -> List[str]:
        """Filter vector keys by metadata criteria."""
        matching_keys = []
        for key, metadata in self.metadata.items():
            if all(metadata.get(k) == v for k, v in filters.items()):
                matching_keys.append(key)
        return matching_keys

    async def abuild_from_list(self, list_of_text: List[str], metadata_list: Optional[List[Dict[str, Any]]] = None) -> "VectorDatabase":
        """Build vector database from list of texts with optional metadata."""
        if self.embedding_model is None:
            raise ValueError("No embedding model available. Cannot convert text to vectors.")
        embeddings = await self.embedding_model.async_get_embeddings(list_of_text)
        for i, (text, embedding) in enumerate(zip(list_of_text, embeddings)):
            metadata = metadata_list[i] if metadata_list and i < len(metadata_list) else None
            self.insert(text, np.array(embedding), metadata)
        return self


if __name__ == "__main__":
    list_of_text = [
        "I like to eat broccoli and bananas.",
        "I ate a banana and spinach smoothie for breakfast.",
        "Chinchillas and kittens are cute.",
        "My sister adopted a kitten yesterday.",
        "Look at this cute hamster munching on a piece of broccoli.",
    ]
    
    # Example metadata for each text
    metadata_list = [
        {"category": "food", "sentiment": "positive", "source": "personal"},
        {"category": "food", "sentiment": "neutral", "source": "personal"},
        {"category": "animals", "sentiment": "positive", "source": "general"},
        {"category": "animals", "sentiment": "positive", "source": "family"},
        {"category": "animals", "sentiment": "positive", "source": "observation"},
    ]

    vector_db = VectorDatabase()
    vector_db = asyncio.run(vector_db.abuild_from_list(list_of_text, metadata_list))
    k = 2

    # Test basic search
    searched_vector = vector_db.search_by_text("I think fruit is awesome!", k=k)
    print(f"Closest {k} vector(s):", searched_vector)

    # Test search with metadata
    searched_with_metadata = vector_db.search_by_text("I think fruit is awesome!", k=k, include_metadata=True)
    print(f"Closest {k} vector(s) with metadata:", searched_with_metadata)

    # Test metadata filtering
    food_vectors = vector_db.filter_by_metadata(category="food")
    print(f"Food-related vectors: {food_vectors}")

    # Test metadata retrieval
    metadata = vector_db.get_metadata("I like to eat broccoli and bananas.")
    print(f"Metadata for first text: {metadata}")

    retrieved_vector = vector_db.retrieve_from_key(
        "I like to eat broccoli and bananas."
    )
    print("Retrieved vector:", retrieved_vector)

    relevant_texts = vector_db.search_by_text(
        "I think fruit is awesome!", k=k, return_as_text=True
    )
    print(f"Closest {k} text(s):", relevant_texts)
