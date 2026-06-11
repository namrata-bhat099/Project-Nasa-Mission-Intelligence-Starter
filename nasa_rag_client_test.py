from rag_client import discover_chroma_backends
from rag_client import initialize_rag_system
from rag_client import retrieve_documents
from rag_client import format_context
from llm_client import generate_response

def main():
    backends = discover_chroma_backends()

    print(backends)
    collection = initialize_rag_system('./chroma_db_openai','nasa_space_missions_text')
    #results = retrieve_documents(collection,'What happened during Apollo 13 mission?',5,'apollo_13')
    #print(results)
    #context = format_context(results.get('documents', [[]])[0],results.get('metadatas', [[]])[0])
    #print(context)

    response = generate_response("voc-777460345126677478748569bc05e493bdd9.29426320", "What was Apollo 11?", "", [])
    print(response)

if __name__ == "__main__":
    main()