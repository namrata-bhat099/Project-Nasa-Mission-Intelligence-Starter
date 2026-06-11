import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
import openai
from openai import OpenAI
import hashlib
import time
from datetime import datetime
import argparse
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_chunking.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ChromaEmbeddingPipelineTextOnly:
    """Pipeline for creating ChromaDB collections with OpenAI embeddings - Text files only"""

    def __init__(self,
                 chroma_persist_directory: str = "./chroma_db",
                 collection_name: str = "nasa_space_missions_text",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 batch_size: int=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.batch_size = batch_size

        self.chromadbclient = chromadb.PersistentClient(
            path=chroma_persist_directory,
            settings=Settings(
                anonymized_telemetry=False,  # Disable telemetry for privacy
                allow_reset=True             # Allow database reset for development
            )
        )
        try:
            self.collection = self.chromadbclient.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Nasa space missions text data collection with OpenAI embeddings"}
            )
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise
    
    def check_document_exists(self, doc_id: str) -> bool:
        """
        Check if a document with the given ID already exists in the collection
        
        Args:
            doc_id: Document ID to check
            
        Returns:
            True if document exists, False otherwise
        """
        # TODO: Query collection for document ID
        # TODO: Return True if exists, False otherwise
        
        try:
            result= self.collection.get(ids=[doc_id])
            return len(result['ids']) > 0
        except Exception as e:
            logger.error(f"Error checking document existence for ID: {doc_id}: {str(e)}")
            return False
    
    def update_document(self, doc_id: str, text: str, metadata: Dict[str, Any]) -> bool:
        """
        Update an existing document in the collection
        
        Args:
            doc_id: Document ID to update
            text: New text content
            metadata: New metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            
            # Update the document
            self.collection.update(
                ids=[doc_id],
                documents=[text],
                metadatas=[metadata]
            )
            logger.debug(f"Updated document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating document {doc_id}: {e}")
            return False
        
    def delete_documents_by_source(self, source_pattern: str) -> int:
        """
        Delete all documents from a specific source (useful for re-processing files)
        
        Args:
            source_pattern: Pattern to match source names
            
        Returns:
            Number of documents deleted
        """
        try:
            # Get all documents
            all_docs = self.collection.get()
            
            # Find documents matching the source pattern
            ids_to_delete = []
            for i, metadata in enumerate(all_docs['metadatas']):
                if source_pattern in metadata.get('source', ''):
                    ids_to_delete.append(all_docs['ids'][i])
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                logger.info(f"Deleted {len(ids_to_delete)} documents matching source pattern: {source_pattern}")
                return len(ids_to_delete)
            else:
                logger.info(f"No documents found matching source pattern: {source_pattern}")
                return 0
                
        except Exception as e:
            logger.error(f"Error deleting documents by source: {e}")
            return 0
        
    def get_file_documents(self, file_path: Path) -> List[str]:
        """
        Get all document IDs for a specific file
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of document IDs for the file
        """
        try:
            source = file_path.stem
            mission = self.extract_mission_from_path(file_path)
            
            # Get all documents
            all_docs = self.collection.get()
            
            # Find documents from this file
            file_doc_ids = []
            for i, metadata in enumerate(all_docs['metadatas']):
                if (metadata.get('source') == source and 
                    metadata.get('mission') == mission):
                    file_doc_ids.append(all_docs['ids'][i])
            
            return file_doc_ids
            
        except Exception as e:
            logger.error(f"Error getting file documents: {e}")
            return []
        
    def generate_document_id(self, file_path: Path, metadata: Dict[str, Any]) -> str:
        """
        Generate stable document ID based on file path and chunk position
        This allows for document updates without changing IDs
        """
        # TODO: Create consistent ID format
        # TODO: Use mission, source, and chunk_index
        # Format: mission_source_chunk_0001
        mission = metadata.get('mission', 'unknown')
        source = metadata.get('source', 'unknown')
        chunk_index = metadata.get('chunk_index', 0)

        # Sanitize source to remove special characters
        source_clean = source.replace('-', '_').replace(' ', '_')
        
        # Format: mission_source_chunk_0001
        doc_id = f"{mission}_{source_clean}_chunk_{chunk_index:04d}"
        return doc_id
    
    def add_documents_to_collection(self, documents: List[Tuple[str, Dict[str, Any]]], 
                                   file_path: Path, batch_size: int = 50, 
                                   update_mode: str = 'skip') -> Dict[str, int]:
        """
        Add documents to ChromaDB collection in batches with update handling
        
        Args:
            documents: List of (text, metadata) tuples
            file_path: Path to the source file
            batch_size: Number of documents to process in each batch
            update_mode: How to handle existing documents:
                        'skip' - skip existing documents
                        'update' - update existing documents
                        'replace' - delete all existing documents from file and re-add
            
        Returns:
            Dictionary with counts of added, updated, and skipped documents
        """
        if not documents:
            return {'added': 0, 'updated': 0, 'skipped': 0}
        
        stats = {'added': 0, 'updated': 0, 'skipped': 0}
        
        # TODO: Handle different update modes (skip, update, replace)
        # TODO: Process documents in batches
        # TODO: For each document:
        #   - Generate document ID
        #   - Check if exists
        #   - Get embedding
        #   - Add or update in collection
        # TODO: Return statistics

        # Handle 'replace' mode by deleting existing documents from this file first
        if update_mode == 'replace':
            existing_ids = self.get_file_documents(file_path)
            if existing_ids:
                self.collection.delete(ids=existing_ids)
                logger.info(f"Replaced {len(existing_ids)} existing documents from file: {file_path}")

        # Process documents in batches
        for batch_start in range(0,len(documents), batch_size):
            batch_end = min(batch_start + batch_size, len(documents))
            batch = documents[batch_start:batch_end]

            # Prepare batch data
            ids_to_add = []
            texts_to_add = []
            metadatas_to_add = []

            ids_to_update = []
            texts_to_update = []
            metadatas_to_update = []

            logger.info(f"Processing batch {batch_start // batch_size + 1}: documents {batch_start} to {batch_end}")
            for text, metadata in batch:
                # Generate document ID
                doc_id = self.generate_document_id(file_path, metadata)
                # Check if document exists
                exists = self.check_document_exists(doc_id)

                # Handle based on update mode
                if exists and update_mode == 'skip':
                    stats['skipped'] += 1
                    logger.info(f"Skipped existing document: {doc_id}")
                    continue
                # Decide whether to add or update
                if exists and update_mode == 'update':
                    # Update existing document
                    ids_to_update.append(doc_id)
                    texts_to_update.append(text)
                    metadatas_to_update.append(metadata)
                    stats['updated'] += 1
                elif not exists or update_mode == 'replace':
                    # Add new document
                    ids_to_add.append(doc_id)
                    texts_to_add.append(text)
                    metadatas_to_add.append(metadata)
                    stats['added'] += 1
                
            # Batch add to collection
            if ids_to_add:
                try:
                    self.collection.add(
                        ids=ids_to_add,
                        documents=texts_to_add,
                        metadatas=metadatas_to_add
                    )
                    logger.info(f"Added {len(ids_to_add)} documents to collection")
                except Exception as e:
                    logger.error(f"Error adding batch of documents to collection: {e}")
                
            # Batch update existing documents
            if ids_to_update:
                try:
                    self.collection.update(
                        ids=ids_to_update,
                        documents=texts_to_update,
                        metadatas=metadatas_to_update
                    )
                    logger.info(f"Updated {len(ids_to_update)} existing documents in collection")
                except Exception as e:
                    logger.error(f"Error updating batch of documents in collection: {e}")

        return stats
    
    def extract_mission_from_path(self, file_path: Path) -> str:
        """Extract mission name from file path"""
        path_str = str(file_path).lower()
        if 'apollo11' in path_str or 'apollo_11' in path_str:
            return 'apollo_11'
        elif 'apollo13' in path_str or 'apollo_13' in path_str:
            return 'apollo_13'
        elif 'challenger' in path_str:
            return 'challenger'
        else:
            return 'unknown'
        
    def extract_data_type_from_path(self, file_path: Path) -> str:
        """Extract data type from file path"""
        path_str = str(file_path).lower()
        if 'transcript' in path_str:
            return 'transcript'
        elif 'textract' in path_str:
            return 'textract_extracted'
        elif 'audio' in path_str:
            return 'audio_transcript'
        elif 'flight_plan' in path_str:
            return 'flight_plan'
        else:
            return 'document'
    
    def extract_document_category_from_filename(self, filename: str) -> str:
        """Extract document category from filename for better organization"""
        filename_lower = filename.lower()
        
        # Apollo transcript types
        if 'pao' in filename_lower:
            return 'public_affairs_officer'
        elif 'cm' in filename_lower:
            return 'command_module'
        elif 'tec' in filename_lower:
            return 'technical'
        elif 'flight_plan' in filename_lower:
            return 'flight_plan'
        
        # Challenger audio segments
        elif 'mission_audio' in filename_lower:
            return 'mission_audio'
        
        # NASA archive documents
        elif 'ntrs' in filename_lower:
            return 'nasa_archive'
        elif '19900066485' in filename_lower:
            return 'technical_report'
        elif '19710015566' in filename_lower:
            return 'mission_report'
        
        # General categories
        elif 'full_text' in filename_lower:
            return 'complete_document'
        else:
            return 'general_document'

    def scan_text_files_only(self, base_path: str) -> List[Path]:
        base_path = Path(base_path)
        logger.debug(base_path)
        files_to_process = []

        data_dirs = [
            'apollo11',
            'apollo13',
            'challenger'
        ]

        for data_dir in data_dirs:
            dir_path = base_path / data_dir
            if dir_path.exists():
                logger.info(f"Scanning directory: {dir_path}")
                
                # Find only text files
                text_files = list(dir_path.glob('**/*.txt'))
                logger.debug(text_files)
                files_to_process.extend(text_files)
                logger.info(f"Found {len(text_files)} text files in {data_dir}")
        filtered_files = []
        for file_path in files_to_process:
            if (file_path.name.startswith('.') or 
                'summary' in file_path.name.lower() or
                file_path.suffix.lower() != '.txt'):
                continue
            filtered_files.append(file_path)
        
        mission_counts = {}
        for file_path in filtered_files:
            logger.debug(file_path)
            mission = self.extract_mission_from_path(file_path)
            mission_counts[mission] = mission_counts.get(mission, 0) + 1
        
        logger.info("Files by mission:")
        for mission, count in mission_counts.items():
            logger.info(f"  {mission}: {count} files")
        
        return filtered_files
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Split text into chunks with metadata
        
        Args:
            text: Text to chunk
            metadata: Base metadata for the text
            
        Returns:
            List of (chunk_text, chunk_metadata) tuples
        """
        # TODO: Handle short texts that don't need chunking
        # TODO: Implement chunking logic with overlap
        # TODO: Try to break at sentence boundaries
        # TODO: Create metadata for each chunk
        
        min_chunk_size = 50
        text = text.strip()

        # Handle short texts
        if len(text) < min_chunk_size:
            return []
        
        if len(text) <= self.chunk_size:
            chunk_metadata = {**metadata, 'chunk_index': 0, 'total_chunks': 1}
            return [(text, chunk_metadata)]
        
        #Fallback Strategy (Sentence -> Word -> Hard Cut)
        def find_best_split_point(text_segment, start, ideal_end):
            """
            Try multiple stratergies to find the best  split point:
            1. Sentence boundary (. ! ? followed by space/newline)
            2. Word boundary (space, tab, newline)
            3. Hard cut at ideal_end
            """

            # Stratergy 1: Try sentence boundary first
            sentence_search_start = max(ideal_end -150, start)
            for i in range(ideal_end, sentence_search_start, -1):
                if i < len(text_segment) - 1:
                    if text_segment[i] in '.!?' and text_segment[i+1] in ' \n':
                        # Found sentence ending
                        return i + 1, 'sentence'
                    
            # Stratergy 2: Try word boundary
            word_search_start = max(ideal_end - 100, start)
            for i in range(ideal_end, word_search_start, -1):
                if i < len(text_segment) -1:
                    if text_segment[i] in ' \n\t':
                        # Found word boundary
                        return i + 1, 'word'
            
            # Stratergy 3: Hard cut
            return ideal_end, 'hard_cut'
        
        chunks = []
        chunk_methods = []
        start = 0

        while start < len(text):
            ideal_end = start + self.chunk_size

            if ideal_end >= len(text):
                chunk = text[start:].strip()
                if chunk:
                    chunks.append(chunk)
                    chunk_methods.append('end_of_text')
                break
            chunk_end, method = find_best_split_point(text, start, ideal_end)

            chunk = text[start:chunk_end].strip()

            if chunk:
                chunks.append(chunk)
                chunk_methods.append(method)

            # Move to next position with overlap
            start = max(chunk_end - self.chunk_overlap, start + 1)
        
        # Create result with metadata
        result = []
        total_chunks = len(chunks)

        for i, (chunk,method) in enumerate(zip(chunks, chunk_methods)):
            chunk_metadata = {
                **metadata,
                'chunk_index': i,
                'total_chunks': total_chunks,
                'chunk_length': len(chunk),
                'chunking_method': method
            }
            result.append((chunk, chunk_metadata))
        return result
    
    def process_text_file(self, file_path: Path) -> List[Tuple[str, Dict[str, Any]]]:
        try:
            logger.info(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return []
            
            # Enhanced metadata extraction
            metadata = {
                'source': file_path.stem,
                'file_path': str(file_path),
                'file_type': 'text',
                'content_type': 'full_text',
                'mission': self.extract_mission_from_path(file_path),
                'data_type': self.extract_data_type_from_path(file_path),
                'document_category': self.extract_document_category_from_filename(file_path.name),
                'file_size': len(content),
                'processed_timestamp': datetime.now().isoformat()
            }

            logger.info(metadata)
            return self.chunk_text(content, metadata)
            
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {e}")
            return []

    def process_all_text_data(self,base_path: str, update_mode: str = 'skip') -> Dict[str, int]:

        stats = {
            'files_processed': 0,
            'documents_added': 0,
            'documents_updated': 0,
            'documents_skipped': 0,
            'errors': 0,
            'total_chunks': 0,
            'missions': {}
        }

        logger.info(f"Scanning for text files to process in: {base_path}")
        files_to_process = self.scan_text_files_only(base_path)

        if not files_to_process:
            logger.warning("No text files found to process.")
            return stats
        logger.info(f"Total text files to process: {len(files_to_process)}")

        for file_idx, file_path in enumerate(files_to_process, 1):
            logger.info(f"Processing file {file_idx}/{len(files_to_process)}: {file_path.name}")
            try:
                # Process the text file to get chunks
                documents = self.process_text_file(file_path)

                if not documents:
                    logger.warning(f"No chunks generated from: {file_path.name}")
                    continue
                logger.info(f"Generated {len(documents)} chunks from file: {file_path.name}")
                stats['total_chunks'] += len(documents)

                # Add documents to collection
                file_stats = self.add_documents_to_collection(
                    documents=documents,
                    file_path=file_path,
                    batch_size=self.batch_size,
                    update_mode=update_mode
                )

                stats['files_processed'] += 1
                stats['documents_added'] += file_stats['added']
                stats['documents_updated'] += file_stats['updated']
                stats['documents_skipped'] += file_stats['skipped']

                mission = self.extract_mission_from_path(file_path)
                if mission not in stats['missions']:
                    stats['missions'][mission] = {
                        'files': 0,
                        'chunks': 0,
                        'added': 0,
                        'updated': 0,
                        'skipped': 0
                    }
                stats['missions'][mission]['files'] += 1
                stats['missions'][mission]['chunks'] += len(documents)
                stats['missions'][mission]['added'] += file_stats['added']
                stats['missions'][mission]['updated'] += file_stats['updated']
                stats['missions'][mission]['skipped'] += file_stats['skipped']
                logger.info(f"Completed {file_path.name}: Added={file_stats['added']}, "
                            f"Updated={file_stats['updated']}, Skipped={file_stats['skipped']}")
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"Error processing file {file_path.name}: {str(e)}", exc_info=True)
                continue
            logger.info(f"Processing complete: {stats['files_processed']} files processed, "
                        f"{stats['total_chunks']} total chunks created")

        return stats
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the ChromaDB collection"""
        # TODO: Return collection name, document count, metadata
        try:
            # Get collection count
            count = self.collection.count()

            # Return collection name , document count, and metadata
            return {
                'collection_name': self.collection.name,
                'document_count': count,
                'metadata': self.collection.metadata
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {
                'collection_name': 'N/A',
                'document_count': 0,
                'metadata': {},
                'error': str(e)
    
            }
    
    def evaluate_query_relevance(self, query_text: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate if query results are relevant and correct
        
        Args:
            query_text: The query that was performed
            results: Results from query_collection
            
        Returns:
            Evaluation results with relevance assessment
        """
        evaluation = {
            'query': query_text,
            'has_results': False,
            'result_count': 0,
            'avg_distance': 0.0,
            'top_distances': [],
            'top_metadatas': [],
            'relevance_assessment': 'NO_RESULTS',
            'issues': []
        }
        
        try:
            if not results or 'documents' not in results:
                evaluation['issues'].append('No results returned from query')
                return evaluation
            
            docs = results.get('documents', [[]])[0]
            distances = results.get('distances', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            if not docs:
                evaluation['issues'].append('Empty document list in results')
                return evaluation
            
            evaluation['has_results'] = True
            evaluation['result_count'] = len(docs)
            evaluation['top_distances'] = distances[:3] if distances else []
            evaluation['top_metadatas'] = metadatas[:3] if metadatas else []
            
            if distances:
                evaluation['avg_distance'] = sum(distances) / len(distances)
            
            # Relevance assessment based on distance
            # ChromaDB uses cosine distance: 0 = perfect match, 2 = completely different
            if distances:
                avg_dist = evaluation['avg_distance']
                if avg_dist < 0.3:
                    evaluation['relevance_assessment'] = 'HIGHLY_RELEVANT'
                elif avg_dist < 0.5:
                    evaluation['relevance_assessment'] = 'RELEVANT'
                elif avg_dist < 0.7:
                    evaluation['relevance_assessment'] = 'SOMEWHAT_RELEVANT'
                else:
                    evaluation['relevance_assessment'] = 'NOT_RELEVANT'
                    evaluation['issues'].append(f'High distance score: {avg_dist:.3f}')
            
            return evaluation
            
        except Exception as e:
            evaluation['issues'].append(f'Error during evaluation: {str(e)}')
            return evaluation
    
    def run_validation_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive validation tests on the collection
        
        Returns:
            Dictionary with validation results for all test queries
        """
        # Define test queries covering different aspects of the data
        test_queries = {
            # Mission-specific queries
            'apollo_11_missions': 'Tell me about Apollo 11 mission details',
            'apollo_13_problems': 'What happened during Apollo 13 mission?',
            'challenger_mission': 'Describe the Challenger mission',
            
            # Technical queries
            'guidance_system': 'Guidance system and spacecraft control',
            'life_support': 'Life support and cabin pressure systems',
            'propulsion_systems': 'Propulsion systems and fuel management',
            'communications': 'Communications systems and transcripts',
            
            # Mission phases
            'launch_procedures': 'Launch sequence and countdown procedures',
            'lunar_landing': 'Moon landing procedures and descent',
            'lunar_surface': 'Activities on lunar surface and moonwalk',
            'return_procedures': 'Return to Earth and re-entry procedures',
            
            # Astronaut names and activities
            'neil_armstrong': 'Neil Armstrong activities and communications',
            'buzz_aldrin': 'Buzz Aldrin lunar module pilot',
            'jim_lovell': 'Jim Lovell Apollo 13',
            'mission_crew': 'Astronauts and crew members',
            
            # Events and incidents
            'oxygen_tank': 'Oxygen tank malfunction',
            'electrical_problems': 'Electrical system issues',
            'equipment_failure': 'Equipment failures during mission',
            'emergency_procedures': 'Emergency procedures and contingency plans',
            
            # Science and objectives
            'lunar_science': 'Scientific objectives and experiments',
            'moon_rocks': 'Sample collection and analysis',
            'lunar_surface_work': 'Moonwalk activities and objectives',
            
            # Cross-mission queries
            'mission_comparison': 'Comparing different Apollo missions',
            'technical_challenges': 'Technical challenges across missions',
            'mission_success': 'Mission success factors and achievements'
        }
        
        validation_results = {
            'total_tests': len(test_queries),
            'tests_run': 0,
            'highly_relevant': 0,
            'relevant': 0,
            'somewhat_relevant': 0,
            'not_relevant': 0,
            'test_details': [],
            'summary': {}
        }
        
        logger.info("=" * 80)
        logger.info("RUNNING COMPREHENSIVE VALIDATION TESTS")
        logger.info("=" * 80)
        
        for test_name, query_text in test_queries.items():
            logger.info(f"\n[Test: {test_name}]")
            logger.info(f"Query: {query_text}")
            
            # Run query
            results = self.query_collection(query_text, n_results=5)
            
            # Evaluate results
            evaluation = self.evaluate_query_relevance(query_text, results)
            
            validation_results['tests_run'] += 1
            
            # Update counts
            relevance = evaluation['relevance_assessment']
            if relevance == 'HIGHLY_RELEVANT':
                validation_results['highly_relevant'] += 1
            elif relevance == 'RELEVANT':
                validation_results['relevant'] += 1
            elif relevance == 'SOMEWHAT_RELEVANT':
                validation_results['somewhat_relevant'] += 1
            elif relevance == 'NOT_RELEVANT':
                validation_results['not_relevant'] += 1
            
            # Log evaluation
            logger.info(f"Relevance: {evaluation['relevance_assessment']}")
            logger.info(f"Result Count: {evaluation['result_count']}")
            logger.info(f"Avg Distance: {evaluation['avg_distance']:.4f}")
            
            if evaluation['has_results']:
                logger.info("Top 3 Results:")
                for i, (doc, meta, dist) in enumerate(zip(
                    results['documents'][0][:3],
                    evaluation['top_metadatas'][:3],
                    evaluation['top_distances'][:3]
                )):
                    logger.info(f"  {i+1}. Distance: {dist:.4f}")
                    logger.info(f"     Source: {meta.get('source', 'N/A')} | Mission: {meta.get('mission', 'N/A')}")
                    logger.info(f"     Preview: {doc[:150]}...")
            
            if evaluation['issues']:
                logger.warning(f"Issues: {', '.join(evaluation['issues'])}")
            
            validation_results['test_details'].append({
                'test_name': test_name,
                'query': query_text,
                'evaluation': evaluation
            })
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {validation_results['total_tests']}")
        logger.info(f"Highly Relevant: {validation_results['highly_relevant']}")
        logger.info(f"Relevant: {validation_results['relevant']}")
        logger.info(f"Somewhat Relevant: {validation_results['somewhat_relevant']}")
        logger.info(f"Not Relevant: {validation_results['not_relevant']}")
        
        success_rate = (validation_results['highly_relevant'] + validation_results['relevant']) / validation_results['total_tests'] * 100 if validation_results['total_tests'] > 0 else 0
        logger.info(f"Success Rate (Highly + Relevant): {success_rate:.1f}%")
        
        return validation_results
    
    
    def query_collection(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Query the collection for testing
        
        Args:
            query_text: Query text
            n_results: Number of results to return
            
        Returns:
            Query results
        """
        # TODO: Perform test query and return results
        try:
            logger.info(f"Querying collection: '{query_text}' with top {n_results} results")

            # Perform test query
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                include=['documents',"distances", 'metadatas']
            )

            # Log results summary
            num_results = len(results.get('documents', [[]])[0]) if results.get('documents') else 0
            logger.info(f"Found {num_results} results") 

            return results
        except Exception as e:
            logger.error(f"Error querying collection: {e}")
            return {
                'documents': [[]],
                'distances': [[]],
                'metadatas': [[]],
                'error': str(e)
     
            }
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get detailed statistics about the collection"""
        try:
            # Get all documents to analyze
            all_docs = self.collection.get()
            
            if not all_docs['metadatas']:
                return {'error': 'No documents in collection'}
            
            stats = {
                'total_documents': len(all_docs['metadatas']),
                'missions': {},
                'data_types': {},
                'document_categories': {},
                'file_types': {}
            }
            
            # Analyze metadata
            for metadata in all_docs['metadatas']:
                mission = metadata.get('mission', 'unknown')
                data_type = metadata.get('data_type', 'unknown')
                doc_category = metadata.get('document_category', 'unknown')
                file_type = metadata.get('file_type', 'unknown')
                
                # Count by mission
                stats['missions'][mission] = stats['missions'].get(mission, 0) + 1
                
                # Count by data type
                stats['data_types'][data_type] = stats['data_types'].get(data_type, 0) + 1
                
                # Count by document category
                stats['document_categories'][doc_category] = stats['document_categories'].get(doc_category, 0) + 1
                
                # Count by file type
                stats['file_types'][file_type] = stats['file_types'].get(file_type, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'error': str(e)}
        
def main():
    parser = argparse.ArgumentParser(description='ChromaDB Embedding Pipeline for NASA Data')
    parser.add_argument('--data-path', default='.', help='Path to data directories')
    parser.add_argument('--chroma-dir', default='./chroma_db_openai', help='ChromaDB persist directory')
    parser.add_argument('--collection-name', default='nasa_space_missions_text', help='Collection name')
    parser.add_argument('--chunk-size', type=int, default=500, help='Text chunk size')
    parser.add_argument('--chunk-overlap', type=int, default=100, help='Chunk overlap size')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size for processing')
    parser.add_argument('--update-mode', choices=['skip', 'update', 'replace'], default='skip',
                       help='How to handle existing documents: skip, update, or replace')
    parser.add_argument('--stats-only', action='store_true', help='Only show collection statistics')
    parser.add_argument('--delete-source', help='Delete all documents from a specific source pattern')
    parser.add_argument('--test-query', help='Test query to validate collection retrieval')
    parser.add_argument('--run-validation', action='store_true', help='Run comprehensive validation tests')

    args = parser.parse_args()
    logger.info(f"chunk size: {args.chunk_size}")
    logger.info(f"chunk overlap: {args.chunk_overlap}")
    logger.info(f"data path: {args.data_path}")
    logger.info(f"data path: {args.chroma_dir}")
    logger.info(f"data path: {args.collection_name}")
    logger.info(f"data path: {args.batch_size}")
    logger.info(f"data path: {args.update_mode}")



    # Initialize pipeline
    logger.info("Initializing ChromaDB Embedding Pipeline...")
    pipeline = ChromaEmbeddingPipelineTextOnly(
        chroma_persist_directory=args.chroma_dir,
        collection_name=args.collection_name,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        batch_size=args.batch_size
    )

    if args.delete_source:
        deleted_count = pipeline.delete_documents_by_source(args.delete_source)
        logger.info(f"Deleted {deleted_count} documents matching source pattern: {args.delete_source}")
        return
    
    if args.stats_only:
        logger.info("Collection Statistics:")
        stats = pipeline.get_collection_stats()
        for key, value in stats.items():
            logger.info(f"{key}: {value}")
        return
    
    if args.run_validation:
        logger.info("Running comprehensive validation tests...")
        validation_results = pipeline.run_validation_tests()
        logger.info("Validation tests completed!")
        return
    
    logger.info(f"Starting text data processing with update mode: {args.update_mode}")
    start_time = time.time()

    stats = pipeline.process_all_text_data(args.data_path, update_mode=args.update_mode)

    end_time = time.time()
    processing_time = end_time - start_time
    
    # Print results
    logger.info("=" * 60)
    logger.info("PROCESSING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Files processed: {stats['files_processed']}")
    logger.info(f"Total chunks created: {stats['total_chunks']}")
    logger.info(f"Documents added to collection: {stats['documents_added']}")
    logger.info(f"Documents updated in collection: {stats['documents_updated']}")
    logger.info(f"Documents skipped (already exist): {stats['documents_skipped']}")
    logger.info(f"Errors: {stats['errors']}")
    logger.info(f"Processing time: {processing_time:.2f} seconds")
    
    # Mission breakdown
    logger.info("\nMission breakdown:")
    for mission, mission_stats in stats['missions'].items():
        logger.info(f"  {mission}: {mission_stats['files']} files, {mission_stats['chunks']} chunks")
        logger.info(f"    Added: {mission_stats['added']}, Updated: {mission_stats['updated']}, Skipped: {mission_stats['skipped']}")
    
    # Collection info
    collection_info = pipeline.get_collection_info()
    logger.info(f"\nCollection: {collection_info.get('collection_name', 'N/A')}")
    logger.info(f"Total documents in collection: {collection_info.get('document_count', 'N/A')}")

    # Test query if provided
    if args.test_query:
        logger.info(f"\nTesting query: '{args.test_query}'")
        results = pipeline.query_collection(args.test_query)
        if results and 'documents' in results:
            logger.info(f"Found {len(results['documents'][0])} results:")
            for i, doc in enumerate(results['documents'][0][:3]):  # Show top 3
                logger.info(f"Result {i+1}: {doc[:200]}...")

    logger.info("Pipeline completed successfully!")

if __name__ == "__main__":
    main()