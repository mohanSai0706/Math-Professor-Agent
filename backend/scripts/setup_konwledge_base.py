import asyncio
import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.knowledge_base import KnowledgeBaseService
from app.core.config import settings

async def setup_knowledge_base():
    """Setup and populate the knowledge base with mathematical problems."""
    
    print("Setting up Math Routing Agent Knowledge Base...")
    
    try:
        # Initialize knowledge base service
        kb_service = KnowledgeBaseService()
        
        # Initialize collection
        await kb_service.initialize_collection()
        print("✅ Knowledge base collection initialized")
        
        # Load additional data if available
        data_file = Path(__file__).parent.parent.parent / "data" / "math_dataset.json"
        if data_file.exists():
            with open(data_file, 'r') as f:
                additional_data = json.load(f)
            
            for item in additional_data:
                await kb_service.add_to_knowledge_base(
                    question=item["question"],
                    solution=item["solution"],
                    topic=item.get("topic", "general"),
                    source="setup_script"
                )
            
            print(f"✅ Loaded {len(additional_data)} additional problems")
        
        # Get statistics
        points = await kb_service.get_all_points()
        print(f"✅ Knowledge base setup complete with {len(points)} problems")
        
    except Exception as e:
        print(f"❌ Error setting up knowledge base: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(setup_knowledge_base())