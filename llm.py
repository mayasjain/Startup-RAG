import os
from groq import Groq
from dotenv import load_dotenv
from retrieval import retrieve

load_dotenv()

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _client


def answer(question, chunks):
    context = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c in chunks
    )
    response = _get_client().chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a startup advisor. Answer the user's question using only "
                    "the context provided below. Be concise and specific. "
                    "At the end of your answer, note which source(s) you drew from."
                ),
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}",
            },
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    question = input("Ask a startup question: ")
    chunks = retrieve(question, k=4)
    print("\nThinking...\n")
    print(answer(question, chunks))
