"""
Collection Rebuilder - Fix embedding model issue
Recreates the collection with proper OpenAI embedding function
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rebuild_collection.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def rebuild_collection_with_openai_embeddings(chroma_dir: str = "./chroma_db_openai",
                                               collection_name: str = "nasa_space_missions_text"):
    """
    Rebuild the collection with proper OpenAI embedding function.
    This fixes the issue where collections were created without specifying embedding models.
    """
    
    logger.info(f"\n{'='*80}")
    logger.info("COLLECTION REBUILDER - Adding OpenAI Embeddings")
    logger.info(f"{'='*80}\n")
    
    # Step 1: Check if OPENAI_API_KEY is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("ERROR: OPENAI_API_KEY environment variable not set!")
        logger.error("Set it with: $env:OPENAI_API_KEY='your-api-key'")
        return False
    
    logger.info(f"[OK] OpenAI API key found (length: {len(api_key)} chars)")
    
    # Step 2: Create persistent client
    logger.info(f"\n[STEP 1] Connecting to ChromaDB at {chroma_dir}")
    old_client = chromadb.PersistentClient(
        path=chroma_dir,
        settings=Settings(anonymized_telemetry=False, allow_reset=True)
    )
    
    try:
        old_collection = old_client.get_collection(name=collection_name)
        old_count = old_collection.count()
        logger.info(f"[OK] Found existing collection with {old_count} documents")
    except Exception as e:
        logger.error(f"ERROR: Could not find collection '{collection_name}': {e}")
        return False
    
    # Step 3: Get all documents from old collection
    logger.info(f"\n[STEP 2] Extracting documents from old collection...")
    try:
        all_data = old_collection.get(limit=10000, include=['documents', 'metadatas'])
        
        ids = all_data['ids']
        documents = all_data['documents']
        metadatas = all_data['metadatas']
        
        logger.info(f"[OK] Extracted {len(ids)} documents")
        
        if len(ids) == 0:
            logger.warning("WARNING: No documents found in collection!")
            return False
            
    except Exception as e:
        logger.error(f"ERROR: Failed to extract documents: {e}")
        return False
    
    # Step 4: Create embedding function
    logger.info(f"\n[STEP 3] Creating OpenAI embedding function...")
    try:
        embedding_function = OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name="text-embedding-3-small"  # Fast, small, high-quality
        )
        logger.info("[OK] OpenAI embedding function created (model: text-embedding-3-small)")
    except Exception as e:
        logger.error(f"ERROR: Failed to create embedding function: {e}")
        return False
    
    # Step 5: Test embedding function
    logger.info(f"\n[STEP 4] Testing embedding function...")
    try:
        test_embedding = embedding_function(["test"])
        logger.info(f"[OK] Embedding function works (vector dimension: {len(test_embedding[0])})")
    except Exception as e:
        logger.error(f"ERROR: Embedding function test failed: {e}")
        logger.error("Check your OpenAI API key and quota")
        return False
    
    # Step 6: Delete old collection and recreate with proper embedding
    logger.info(f"\n[STEP 5] Recreating collection with OpenAI embeddings...")
    try:
        # Delete old collection
        logger.info("Deleting old collection...")
        old_client.delete_collection(name=collection_name)
        logger.info("[OK] Old collection deleted")
        
        # Create new collection with embedding function
        logger.info("Creating new collection with embedding function...")
        new_client = chromadb.PersistentClient(
            path=chroma_dir,
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        
        new_collection = new_client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function,
            metadata={"description": "NASA space missions with OpenAI embeddings (text-embedding-3-small)"}
        )
        logger.info("[OK] New collection created")
        
    except Exception as e:
        logger.error(f"ERROR: Failed to recreate collection: {e}")
        return False
    
    # Step 7: Re-add documents in batches
    logger.info(f"\n[STEP 6] Adding {len(ids)} documents to new collection...")
    batch_size = 50
    added_count = 0
    
    try:
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i+batch_size]
            batch_docs = documents[i:i+batch_size]
            batch_metas = metadatas[i:i+batch_size]
            
            new_collection.add(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_metas
            )
            added_count += len(batch_ids)
            
            logger.info(f"  [{added_count}/{len(ids)}] documents added...")
        
        logger.info(f"[OK] All {added_count} documents added to new collection")
        
    except Exception as e:
        logger.error(f"ERROR: Failed to add documents: {e}")
        logger.error(f"Added {added_count} before failure")
        return False
    
    # Step 8: Verify collection
    logger.info(f"\n[STEP 7] Verifying collection...")
    try:
        final_count = new_collection.count()
        logger.info(f"[OK] Collection verification: {final_count} documents")
        
        if final_count != len(ids):
            logger.warning(f"WARNING: Count mismatch! Expected {len(ids)}, got {final_count}")
            return False
        
    except Exception as e:
        logger.error(f"ERROR: Verification failed: {e}")
        return False
    
    # Step 9: Quick test query
    logger.info(f"\n[STEP 8] Testing with sample query 'Apollo 11'...")
    try:
        results = new_collection.query(
            query_texts=["Apollo 11"],
            n_results=3,
            include=['documents', 'distances']
        )
        
        distances = results['distances'][0] if results['distances'] else []
        if distances:
            avg_distance = sum(distances) / len(distances)
            logger.info(f"[OK] Query returned {len(distances)} results")
            logger.info(f"    Average distance: {avg_distance:.4f}")
            
            if avg_distance < 0.5:
                logger.info("    [GOOD] Distances look reasonable!")
            else:
                logger.warning(f"    [CAUTION] Distances still high (> 0.5)")
        
    except Exception as e:
        logger.error(f"ERROR: Test query failed: {e}")
        return False
    
    logger.info(f"\n{'='*80}")
    logger.info("REBUILD COMPLETE!")
    logger.info(f"{'='*80}\n")
    logger.info("Next steps:")
    logger.info("1. Run diagnostics: python collection_diagnostic.py --test all")
    logger.info("2. Run validation: python validate_rag_collection.py")
    logger.info("")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Rebuild collection with OpenAI embeddings')
    parser.add_argument('--chroma-dir', default='./chroma_db_openai')
    parser.add_argument('--collection', default='nasa_space_missions_text')
    parser.add_argument('--api-key', help='OpenAI API key (uses OPENAI_API_KEY env var if not provided)')
    
    args = parser.parse_args()
    
    if args.api_key:
        os.environ['OPENAI_API_KEY'] = args.api_key
    
    success = rebuild_collection_with_openai_embeddings(args.chroma_dir, args.collection)
    exit(0 if success else 1)
