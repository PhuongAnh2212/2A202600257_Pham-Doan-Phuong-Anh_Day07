from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base (RAG pattern).
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        """
        Answer a question using Retrieval-Augmented Generation (RAG):
        
        1. Retrieve top-k most relevant chunks from the store
        2. Build a prompt with context + question
        3. Call the LLM function to generate the answer
        """
        if not question or not question.strip():
            return "Please ask a valid question."

        # Step 1: Retrieve relevant chunks
        retrieved_docs = self.store.search(query=question, top_k=top_k)

        if not retrieved_docs:
            return "I don't have enough information to answer this question."

        # Step 2: Build context from retrieved documents
        context_parts = []
        for doc in retrieved_docs:
            content = doc.get("content", "").strip()
            if content:
                context_parts.append(content)

        context = "\n\n".join(context_parts)

        # Step 3: Build prompt
        prompt = f"""You are a helpful assistant. Use the following context to answer the question accurately.

Context:
{context}

Question: {question}

Answer:"""

        # Step 4: Call LLM
        try:
            answer = self.llm_fn(prompt)
            return answer.strip()
        except Exception as e:
            return f"Sorry, I encountered an error while generating the answer: {str(e)}"