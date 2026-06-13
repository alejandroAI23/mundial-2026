"""Plantilla de fine-tuning LoRA para un modelo pequeño.

Recomendación: ejecutar en Google Colab con GPU o en tu PC si tienes NVIDIA.
No es necesario para fase 1. Usa esto cuando ya tengas muchos ejemplos reales.
"""

from __future__ import annotations

import json
from pathlib import Path

from datasets import Dataset

SYSTEM_PROMPT = (
    "Eres un asistente experto en el Mundial 2026. Responde en español, "
    "con datos del torneo, sin inventar información y de forma breve."
)

PROMPT_TEMPLATE = """<s>[INST] <<SYS>>
{system}
<</SYS>>

{question} [/INST] {answer}</s>"""


def load_examples(path: Path) -> Dataset:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            rows.append({
                "text": PROMPT_TEMPLATE.format(
                    system=SYSTEM_PROMPT,
                    question=item["question"],
                    answer=item["answer"],
                )
            })
    return Dataset.from_list(rows)


def main() -> None:
    # Instala antes: pip install transformers datasets trl peft accelerate bitsandbytes
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import LoraConfig
    from trl import SFTTrainer, SFTConfig

    model_name = "microsoft/Phi-3-mini-4k-instruct"  # Alternativa: mistralai/Mistral-7B-Instruct-v0.3
    dataset_path = Path("model_local/datasets/qa_worldcup_generated.jsonl")
    dataset = load_examples(dataset_path)

    quant_config = BitsAndBytesConfig(load_in_4bit=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=quant_config,
        device_map="auto",
        trust_remote_code=True,
    )

    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["qkv_proj", "o_proj", "gate_up_proj", "down_proj"],
    )

    args = SFTConfig(
        output_dir="model_local/out/phi3-worldcup-lora",
        num_train_epochs=1,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=2e-4,
        logging_steps=10,
        max_seq_length=1024,
        dataset_text_field="text",
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        peft_config=peft_config,
        args=args,
    )
    trainer.train()
    trainer.save_model("model_local/out/phi3-worldcup-lora")
    print("Modelo LoRA guardado en model_local/out/phi3-worldcup-lora")


if __name__ == "__main__":
    main()
