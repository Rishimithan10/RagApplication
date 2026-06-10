from groq import Groq
import json

def _ask_groq(client, prompt):
    """Send a scoring prompt to Groq and parse JSON response."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    text = response.choices[0].message.content.strip()

    # Extract JSON from response
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end != 0:
        return json.loads(text[start:end])
    return None


def score_faithfulness(client, answer, contexts):
    """
    Faithfulness: Is every claim in the answer supported by the retrieved chunks?
    Score 0.0 - 1.0
    """
    context_text = "\n---\n".join(contexts)
    prompt = f"""You are an evaluator. Given the context and an answer, check if every statement in the answer is supported by the context.

Context:
{context_text}

Answer:
{answer}

Score the faithfulness from 0.0 to 1.0:
- 1.0 = every claim is fully supported by the context
- 0.5 = some claims are supported, some are not
- 0.0 = the answer contradicts or ignores the context

Respond ONLY with a JSON object like this:
{{"score": 0.85, "reason": "one sentence explanation"}}"""

    result = _ask_groq(client, prompt)
    return result if result else {"score": 0.0, "reason": "Could not evaluate"}


def score_answer_relevancy(client, question, answer):
    """
    Answer Relevancy: Does the answer actually address the question?
    Score 0.0 - 1.0
    """
    prompt = f"""You are an evaluator. Given a question and an answer, check how well the answer addresses the question.

Question:
{question}

Answer:
{answer}

Score the answer relevancy from 0.0 to 1.0:
- 1.0 = answer directly and completely addresses the question
- 0.5 = answer is partially relevant but misses key points
- 0.0 = answer is completely off-topic or doesn't answer the question

Respond ONLY with a JSON object like this:
{{"score": 0.85, "reason": "one sentence explanation"}}"""

    result = _ask_groq(client, prompt)
    return result if result else {"score": 0.0, "reason": "Could not evaluate"}


def score_context_precision(client, question, contexts):
    """
    Context Precision: Were the retrieved chunks actually relevant to the question?
    Score 0.0 - 1.0
    """
    context_text = "\n---\n".join([f"Chunk {i+1}: {c}" for i, c in enumerate(contexts)])
    prompt = f"""You are an evaluator. Given a question and retrieved chunks, check how relevant the chunks are for answering the question.

Question:
{question}

Retrieved Chunks:
{context_text}

Score the context precision from 0.0 to 1.0:
- 1.0 = all chunks are highly relevant to answering the question
- 0.5 = some chunks are relevant, some are noise
- 0.0 = none of the chunks are relevant to the question

Respond ONLY with a JSON object like this:
{{"score": 0.85, "reason": "one sentence explanation"}}"""

    result = _ask_groq(client, prompt)
    return result if result else {"score": 0.0, "reason": "Could not evaluate"}


def evaluate_rag(question, answer, contexts, groq_api_key):
    """
    Evaluate RAG response on 3 metrics using Groq directly.
    Returns dict with scores and reasons for each metric.
    """
    try:
        client = Groq(api_key=groq_api_key)

        faithfulness     = score_faithfulness(client, answer, contexts)
        answer_relevancy = score_answer_relevancy(client, question, answer)
        context_precision = score_context_precision(client, question, contexts)

        return {
            "faithfulness":        faithfulness,
            "answer_relevancy":    answer_relevancy,
            "context_precision":   context_precision,
        }

    except Exception as e:
        return {"error": str(e)}
