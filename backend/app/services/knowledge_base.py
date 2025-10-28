import logging
import asyncio
import numpy as np
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.models.schemas import KnowledgeBaseResult

logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key if settings.qdrant_api_key else None
        )
        self.collection_name = "math_knowledge_base"
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_size = 384  # Size for all-MiniLM-L6-v2
        
    async def initialize_collection(self):
        """Initialize the Qdrant collection for math knowledge base."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_exists = any(
                collection.name == self.collection_name 
                for collection in collections.collections
            )
            
            if not collection_exists:
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
                
                # Load initial data
                await self._load_initial_data()
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Error initializing collection: {str(e)}")
            raise
    
    async def search_knowledge_base(self, question: str, limit: int = 3) -> KnowledgeBaseResult:
        """Search the knowledge base for relevant content."""
        try:
            # Generate embedding for the question
            question_embedding = self.embedding_model.encode(question).tolist()
            
            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=question_embedding,
                limit=limit,
                score_threshold=0.7  # Minimum similarity threshold
            )
            
            if search_results and search_results[0].score > 0.7:
                best_result = search_results[0]
                return KnowledgeBaseResult(
                    found=True,
                    content=best_result.payload.get("content", ""),
                    similarity_score=best_result.score,
                    source=best_result.payload.get("source", "Knowledge Base")
                )
            else:
                return KnowledgeBaseResult(
                    found=False,
                    content=None,
                    similarity_score=search_results[0].score if search_results else 0.0,
                    source=None
                )
                
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return KnowledgeBaseResult(
                found=False,
                content=None,
                similarity_score=0.0,
                source=None
            )
    
    async def add_to_knowledge_base(
        self, 
        question: str, 
        solution: str, 
        topic: str = "general",
        source: str = "user_feedback"
    ):
        """Add new content to the knowledge base."""
        try:
            # Combine question and solution for better search
            combined_content = f"Question: {question}\n\nSolution: {solution}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(combined_content).tolist()
            
            # Generate unique ID
            point_id = len(await self.get_all_points()) + 1
            
            # Create point
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "question": question,
                    "solution": solution,
                    "content": combined_content,
                    "topic": topic,
                    "source": source,
                    "difficulty": "intermediate"  # Default difficulty
                }
            )
            
            # Insert into Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"Added new content to knowledge base: {point_id}")
            
        except Exception as e:
            logger.error(f"Error adding to knowledge base: {str(e)}")
            raise
    
    async def get_all_points(self) -> List[Dict]:
        """Get all points from the collection."""
        try:
            result = self.client.scroll(
                collection_name=self.collection_name,
                limit=1000  # Adjust based on your needs
            )
            return result[0]  # result is a tuple (points, next_page_offset)
        except Exception as e:
            logger.error(f"Error getting all points: {str(e)}")
            return []
    
    async def _load_initial_data(self):
        """Load initial mathematical problems and solutions."""
        initial_data = [
            {
                "question": "What is the derivative of x^2?",
                "solution": "The derivative of x^2 is 2x. Using the power rule: d/dx(x^n) = n*x^(n-1), so d/dx(x^2) = 2*x^(2-1) = 2x.",
                "topic": "calculus",
                "difficulty": "beginner"
            },
            {
                "question": "Solve the quadratic equation x^2 + 5x + 6 = 0",
                "solution": "Step 1: Factor the quadratic. We need two numbers that multiply to 6 and add to 5. Those are 2 and 3.\nStep 2: x^2 + 5x + 6 = (x + 2)(x + 3) = 0\nStep 3: Set each factor to zero: x + 2 = 0 or x + 3 = 0\nStep 4: Solve: x = -2 or x = -3",
                "topic": "algebra",
                "difficulty": "intermediate"
            },
            {
                "question": "What is the area of a circle with radius r?",
                "solution": "The area of a circle with radius r is πr^2. This formula comes from integrating the circumference over the radius.",
                "topic": "geometry",
                "difficulty": "beginner"
            },
            {
                "question": "Find the integral of sin(x)",
                "solution": "The integral of sin(x) is -cos(x) + C, where C is the constant of integration. This is because d/dx(-cos(x)) = sin(x).",
                "topic": "calculus",
                "difficulty": "intermediate"
            },
            {
                "question": "What is the Pythagorean theorem?",
                "solution": "The Pythagorean theorem states that in a right triangle, the square of the hypotenuse (c) equals the sum of squares of the other two sides (a and b): a^2 + b^2 = c^2.",
                "topic": "geometry",
                "difficulty": "beginner"
            }
        ]
        
        points = []
        for i, item in enumerate(initial_data):
            combined_content = f"Question: {item['question']}\n\nSolution: {item['solution']}"
            embedding = self.embedding_model.encode(combined_content).tolist()
            
            point = PointStruct(
                id=i + 1,
                vector=embedding,
                payload={
                    "question": item["question"],
                    "solution": item["solution"],
                    "content": combined_content,
                    "topic": item["topic"],
                    "source": "initial_dataset",
                    "difficulty": item["difficulty"]
                }
            )
            points.append(point)
        
        # Bulk insert
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        logger.info(f"Loaded {len(initial_data)} initial problems into knowledge base")
