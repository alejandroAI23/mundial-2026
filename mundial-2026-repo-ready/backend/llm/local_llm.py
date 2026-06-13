"""Conector opcional para modelo local GGUF con llama-cpp-python.

No es obligatorio para producción inicial. Úsalo cuando quieras respuestas más
naturales que las reglas de qa_service.py.
"""

from __future__ import annotations

import os
from functools import lru_cache


@lru_cache(maxsize=1)
def get_llm():
    model_path = os.getenv("LOCAL_MODEL_PATH")
    if not model_path:
        return None
    try:
        from llama_cpp import Llama
    except ImportError as exc:
        raise RuntimeError("Instala llama-cpp-python para usar modelo local") from exc

    return Llama(
        model_path=model_path,
        n_ctx=int(os.getenv("LOCAL_MODEL_CTX", "4096")),
        n_threads=int(os.getenv("LOCAL_MODEL_THREADS", "6")),
        verbose=False,
    )


def generate_with_context(question: str, context: str) -> str | None:
    llm = get_llm()
    if llm is None:
        return None
    prompt = f"""Eres un asistente experto en el Mundial 2026.
Responde en español, breve y sin inventar datos.
Usa exclusivamente el contexto.

CONTEXTO:
{context}

PREGUNTA: {question}
RESPUESTA:"""
    output = llm(prompt, max_tokens=220, temperature=0.1, stop=["PREGUNTA:"])
    return output["choices"][0]["text"].strip()
