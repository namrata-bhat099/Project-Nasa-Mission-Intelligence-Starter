"""
Adapted Query Validator for NASA Mission RAG Collection
Queries are based on actual content found in the data_text files
"""

import logging
from pathlib import Path
import chromadb
from chromadb.config import Settings
from typing import Dict, List, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('validation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AdaptedQueryValidator:
    """Validator using queries matched to actual document content"""
    
    def __init__(self, chroma_dir: str = "./chroma_db_openai", 
                 collection_name: str = "nasa_space_missions_text"):
        self.client = chromadb.PersistentClient(
            path=chroma_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_collection(name=collection_name)
        logger.info(f"Connected. Total documents: {self.collection.count()}")
    
    def get_countdown_and_launch_queries(self) -> Dict[str, str]:
        """Queries about countdown and launch procedures"""
        return {
            'apollo11_countdown': 'Apollo 11 countdown T minus launch',
            'liftoff_procedures': 'liftoff engines running ignition sequence',
            'launch_control': 'Launch Control Houston firing room',
            'swing_arm_procedures': 'swing arm spacecraft hatch retracted',
            'escape_tower': 'escape tower spacecraft emergency',
            'Saturn_V_launch': 'Saturn V launch vehicle stages propellants',
            'propellant_loading': 'propellant loading liquid oxygen hydrogen',
            'spacecraft_checkout': 'spacecraft checkout procedures test',
            'countdown_abort_checks': 'abort checks launch director GO',
        }
    
    def get_systems_and_instrumentation_queries(self) -> Dict[str, str]:
        """Queries about spacecraft systems"""
        return {
            'reaction_control_system': 'reaction control system thrusters service module',
            'guidance_system': 'guidance system tracking beacons instrument unit',
            'fuel_cells': 'fuel cells power spacecraft internal power',
            'command_module': 'command module Columbia spacecraft',
            'lunar_module': 'lunar module Eagle ascent stage descent stage',
            'telemetry': 'telemetry tracking ground control',
            'stabilization_control': 'stabilization control system rotational hand controller',
            'batteries': 'batteries internal power ascent stage descent stage',
            'pressurization': 'pressurization reaction control helium pressure',
        }
    
    def get_crew_and_communication_queries(self) -> Dict[str, str]:
        """Queries about crew members and communications"""
        return {
            'neil_armstrong': 'Neil Armstrong commander spacecraft check',
            'buzz_aldrin': 'Buzz Aldrin middle seat test conductor',
            'mike_collins': 'Mike Collins astronaut spacecraft',
            'capsule_communicator': 'Capsule Communication CAP COMM Houston',
            'mission_control_houston': 'Mission Control Houston flight director',
            'test_conductor': 'test conductor spacecraft procedures',
            'astronaut_crew': 'astronauts aboard spacecraft procedures',
            'launch_director': 'launch director GO for launch',
            'skip_chauvin': 'Skip Chauvin spacecraft test conductor',
        }
    
    def get_mission_phase_queries(self) -> Dict[str, str]:
        """Queries about specific mission phases from actual documents"""
        return {
            'final_launch_preparations': 'final preparations launch pad spacecraft ready',
            't_minus_ten_minutes': 'T minus 10 minutes countdown Apollo',
            't_minus_five_minutes': 'T minus 5 minutes swing arm retracted',
            'automatic_sequence': 'automatic sequence computer countdown',
            'powered_flight': 'powered flight engines thrust Saturn V',
            'separation': 'separation command module lunar module orbit',
            'vehicle_checkout': 'vehicle checkout systems status GO',
            'pressurization_tanks': 'pressurization oxidizer tanks stages',
        }
    
    def get_apollo_13_queries(self) -> Dict[str, str]:
        """Queries specific to Apollo 13 data"""
        return {
            'apollo_13_launch': 'Apollo 13 lift-off ignition countdown',
            'apollo_13_yaw_roll': 'yaw program roll procedure Apollo 13',
            'apollo_13_command_module': 'Command Module onboard Apollo 13',
            'apollo_13_lunar_module': 'lunar module pilot Fred Haise',
            'jim_lovell': 'Jim Lovell commander Apollo 13',
            'jack_swigert': 'Jack Swigert command module pilot',
            'apollo_13_crew': 'Apollo 13 flight crew procedures',
        }
    
    def get_challenger_queries(self) -> Dict[str, str]:
        """Queries specific to Challenger data"""
        return {
            'challenger_mission': 'Challenger STS-51L mission launch',
            'challenger_crew': 'Dick Scobie Mike Smith Judy Resnick',
            'krista_mcauliffe': 'Krista McAuliffe teacher space participant',
            'challenger_countdown': 'Challenger countdown launch control',
            'challenger_launch_window': 'launch window 9:37 eastern',
            'challenger_weather': 'weather conditions launch pad winds',
            'challenger_external_tank': 'external tank liquid oxygen hydrogen',
            'challenger_ice_inspection': 'ice inspection team frost formation',
            'challenger_orbiter': 'Orbiter Challenger crew module',
        }
    
    def query_collection(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """Execute a query"""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                include=['documents', 'distances', 'metadatas']
            )
            return results
        except Exception as e:
            logger.error(f"Error querying: {e}")
            return {'error': str(e)}
    
    def evaluate_relevance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate query results"""
        if 'error' in results:
            return {'status': 'ERROR', 'relevance': 'ERROR', 'distance': None}
        
        docs = results.get('documents', [[]])[0]
        distances = results.get('distances', [[]])[0]
        
        if not docs:
            return {'status': 'NO_RESULTS', 'relevance': 'NO_RESULTS', 'distance': None}
        
        avg_dist = sum(distances) / len(distances) if distances else 999
        
        if avg_dist < 0.3:
            relevance = '[HIGHLY_RELEVANT]'
        elif avg_dist < 0.5:
            relevance = '[RELEVANT]'
        elif avg_dist < 0.7:
            relevance = '[SOMEWHAT_RELEVANT]'
        else:
            relevance = '[NOT_RELEVANT]'
        
        return {
            'status': 'SUCCESS',
            'relevance': relevance,
            'distance': avg_dist,
            'result_count': len(docs),
            'source': results['metadatas'][0][0].get('source', 'N/A') if results['metadatas'] else 'N/A'
        }
    
    def run_category_tests(self, query_dict: Dict[str, str], 
                          category_name: str) -> List[Dict[str, Any]]:
        """Run tests for a category"""
        logger.info(f"\n{'='*80}")
        logger.info(f"TESTING: {category_name}")
        logger.info(f"{'='*80}\n")
        
        results_list = []
        success_count = 0
        
        for test_name, query_text in query_dict.items():
            logger.info(f"[{test_name}]")
            logger.info(f"Query: {query_text}")
            
            results = self.query_collection(query_text, n_results=5)
            evaluation = self.evaluate_relevance(results)
            
            logger.info(f"Relevance: {evaluation['relevance']}")
            if evaluation.get('distance') is not None:
                logger.info(f"Distance: {evaluation['distance']:.4f}")
            logger.info(f"Source: {evaluation.get('source', 'N/A')}")
            logger.info("-" * 80)
            
            if evaluation['relevance'] in ['HIGHLY_RELEVANT ✓✓', 'RELEVANT ✓']:
                success_count += 1
            
            results_list.append({
                'test_name': test_name,
                'query': query_text,
                'evaluation': evaluation
            })
        
        category_rate = (success_count / len(query_dict) * 100) if query_dict else 0
        logger.info(f"\nCategory Success Rate: {category_rate:.1f}%\n")
        
        return results_list
    
    def run_all_validations(self) -> Dict[str, Any]:
        """Run all validation tests"""
        all_results = {
            'total_tests': 0,
            'categories': {},
            'summary': {
                'highly_relevant': 0,
                'relevant': 0,
                'somewhat_relevant': 0,
                'not_relevant': 0,
                'no_results': 0,
                'errors': 0
            }
        }
        
        test_categories = [
            ('Countdown and Launch', self.get_countdown_and_launch_queries()),
            ('Systems and Instrumentation', self.get_systems_and_instrumentation_queries()),
            ('Crew and Communication', self.get_crew_and_communication_queries()),
            ('Mission Phases', self.get_mission_phase_queries()),
            ('Apollo 13 Specific', self.get_apollo_13_queries()),
            ('Challenger Specific', self.get_challenger_queries()),
        ]
        
        for category_name, query_dict in test_categories:
            results = self.run_category_tests(query_dict, category_name)
            all_results['categories'][category_name] = results
            all_results['total_tests'] += len(results)
            
            for result in results:
                relevance = result['evaluation']['relevance']
                if 'HIGHLY_RELEVANT' in relevance:
                    all_results['summary']['highly_relevant'] += 1
                elif 'RELEVANT' in relevance and 'NOT' not in relevance:
                    all_results['summary']['relevant'] += 1
                elif 'SOMEWHAT_RELEVANT' in relevance:
                    all_results['summary']['somewhat_relevant'] += 1
                elif 'NOT_RELEVANT' in relevance:
                    all_results['summary']['not_relevant'] += 1
                elif 'NO_RESULTS' in relevance:
                    all_results['summary']['no_results'] += 1
                elif 'ERROR' in relevance:
                    all_results['summary']['errors'] += 1
        
        return all_results
    
    def print_summary(self, all_results: Dict[str, Any]):
        """Print summary"""
        logger.info(f"\n{'='*80}")
        logger.info("VALIDATION SUMMARY")
        logger.info(f"{'='*80}\n")
        
        stats = all_results['summary']
        total = all_results['total_tests']
        
        logger.info(f"Total Tests: {total}")
        logger.info(f"Highly Relevant ✓✓: {stats['highly_relevant']}")
        logger.info(f"Relevant ✓: {stats['relevant']}")
        logger.info(f"Somewhat Relevant ◐: {stats['somewhat_relevant']}")
        logger.info(f"Not Relevant ✗: {stats['not_relevant']}")
        logger.info(f"No Results: {stats['no_results']}")
        logger.info(f"Errors: {stats['errors']}")
        
        if total > 0:
            success = (stats['highly_relevant'] + stats['relevant']) / total * 100
            logger.info(f"\n✓ Success Rate (Highly + Relevant): {success:.1f}%")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Adapted RAG Query Validator')
    parser.add_argument('--chroma-dir', default='./chroma_db_openai')
    parser.add_argument('--collection', default='nasa_space_missions_text')
    parser.add_argument('--category', choices=['countdown', 'systems', 'crew', 'phases', 
                                               'apollo13', 'challenger', 'all'],
                       default='all')
    parser.add_argument('--query', help='Custom query')
    
    args = parser.parse_args()
    
    validator = AdaptedQueryValidator(args.chroma_dir, args.collection)
    
    if args.query:
        logger.info(f"Query: {args.query}")
        results = validator.query_collection(args.query, n_results=5)
        evaluation = validator.evaluate_relevance(results)
        logger.info(f"Relevance: {evaluation['relevance']}")
        logger.info(f"Distance: {evaluation.get('distance', 'N/A')}")
    
    elif args.category == 'all':
        all_results = validator.run_all_validations()
        validator.print_summary(all_results)
    
    else:
        category_mapping = {
            'countdown': ('Countdown and Launch', validator.get_countdown_and_launch_queries()),
            'systems': ('Systems and Instrumentation', validator.get_systems_and_instrumentation_queries()),
            'crew': ('Crew and Communication', validator.get_crew_and_communication_queries()),
            'phases': ('Mission Phases', validator.get_mission_phase_queries()),
            'apollo13': ('Apollo 13 Specific', validator.get_apollo_13_queries()),
            'challenger': ('Challenger Specific', validator.get_challenger_queries()),
        }
        
        cat_name, queries = category_mapping[args.category]
        results = validator.run_category_tests(queries, cat_name)


if __name__ == "__main__":
    main()
