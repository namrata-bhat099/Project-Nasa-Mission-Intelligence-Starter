"""
Simple Query Validator - Easy-to-use helper for testing RAG collection queries
Can be imported and used programmatically or via command line
"""

import chromadb
from chromadb.config import Settings
from typing import Dict, List, Tuple, Any
import logging

# Configure logging with UTF-8 encoding for Windows compatibility
logging.basicConfig(level=logging.INFO, format='%(message)s', handlers=[
    logging.FileHandler('simple_validation.log', encoding='utf-8'),
    logging.StreamHandler()
])
logger = logging.getLogger(__name__)


class SimpleValidator:
    """Minimal validator for quick query testing"""
    
    def __init__(self, chroma_dir: str = "./chroma_db_openai",
                 collection_name: str = "nasa_space_missions_text"):
        """Initialize with ChromaDB collection"""
        self.client = chromadb.PersistentClient(
            path=chroma_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_collection(name=collection_name)
    
    def query(self, question: str, n_results: int = 5) -> Dict[str, Any]:
        """Query the collection and return results with relevance info"""
        results = self.collection.query(
            query_texts=[question],
            n_results=n_results,
            include=['documents', 'distances', 'metadatas']
        )
        
        docs = results['documents'][0]
        distances = results['distances'][0]
        metadatas = results['metadatas'][0]
        
        return {
            'question': question,
            'results_count': len(docs),
            'avg_distance': sum(distances) / len(distances) if distances else None,
            'results': [
                {
                    'rank': i + 1,
                    'distance': distances[i],
                    'relevance': self._distance_to_relevance(distances[i]),
                    'source': metadatas[i].get('source', 'N/A'),
                    'mission': metadatas[i].get('mission', 'N/A'),
                    'document_category': metadatas[i].get('document_category', 'N/A'),
                    'chunk_index': metadatas[i].get('chunk_index', 'N/A'),
                    'text_preview': docs[i][:300] + ('...' if len(docs[i]) > 300 else '')
                }
                for i in range(len(docs))
            ]
        }
    
    def validate_batch(self, queries: List[str]) -> Dict[str, Any]:
        """Validate a batch of queries and return summary statistics"""
        results = []
        stats = {'high': 0, 'good': 0, 'ok': 0, 'poor': 0}
        
        for query in queries:
            result = self.query(query, n_results=3)
            results.append(result)
            
            if result['avg_distance'] is not None:
                if result['avg_distance'] < 0.3:
                    stats['high'] += 1
                elif result['avg_distance'] < 0.5:
                    stats['good'] += 1
                elif result['avg_distance'] < 0.7:
                    stats['ok'] += 1
                else:
                    stats['poor'] += 1
        
        return {
            'total_queries': len(queries),
            'queries_tested': results,
            'summary': stats,
            'success_rate': (stats['high'] + stats['good']) / len(queries) * 100 if queries else 0
        }
    
    def _distance_to_relevance(self, distance: float) -> str:
        """Convert distance score to human-readable relevance"""
        if distance < 0.3:
            return '[HIGHLY_RELEVANT]'
        elif distance < 0.5:
            return '[RELEVANT]'
        elif distance < 0.7:
            return '[SOMEWHAT_RELEVANT]'
        else:
            return '[NOT_RELEVANT]'
    
    def print_results(self, query_results: Dict[str, Any], show_full_text: bool = False):
        """Pretty print query results"""
        print(f"\n{'='*80}")
        print(f"QUESTION: {query_results['question']}")
        print(f"{'='*80}")
        print(f"Results found: {query_results['results_count']}")
        print(f"Average distance: {query_results['avg_distance']:.4f}")
        print(f"-" * 80)
        
        for result in query_results['results']:
            print(f"\n[Result #{result['rank']}] {result['relevance']}")
            print(f"Distance: {result['distance']:.4f}")
            print(f"Source: {result['source']} | Mission: {result['mission']}")
            print(f"Category: {result['document_category']} | Chunk: {result['chunk_index']}")
            print(f"Text: {result['text_preview']}")


# Pre-defined test query sets
QUICK_TESTS = {
    'missions_101': [
        "Tell me about Apollo 11",
        "Apollo 13 oxygen tank crisis",
        "Challenger space shuttle mission"
    ],
    'technical_101': [
        "Guidance system navigation computer",
        "Life support oxygen systems",
        "Fuel cells power generation"
    ],
    'crew_101': [
        "Neil Armstrong moonwalk",
        "Buzz Aldrin lunar module pilot",
        "Jim Lovell Apollo 13"
    ],
    'events_101': [
        "What was the oxygen tank problem",
        "Launch procedures countdown",
        "Lunar landing procedures"
    ]
}


def main():
    """Simple CLI for quick testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quick RAG Query Validator')
    parser.add_argument('--query', help='Single query to test')
    parser.add_argument('--test-set', choices=QUICK_TESTS.keys(), help='Run predefined test set')
    parser.add_argument('--chroma-dir', default='./chroma_db_openai', help='ChromaDB directory')
    parser.add_argument('--collection', default='nasa_space_missions_text', help='Collection name')
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = SimpleValidator(args.chroma_dir, args.collection)
    
    if args.query:
        # Single query
        results = validator.query(args.query, n_results=5)
        validator.print_results(results)
    
    elif args.test_set:
        # Predefined test set
        queries = QUICK_TESTS[args.test_set]
        print(f"\nRunning test set: {args.test_set}")
        print(f"Queries: {len(queries)}\n")
        
        for query in queries:
            results = validator.query(query, n_results=3)
            validator.print_results(results)
        
        # Summary
        validation = validator.validate_batch(queries)
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        print(f"Highly Relevant: {validation['summary']['high']}")
        print(f"Relevant: {validation['summary']['good']}")
        print(f"Somewhat Relevant: {validation['summary']['ok']}")
        print(f"Not Relevant: {validation['summary']['poor']}")
        print(f"Success Rate: {validation['success_rate']:.1f}%")
    
    else:
        # Interactive mode
        print("RAG Query Validator - Interactive Mode")
        print("Type 'quit' to exit, 'help' for test sets\n")
        
        while True:
            query = input("Enter query: ").strip()
            
            if query.lower() == 'quit':
                break
            elif query.lower() == 'help':
                print("Available test sets:")
                for key in QUICK_TESTS.keys():
                    print(f"  {key}: {QUICK_TESTS[key]}")
                continue
            elif query.lower().startswith('set:'):
                test_set = query[4:].strip()
                if test_set in QUICK_TESTS:
                    for test_query in QUICK_TESTS[test_set]:
                        results = validator.query(test_query, n_results=3)
                        validator.print_results(results)
                continue
            
            if query:
                results = validator.query(query, n_results=5)
                validator.print_results(results)


if __name__ == '__main__':
    main()
