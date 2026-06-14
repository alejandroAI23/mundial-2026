"""Optional local LLM integration.

This file is intentionally not activated in the free Render/Replit deployment.
Running Mistral/Phi locally needs more RAM/CPU/GPU than most free web-service tiers.
Use this only for local experiments or a paid GPU/VM.
"""

from __future__ import annotations

from pathlib import Path


class LocalLLM:
    def __init__(self, model_path: str | Path):
        self.model_path = str(model_path)
        self.llm = None

    def load(self) -> None:
        from llama_cpp import Llama

        self.llm = Llama(model_path=self.model_path, n_ctx=4096, n_threads=6)

    def answer(self, prompt: str) -> str:
        if self.llm is None:
            self.load()
        output = self.llm(prompt, max_tokens=256, temperature=0.2)
        return output["choices"][0]["text"].strip()
