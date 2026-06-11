from typing import Dict, List
from openai import OpenAI

def generate_response(openai_key: str, user_message: str, context: str, 
                     conversation_history: List[Dict], model: str = "gpt-3.5-turbo") -> str:
    """Generate response using OpenAI with context"""

    # TODO: Define system prompt
    system_prompt = """You are a knowledgeable NASA mission assistant with expertise in Apollo 11,
    Apollo 13, and Challenger missions. You help users understand historical space mission details,
    transcripts, and technical information.

    Answer user questions based on the provided context. If the content doesn't contain relevant
    information to answer the question, say so clearly. Be concise and accurate."""

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # TODO: Add chat history
    for msg in conversation_history:
        messages.append(msg)

    # TODO: Set context in messages
    if context:
        user_message_with_context = f""""Context from NASA mission documents:

        {context}

        ---
        Question: {user_message}"""
    else:
        user_message_with_context = user_message
    messages.append({"role": "user", "content": user_message_with_context})

    # TODO: Create OpenAI Client
    client = OpenAI(
        base_url="https://openai.vocareum.com/v1",
        api_key=openai_key
    )

    # TODO: Send request to OpenAI
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )

        # TODO: Return response
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"
