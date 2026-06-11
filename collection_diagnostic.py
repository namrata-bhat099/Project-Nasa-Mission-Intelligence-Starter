"""
Diagnostic Tool - Debug RAG Collection Issues
Helps identify why queries are returning NOT_RELEVANT results
"""

import chromadb
from chromadb.config import Settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('diagnostic.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CollectionDiagnostics:
    """Diagnostic tools for RAG collection"""
    
    def __init__(self, chroma_dir: str = "./chroma_db_openai",
                 collection_name: str = "nasa_space_missions_text"):
        self.client = chromadb.PersistentClient(
            path=chroma_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_collection(name=collection_name)
    
    def check_collection_health(self):
        """Check basic collection statistics"""
        try:
            count = self.collection.count()
            logger.info(f"\n{'='*80}")
            logger.info("COLLECTION HEALTH CHECK")
            logger.info(f"{'='*80}")
            logger.info(f"Total documents: {count}")
            
            if count == 0:
                logger.error("ERROR: Collection is empty! Data not processed.")
                return False
            
            # Get sample documents
            sample = self.collection.get(limit=5)
            logger.info(f"\nSample documents (first 5):")
            for i, (doc_id, meta, content) in enumerate(zip(
                sample['ids'],
                sample['metadatas'],
                sample['documents']
            )):
                logger.info(f"\n[Document {i+1}]")
                logger.info(f"ID: {doc_id}")
                logger.info(f"Mission: {meta.get('mission', 'N/A')}")
                logger.info(f"Source: {meta.get('source', 'N/A')}")
                logger.info(f"Content (first 200 chars): {content[:200]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking collection: {e}")
            return False
    
    def test_exact_phrases(self):
        """Test with exact phrases from documents"""
        exact_phrases = [
            "Apollo/Saturn Launch Control",
            "T minus",
            "countdown",
            "spacecraft",
            "launch",
            "ignition",
            "Neil Armstrong",
            "Buzz Aldrin",
            "Apollo 11",
            "Apollo 13",
            "Challenger",
            "liftoff",
            "engines running",
            "command module",
            "lunar module",
            "Eagle",
            "Columbia",
        ]
        
        logger.info(f"\n{'='*80}")
        logger.info("TESTING EXACT PHRASES FROM DOCUMENTS")
        logger.info(f"{'='*80}\n")
        
        results_summary = {
            'highly_relevant': 0,
            'relevant': 0,
            'somewhat_relevant': 0,
            'not_relevant': 0,
            'failed': []
        }
        
        for phrase in exact_phrases:
            try:
                results = self.collection.query(
                    query_texts=[phrase],
                    n_results=3,
                    include=['documents', 'distances', 'metadatas']
                )
                
                docs = results.get('documents', [[]])[0]
                distances = results.get('distances', [[]])[0]
                metadatas = results.get('metadatas', [[]])[0]
                
                if not docs:
                    logger.info(f"[{phrase}] NO_RESULTS")
                    results_summary['failed'].append(phrase)
                    continue
                
                avg_dist = sum(distances) / len(distances) if distances else 999
                
                if avg_dist < 0.3:
                    status = "[HIGHLY_RELEVANT]"
                    results_summary['highly_relevant'] += 1
                elif avg_dist < 0.5:
                    status = "[RELEVANT]"
                    results_summary['relevant'] += 1
                elif avg_dist < 0.7:
                    status = "[SOMEWHAT_RELEVANT]"
                    results_summary['somewhat_relevant'] += 1
                else:
                    status = "[NOT_RELEVANT]"
                    results_summary['not_relevant'] += 1
                
                logger.info(f"[{phrase}] {status} (Distance: {avg_dist:.4f})")
                logger.info(f"  Top Result: {docs[0][:150]}...")
                logger.info(f"  Source: {metadatas[0].get('source', 'N/A')}")
                
            except Exception as e:
                logger.error(f"[{phrase}] ERROR: {e}")
                results_summary['failed'].append(phrase)
        
        # Summary
        logger.info(f"\n{'='*80}")
        logger.info("EXACT PHRASE TEST SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Highly Relevant: {results_summary['highly_relevant']}")
        logger.info(f"Relevant: {results_summary['relevant']}")
        logger.info(f"Somewhat Relevant: {results_summary['somewhat_relevant']}")
        logger.info(f"Not Relevant: {results_summary['not_relevant']}")
        logger.info(f"Failed: {len(results_summary['failed'])}")
        
        if results_summary['failed']:
            logger.info(f"Failed phrases: {results_summary['failed']}")
        
        return results_summary
    
    def test_simple_queries(self):
        """Test with simple, specific queries"""
        queries = [
            "Apollo 11",
            "countdown",
            "launch",
            "spacecraft",
            "Armstrong",
            "Lovell",
            "Scobie",
            "ignition",
            "Apollo 13",
            "Challenger",
            "Houston",
            "Control",
        ]
        
        logger.info(f"\n{'='*80}")
        logger.info("TESTING SIMPLE QUERIES")
        logger.info(f"{'='*80}\n")
        
        for query in queries:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=3,
                    include=['documents', 'distances', 'metadatas']
                )
                
                docs = results.get('documents', [[]])[0]
                distances = results.get('distances', [[]])[0]
                metadatas = results.get('metadatas', [[]])[0]
                
                if not docs:
                    logger.info(f"[{query}] NO_RESULTS")
                    continue
                
                avg_dist = sum(distances) / len(distances) if distances else 999
                
                if avg_dist < 0.5:
                    status = "GOOD"
                else:
                    status = "POOR"
                
                logger.info(f"[{query}] {status} (Distance: {avg_dist:.4f})")
                for i, (doc, dist, meta) in enumerate(zip(docs, distances, metadatas)):
                    logger.info(f"  Result {i+1} (dist {dist:.4f}): {doc[:100]}... [source: {meta.get('source', 'N/A')}]")
                
            except Exception as e:
                logger.error(f"[{query}] ERROR: {e}")
    
    def examine_chunk_quality(self):
        """Examine the quality of chunks"""
        logger.info(f"\n{'='*80}")
        logger.info("EXAMINING CHUNK QUALITY")
        logger.info(f"{'='*80}\n")
        
        try:
            # Get all documents with metadata
            all_docs = self.collection.get(limit=100)
            
            if not all_docs['documents']:
                logger.error("No documents found in collection")
                return
            
            # Analyze chunk characteristics
            chunk_lengths = []
            missions_count = {}
            sources_count = {}
            
            for doc, meta in zip(all_docs['documents'], all_docs['metadatas']):
                chunk_lengths.append(len(doc))
                mission = meta.get('mission', 'unknown')
                source = meta.get('source', 'unknown')
                
                missions_count[mission] = missions_count.get(mission, 0) + 1
                sources_count[source] = sources_count.get(source, 0) + 1
            
            logger.info(f"\nChunk Length Statistics:")
            logger.info(f"  Min: {min(chunk_lengths)} chars")
            logger.info(f"  Max: {max(chunk_lengths)} chars")
            logger.info(f"  Avg: {sum(chunk_lengths) / len(chunk_lengths):.0f} chars")
            
            logger.info(f"\nMissions in collection:")
            for mission, count in missions_count.items():
                logger.info(f"  {mission}: {count} chunks")
            
            logger.info(f"\nSources in collection:")
            for source, count in sorted(sources_count.items()):
                logger.info(f"  {source}: {count} chunks")
            
            # Show some example chunks
            logger.info(f"\nExample chunks (first 5):")
            for i, (doc, meta) in enumerate(zip(all_docs['documents'][:5], all_docs['metadatas'][:5])):
                logger.info(f"\n[Chunk {i+1}]")
                logger.info(f"  Mission: {meta.get('mission')}")
                logger.info(f"  Source: {meta.get('source')}")
                logger.info(f"  Length: {len(doc)} chars")
                logger.info(f"  Content: {doc[:300]}...")
            
        except Exception as e:
            logger.error(f"Error examining chunks: {e}")
    
    def test_distance_distribution(self):
        """Check the distance distribution for a query"""
        logger.info(f"\n{'='*80}")
        logger.info("TESTING DISTANCE DISTRIBUTION")
        logger.info(f"{'='*80}\n")
        
        test_query = "Apollo 11"
        
        try:
            results = self.collection.query(
                query_texts=[test_query],
                n_results=10,
                include=['documents', 'distances', 'metadatas']
            )
            
            docs = results.get('documents', [[]])[0]
            distances = results.get('distances', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            logger.info(f"Query: '{test_query}'")
            logger.info(f"Retrieved {len(docs)} results")
            logger.info(f"\nDistance Distribution:")
            
            for i, (doc, dist, meta) in enumerate(zip(docs, distances, metadatas)):
                logger.info(f"\n[Result {i+1}] Distance: {dist:.4f}")
                logger.info(f"  Source: {meta.get('source')}")
                logger.info(f"  Mission: {meta.get('mission')}")
                logger.info(f"  Content: {doc[:200]}...")
            
            # Summary statistics
            logger.info(f"\nDistance Statistics:")
            logger.info(f"  Min: {min(distances):.4f}")
            logger.info(f"  Max: {max(distances):.4f}")
            logger.info(f"  Avg: {sum(distances) / len(distances):.4f}")
            
        except Exception as e:
            logger.error(f"Error testing distance distribution: {e}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Diagnostic Tool for RAG Collection')
    parser.add_argument('--chroma-dir', default='./chroma_db_openai')
    parser.add_argument('--collection', default='nasa_space_missions_text')
    parser.add_argument('--test', choices=['health', 'phrases', 'simple', 'chunks', 'distance', 'all'],
                       default='all', help='Which test to run')
    
    args = parser.parse_args()
    
    diag = CollectionDiagnostics(args.chroma_dir, args.collection)
    
    if args.test in ['health', 'all']:
        diag.check_collection_health()
    
    if args.test in ['phrases', 'all']:
        diag.test_exact_phrases()
    
    if args.test in ['simple', 'all']:
        diag.test_simple_queries()
    
    if args.test in ['chunks', 'all']:
        diag.examine_chunk_quality()
    
    if args.test in ['distance', 'all']:
        diag.test_distance_distribution()


if __name__ == "__main__":
    main()
