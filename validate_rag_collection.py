"""
Validation Script for NASA Mission RAG Collection
This script demonstrates how to query the ChromaDB collection and validate results
with relevant test queries covering different aspects of the mission data.
"""

import logging
from pathlib import Path
import chromadb
from chromadb.config import Settings
from typing import Dict, List, Any, Tuple
import json

# Configure logging with UTF-8 encoding for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('validation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class QueryValidator:
    """Validator for RAG collection queries"""
    
    def __init__(self, chroma_dir: str = "./chroma_db_openai", 
                 collection_name: str = "nasa_space_missions_text"):
        """Initialize validator with ChromaDB collection"""
        self.chromadb_client = chromadb.PersistentClient(
            path=chroma_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.chromadb_client.get_collection(name=collection_name)
        logger.info(f"Connected to collection: {collection_name}")
        logger.info(f"Total documents: {self.collection.count()}")
    
    # ==================== MISSION-SPECIFIC QUERIES ====================
    def get_mission_queries(self) -> Dict[str, str]:
        """Queries focused on specific missions - using actual document terminology"""
        return {
            'apollo_11_countdown': 'Apollo 11 countdown T minus launch control',
            'apollo_11_liftoff': 'Apollo 11 liftoff ignition engines running',
            'apollo_11_astronauts': 'Neil Armstrong Buzz Aldrin Mike Collins spacecraft',
            'apollo_11_columbia_eagle': 'Columbia Eagle command module lunar module',
            'apollo_13_launch': 'Apollo 13 lift-off ignition onboard voice transcription',
            'apollo_13_yaw_roll': 'Apollo 13 yaw program roll procedure',
            'apollo_13_crew': 'Jim Lovell Jack Swigert Fred Haise Apollo 13',
            'challenger_sts_51l': 'Challenger STS-51L mission launch control',
            'challenger_crew': 'Dick Scobie Mike Smith Judy Resnick Challenger',
            'krista_mcauliffe': 'Krista McAuliffe teacher space participant Challenger',
        }
    
    # ==================== TECHNICAL QUERIES ====================
    def get_technical_queries(self) -> Dict[str, str]:
        """Queries about technical systems and components"""
        return {
            'guidance_system': 'guidance system tracking beacons instrument unit',
            'reaction_control': 'reaction control system thrusters service module',
            'fuel_cells': 'fuel cells power spacecraft internal power',
            'lunar_module': 'lunar module Eagle ascent stage descent stage',
            'command_module': 'command module Columbia spacecraft checkout',
            'propellants': 'propellant loading liquid oxygen liquid hydrogen',
            'telemetry': 'telemetry ground control Houston tracking',
            'stabilization': 'stabilization control system rotational hand controller',
            'batteries': 'batteries internal power spacecraft systems',
            'pressurization': 'pressurization tanks helium pressure systems',
        }
    
    # ==================== MISSION PHASE QUERIES ====================
    def get_mission_phase_queries(self) -> Dict[str, str]:
        """Queries about different phases of missions"""
        return {
            'launch_sequence': 'launch sequence countdown T minus procedures',
            'countdown': 'countdown Apollo launch control firing room',
            'liftoff': 'liftoff engines running ignition Saturn V thrust',
            'automatic_sequence': 'automatic sequence computer ground master',
            'powered_flight': 'powered flight first stage S-IC engines',
            'separation': 'separation command module lunar module orbit',
            'lunar_operations': 'lunar orbit insertion descent procedures',
            'surface_activities': 'spacecraft checkout procedures test systems',
            'return_trajectory': 'return trajectory Earth mission control',
            'swing_arm': 'swing arm spacecraft hatch procedures',
        }
    
    # ==================== EVENT/INCIDENT QUERIES ====================
    def get_incident_queries(self) -> Dict[str, str]:
        """Queries about specific events, problems, and incidents"""
        return {
            'launch_hold': 'launch hold countdown procedures postpone',
            'weather_conditions': 'weather conditions winds launch pad',
            'abort_checks': 'abort checks launch director GO',
            'destruct_system': 'destruct system range safety command',
            'manual_procedures': 'manual procedures test conductor spacecraft',
            'emergency_detection': 'emergency detection system spacecraft',
            'system_checkout': 'system checkout procedures status GO',
            'leaky_valve': 'valve hydrogen fuel supply bypass',
            'pyrotechnics': 'pyrotechnics systems armed escape tower',
        }
    
    # ==================== CREW AND ACTIVITIES QUERIES ====================
    def get_crew_queries(self) -> Dict[str, str]:
        """Queries about crew members and their activities"""
        return {
            'neil_armstrong': 'Neil Armstrong commander spacecraft procedures',
            'buzz_aldrin': 'Buzz Aldrin middle seat reaction control pressurization',
            'michael_collins': 'Mike Collins astronaut spacecraft checkout',
            'jim_lovell': 'Jim Lovell commander Apollo 13 flight crew',
            'fred_haise': 'Fred Haise lunar module pilot Apollo 13',
            'jack_swigert': 'Jack Swigert command module pilot Apollo 13',
            'test_conductor': 'test conductor spacecraft Skip Chauvin procedures',
            'capsule_communicator': 'Capsule Communication CAP COMM Houston mission control',
            'launch_director': 'launch director GO for launch procedures',
            'crew_communications': 'crew communications mission control procedures',
        }
    
    # ==================== SYSTEMS AND CONTROLS QUERIES ====================
    def get_science_queries(self) -> Dict[str, str]:
        """Queries about systems and technical operations"""
        return {
            'external_tank': 'external tank propellant loading cryogenic',
            'orbital_operations': 'orbital operations procedures tracking',
            'vehicle_systems': 'vehicle systems configuration preflight',
            'ice_inspection': 'ice inspection team frost formation',
            'launch_pad': 'launch pad preparation procedures complex 39',
            'saturn_five': 'Saturn V launch vehicle stages thrust',
            'orbiter_systems': 'orbiter systems preflight checkout',
            'spacecraft_power': 'spacecraft power systems internal power',
            'ground_support': 'ground support equipment launch team',
        }
    
    # ==================== PROCEDURAL QUERIES ====================
    def get_flight_plan_queries(self) -> Dict[str, str]:
        """Queries about procedures and operations"""
        return {
            'preflight_preparation': 'preflight preparation countdown procedures',
            'vehicle_checkout': 'vehicle checkout systems status firing room',
            'crew_procedures': 'crew procedures astronaut breakfast preparations',
            'telemetry_checks': 'telemetry checks ground control tracking',
            'propellant_status': 'propellant status oxidizer tanks pressurization',
            'range_safety': 'range safety command destruct procedures',
            'communications_checks': 'communications checks antennas transponders',
            'launch_operations': 'launch operations procedures team status',
            'crew_access': 'crew access procedures spacecraft hatch entry',
        }
    
    def query_collection(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """Execute a query on the collection"""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                include=['documents', 'distances', 'metadatas']
            )
            return results
        except Exception as e:
            logger.error(f"Error querying collection: {e}")
            return {'error': str(e)}
    
    def evaluate_relevance(self, results: Dict[str, Any], 
                          query_text: str = "") -> Dict[str, Any]:
        """
        Evaluate if query results are relevant
        ChromaDB cosine distance: 0 = perfect match, 2 = completely different
        """
        if 'error' in results:
            return {
                'status': 'ERROR',
                'message': results['error'],
                'result_count': 0,
                'avg_distance': None,
                'relevance': 'ERROR'
            }
        
        docs = results.get('documents', [[]])[0]
        distances = results.get('distances', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        
        if not docs:
            return {
                'status': 'NO_RESULTS',
                'message': 'No documents found',
                'result_count': 0,
                'avg_distance': None,
                'relevance': 'NO_RESULTS'
            }
        
        avg_distance = sum(distances) / len(distances) if distances else float('inf')
        
        # Determine relevance level
        if avg_distance < 0.3:
            relevance = '[HIGHLY_RELEVANT]'
        elif avg_distance < 0.5:
            relevance = '[RELEVANT]'
        elif avg_distance < 0.7:
            relevance = '[SOMEWHAT_RELEVANT]'
        else:
            relevance = '[NOT_RELEVANT]'
        
        return {
            'status': 'SUCCESS',
            'result_count': len(docs),
            'avg_distance': avg_distance,
            'top_distances': distances[:3],
            'relevance': relevance,
            'first_result_preview': docs[0][:200] if docs else '',
            'first_source': metadatas[0].get('source', 'N/A') if metadatas else 'N/A',
            'first_mission': metadatas[0].get('mission', 'N/A') if metadatas else 'N/A',
        }
    
    def run_test_queries(self, query_dict: Dict[str, str], 
                        category_name: str = "Test Category") -> List[Dict[str, Any]]:
        """Run a set of test queries and return results"""
        logger.info(f"\n{'='*80}")
        logger.info(f"TESTING: {category_name}")
        logger.info(f"{'='*80}\n")
        
        results_list = []
        
        for test_name, query_text in query_dict.items():
            logger.info(f"[{test_name}]")
            logger.info(f"Query: {query_text}")
            
            # Execute query
            results = self.query_collection(query_text, n_results=5)
            
            # Evaluate relevance
            evaluation = self.evaluate_relevance(results, query_text)
            
            logger.info(f"Status: {evaluation['status']}")
            logger.info(f"Relevance: {evaluation['relevance']}")
            logger.info(f"Results: {evaluation['result_count']}")
            if evaluation.get('avg_distance') is not None:
                logger.info(f"Avg Distance: {evaluation['avg_distance']:.4f}")
                logger.info(f"Top Distances: {[f'{d:.4f}' for d in evaluation.get('top_distances', [])]}")
            logger.info(f"Source: {evaluation.get('first_source', 'N/A')}")
            logger.info(f"Mission: {evaluation.get('first_mission', 'N/A')}")
            if evaluation['first_result_preview']:
                logger.info(f"Preview: {evaluation['first_result_preview']}...")
            logger.info("-" * 80)
            
            results_list.append({
                'test_name': test_name,
                'query': query_text,
                'evaluation': evaluation
            })
        
        return results_list
    
    def run_all_validations(self) -> Dict[str, Any]:
        """Run all validation test categories"""
        all_results = {
            'total_tests': 0,
            'categories': {},
            'summary_stats': {
                'highly_relevant': 0,
                'relevant': 0,
                'somewhat_relevant': 0,
                'not_relevant': 0,
                'no_results': 0,
                'errors': 0
            }
        }
        
        # Test each category
        test_categories = [
            ('Mission Queries', self.get_mission_queries()),
            ('Technical Queries', self.get_technical_queries()),
            ('Mission Phase Queries', self.get_mission_phase_queries()),
            ('Incident/Event Queries', self.get_incident_queries()),
            ('Crew Queries', self.get_crew_queries()),
            ('Systems and Controls Queries', self.get_science_queries()),
            ('Procedural Queries', self.get_flight_plan_queries()),
        ]
        
        for category_name, query_dict in test_categories:
            results = self.run_test_queries(query_dict, category_name)
            all_results['categories'][category_name] = results
            all_results['total_tests'] += len(results)
            
            # Update summary stats
            for result in results:
                relevance = result['evaluation']['relevance']
                if 'HIGHLY_RELEVANT' in relevance:
                    all_results['summary_stats']['highly_relevant'] += 1
                elif 'RELEVANT' in relevance and 'NOT' not in relevance:
                    all_results['summary_stats']['relevant'] += 1
                elif 'SOMEWHAT_RELEVANT' in relevance:
                    all_results['summary_stats']['somewhat_relevant'] += 1
                elif 'NOT_RELEVANT' in relevance:
                    all_results['summary_stats']['not_relevant'] += 1
                elif 'NO_RESULTS' in relevance:
                    all_results['summary_stats']['no_results'] += 1
                elif 'ERROR' in relevance:
                    all_results['summary_stats']['errors'] += 1
        
        return all_results
    
    def print_summary(self, all_results: Dict[str, Any]):
        """Print summary of validation results"""
        logger.info(f"\n{'='*80}")
        logger.info("VALIDATION SUMMARY")
        logger.info(f"{'='*80}\n")
        
        stats = all_results['summary_stats']
        total = all_results['total_tests']
        
        logger.info(f"Total Tests: {total}")
        logger.info(f"Highly Relevant: {stats['highly_relevant']}")
        logger.info(f"Relevant: {stats['relevant']}")
        logger.info(f"Somewhat Relevant: {stats['somewhat_relevant']}")
        logger.info(f"Not Relevant: {stats['not_relevant']}")
        logger.info(f"No Results: {stats['no_results']}")
        logger.info(f"Errors: {stats['errors']}")
        
        if total > 0:
            success_rate = ((stats['highly_relevant'] + stats['relevant']) / total) * 100
            good_rate = ((stats['highly_relevant'] + stats['relevant'] + stats['somewhat_relevant']) / total) * 100
            logger.info(f"\n[SUCCESS] Success Rate (Highly + Relevant): {success_rate:.1f}%")
            logger.info(f"[SUCCESS] Good Rate (Highly + Relevant + Somewhat): {good_rate:.1f}%")


def main():
    """Main function to run validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate NASA Mission RAG Collection')
    parser.add_argument('--chroma-dir', default='./chroma_db_openai', 
                       help='ChromaDB directory path')
    parser.add_argument('--collection-name', default='nasa_space_missions_text',
                       help='Collection name')
    parser.add_argument('--category', choices=['missions', 'technical', 'phases', 'incidents', 
                                               'crew', 'science', 'flight_plan', 'all'],
                       default='all', help='Which category to test')
    parser.add_argument('--query', help='Run a single custom query')
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = QueryValidator(args.chroma_dir, args.collection_name)
    
    # Run tests based on selection
    if args.query:
        # Custom query
        logger.info(f"Running custom query: {args.query}")
        results = validator.query_collection(args.query, n_results=5)
        evaluation = validator.evaluate_relevance(results, args.query)
        logger.info(f"Results: {json.dumps(evaluation, indent=2, default=str)}")
    
    elif args.category == 'all':
        # Run all validations
        all_results = validator.run_all_validations()
        validator.print_summary(all_results)
    
    else:
        # Run specific category
        category_mapping = {
            'missions': ('Mission Queries', validator.get_mission_queries()),
            'technical': ('Technical Queries', validator.get_technical_queries()),
            'phases': ('Mission Phase Queries', validator.get_mission_phase_queries()),
            'incidents': ('Incident/Event Queries', validator.get_incident_queries()),
            'crew': ('Crew Queries', validator.get_crew_queries()),
            'science': ('Systems and Controls Queries', validator.get_science_queries()),
            'flight_plan': ('Procedural Queries', validator.get_flight_plan_queries()),
        }
        
        category_name, query_dict = category_mapping[args.category]
        results = validator.run_test_queries(query_dict, category_name)
        
        # Print category summary
        logger.info(f"\nCategory: {category_name}")
        logger.info(f"Tests: {len(results)}")


if __name__ == "__main__":
    main()
