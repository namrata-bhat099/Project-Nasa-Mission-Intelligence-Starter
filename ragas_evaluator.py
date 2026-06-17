import sys
from unittest.mock import MagicMock

# Trick ragas into bypassing the broken Google VertexAI imports
sys.modules['langchain_community.chat_models.vertexai'] = MagicMock()
sys.modules['langchain_community.llms.vertexai'] = MagicMock()

from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from typing import Dict, List, Optional
from datasets import Dataset

# RAGAS imports
try:
    from ragas import SingleTurnSample
    from ragas.metrics import BleuScore, NonLLMContextPrecisionWithReference, ResponseRelevancy, Faithfulness, RougeScore
    from ragas import evaluate
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False

def evaluate_response_quality(question: str, answer: str, contexts: List[str]) -> Dict[str, float]:
    """Evaluate response quality using RAGAS metrics"""
    if not RAGAS_AVAILABLE:
        return {"error": "RAGAS not available"}
    
    # Validate inputs - handle empty or malformed inputs
    if not question or not question.strip():
        return {"error": "Question cannot be empty"}
    
    if not answer or not answer.strip():
        return {"error": "Answer cannot be empty"}
    
    if not contexts or len(contexts) == 0:
        return {"error": "Contexts cannot be empty"}
    
    # Filter out empty contexts
    valid_contexts = [ctx.strip() for ctx in contexts if ctx and ctx.strip()]

    if not valid_contexts:
        return {"error": "No valid contexts provided"}
    
    openai_api_key="voc-777460345126677478748569bc05e493bdd9.29426320"
    
    try:
        # TODO: Create evaluator LLM with model gpt-3.5-turbo
        evaluator_llm = LangchainLLMWrapper(
            ChatOpenAI(
                model="gpt-3.5-turbo",
                openai_api_base="",
                openai_api_key=openai_api_key,
                temperature=0 # Consistent evaluation
            )
        )
        
        # TODO: Create evaluator_embeddings with model test-embedding-3-small
        evaluator_embeddings = LangchainEmbeddingsWrapper(
            OpenAIEmbeddings(
                model="test-embedding-3-small",
                openai_api_base="",
                openai_api_key=openai_api_key,

            )
        )
    
        # TODO: Define an instance for each metric to evaluate
        # Core RAGAS metrics (LLM-based)
        faithfulness = Faithfulness(llm=evaluator_llm)
        response_relevancy = ResponseRelevancy(
            llm=evaluator_llm,
            embeddings=evaluator_embeddings
        )

        # Additional metrics (non-LLM based)
        bleu_score = BleuScore()
        rouge_score = RougeScore()
        context_precision = NonLLMContextPrecisionWithReference()

        # Create list of all metrics
        metrics = [
            faithfulness,
            response_relevancy,
            bleu_score,
            rouge_score,
            context_precision
        ]

        # Create sample for evaluation
        samples = SingleTurnSample(
            user_input=question,
            response=answer,
            retrieved_contexts=valid_contexts,
            reference="", #Optional: ground truth answer
        )

        evaluation_dataset = [
            {
                "question": sample.user_input,
                "contexts": sample.retrieved_contexts,
                "answer": sample.response,
                "ground_truth": sample.reference
            }
            for sample in samples
        ]

        ragas_dataset = Dataset.from_list(evaluation_dataset)

        # TODO: Evaluate the response using the metrics
        result= evaluate(
            llm=evaluator_llm,
            embeddings=evaluator_embeddings,
            dataset=[sample],
            metrics=metrics
        )
        # TODO: Return the evaluation results
        # convert result to dictionary with metric scores
        evaluation_scores = {}

        # Extract scores from result Dataframe
        if hasattr(result, 'to_pandas'):
            df=result.to_pandas()
            if not df.empty:
                # Get first row (single sample)
                for column in df.column:
                    if column not in ['user_inpt', 'response', 'retrieved_contexts', 'reference']:
                        evaluation_scores[column] = float(df[column].iloc[0])
        else:
            # Fallback: convert result dict directly
            evaluation_scores= {k: float(v) for k, v in result.items()
                            if isinstance(v, (int,float))}
        return evaluation_scores
    except Exception as e:
        # Handle errors gracefully - no crashes
        return {"error": f"Evaluation failed: {str(e)}"}
