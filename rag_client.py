import chromadb
import logging
from chromadb.config import Settings
from typing import Dict, List, Optional
from pathlib import Path
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_client.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def discover_chroma_backends() -> Dict[str, Dict[str, str]]:
    """Discover available ChromaDB backends in the project directory"""
    backends = {}
    current_dir = Path(".")
    
    # Look for ChromaDB directories
    # TODO: Create list of directories that match specific criteria (directory type and name pattern)
    chroma_dirs = []

    # Search for directories containing ChromaDB database files
    for path in current_dir.rglob("chroma.sqlite3"):
        chroma_dir = path.parent
        if chroma_dir not in chroma_dirs:
            chroma_dirs.append(chroma_dir)

    # Also check directories with "chroma in the name
    for item in current_dir.glob("*chroma*"):
        if item.is_dir() and item not in chroma_dirs:
            chroma_dirs.append(item)

    logger.info(f"Found {len(chroma_dirs)} ChromaDB directories")


    # TODO: Loop through each discovered directory
    for chroma_dir in chroma_dirs:

        # TODO: Wrap connection attempt in try-except block for error handling
        try:
            logger.info(f"Checking directory: {chroma_dir}")        
            # TODO: Initialize database client with directory path and configuration settings
            client = chromadb.PersistentClient(
                path=str(chroma_dir),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                )
            )
            # TODO: Retrieve list of available collections from the database
            collections = client.list_collections()

            # TODO: Loop through each collection found
            for collection in collections:
                # TODO: Create unique identifier key combining directory and collection names
                key = f"{chroma_dir.name}_{collection.name}"
                
                # TODO: Get document count with fallback for unsupported operations
                try:
                    doc_count = collection.count()
                except Exception as e:
                    doc_count = 0
                
                logger.info(f"Discovered collection: {collection.name} with {doc_count} documents in directory: {chroma_dir}")
                # TODO: Build information dictionary containing:
                backends[key] = {
                    # TODO: Store directory path as string
                    'directory': str(chroma_dir),
                    # TODO: Store collection name
                    'collection_name': collection.name,
                    # TODO: Create user-friendly display name
                    'display_name': f"{chroma_dir.name}/{collection.name} ({doc_count} documents",
                    # TODO: Get document count
                    'count': str(doc_count)
                }
        # TODO: Handle connection or access errors gracefully
        except Exception as e:
            logger.error(f"Error accessing directory {chroma_dir}: {e}")
            # TODO: Create fallback entry for inaccessible directories
            key = f"{chroma_dir.name}_error"
            # TODO: Include error information in display name with truncation
            error_message = str(e)
            if len(error_message) > 50:
                error_message = error_message[:47] + "..."
            # TODO: Set appropriate fallback values for missing information
            backends[key] = {
                'path': str(chroma_dir),
                'collection': 'N/A',
                'display_name': f"{chroma_dir.name} (Error: {error_message})",
                'count': 'N/A'
            }
    # TODO: Return complete backends dictionary with all discovered collections
    return backends

def initialize_rag_system(chroma_dir: str, collection_name: str):
    """Initialize the RAG system with specified backend (cached for performance)"""

    
    try:
        # TODO: Create a chomadb persistentclient
        client = chromadb.PersistentClient(
            path=chroma_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            )
        )
        # TODO: Return the collection with the collection_name
        collection = client.get_collection(name=collection_name)

        # Verify collection has documents
        doc_count = collection.count()
        logger.info(f"Initialized RAG system with collection: {collection_name} containing {doc_count} documents")
        return collection,"success",""
    except ValueError as e:
        # Collection not found
        logger.error(f"Collection '{collection_name}' not found in directory '{chroma_dir}'. "
                     "Please run embedding_pipeline.py first")
        return "","","Collection '{collection_name}' not found in directory '{chroma_dir}'. Please run embedding_pipeline.py first"
        """ raise ValueError(f"Collection '{collection_name}' not found in directory '{chroma_dir}'. "
                     "Please run embedding_pipeline.py first")"""
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        return "","","Failed to initialize RAG system: {e}"
        """raise RuntimeError(f"Failed to initialize RAG system: {e}")"""
    
def get_embedding(text:str, openai_api_key: str, embedding_model: str = "text-embedding-3-small") -> List[float]:
    """
    Get OpenAI embedding for text
    
    Args:
        text: Input text to embed
        openai_key: OpenAI API key
        embedding_model: OpenAI embedding model to use
        
    Returns:
        Embedding vector
    """

    try:
        openai_client = OpenAI(
            base_url="https://openai.vocareum.com/v1", 
            api_key=openai_api_key
        )

        response = openai_client.embeddings.create(
            input=text,
            model=embedding_model
        )
        embeddings = response.data[0].embedding
        logger.info(f"Generated {len(embeddings)} OpenAI embeddings")
        return embeddings
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise

def retrieve_documents(collection, query: str, n_results: int = 3, 
                      mission_filter: Optional[str] = None) -> Optional[Dict]:
    """Retrieve relevant documents from ChromaDB with optional filtering"""

    # TODO: Initialize filter variable to None (represents no filtering)
    where_filter = None

    # TODO: Check if filter parameter exists and is not set to "all" or equivalent
    if mission_filter and mission_filter.lower() != "all":
        # TODO: If filter conditions are met, create filter dictionary with appropriate field-value pairs
        where_filter = {"mission": mission_filter}
    try:
        # Generate embedding for query
        api_key = "voc-777460345126677478748569bc05e493bdd9.29426320"
        query_embedding = get_embedding(query,api_key)
        
        # TODO: Execute database query with the following parameters:
        results = collection.query(
            # TODO: Pass search query in the required format
            query_embeddings=[query_embedding],
            # TODO: Set maximum number of results to return
            n_results=n_results,
            # TODO: Apply conditional filter (None for no filtering, dictionary for specific filtering)
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        # TODO: Return query results to caller
        return results
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        return None

def format_context(documents: List[str], metadatas: List[Dict]) -> str:
    """Format retrieved documents into context"""
    if not documents:
        return ""
    
    # TODO: Initialize list with header text for context section
    context_parts = ["== Retrieved Context ===\n"]

    # TODO: Loop through paired documents and their metadata using enumeration
    for i , (doc, metadata) in enumerate(zip(documents, metadatas),1):
        # TODO: Extract mission information from metadata with fallback value
        mission = metadata.get('mission', 'unknown')
        # TODO: Clean up mission name formatting (replace underscores, capitalize)
        mission_clean= mission.replace('_',' ').title()
        # TODO: Extract source information from metadata with fallback value 
        source = metadata.get('source', 'unknown') 
        # TODO: Extract category information from metadata with fallback value
        category= metadata.get('category', 'unknown')
        # TODO: Clean up category name formatting (replace underscores, capitalize)
        category_clean = category.replace('_',' ').title()
        
        # TODO: Create formatted source header with index number and extracted information
        header = f"\n[Source {i}] Mission: {mission_clean} | Document: {source} | Category: {category_clean}"
        # TODO: Add source header to context parts list
        context_parts.append(header)
        # TODO: Check document length and truncate if necessary
        max_doc_length = 1000 # Limit each document to 1000 chracters
        if len(doc) > max_doc_length:
            truncated_doc = doc[:max_doc_length] + "...[truncated]"
            context_parts.append(truncated_doc)
        else:
            # TODO: Add truncated or full document content to context parts list
            context_parts.append(doc)
        
    # TODO: Join all context parts with newlines and return formatted string
    return "\n".join(context_parts)