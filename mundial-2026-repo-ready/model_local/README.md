# Modelo local Mundial 2026

## Recomendación profesional

Primero usa API + JSON/CSV + reglas (`backend/services/qa_service.py`). Es gratis, rápido y fiable.

Entrena o carga modelo local solo si quieres una experiencia tipo ChatGPT con preguntas abiertas.

## Fase 1: Dataset

```bash
python model_local/scripts/build_qa_dataset.py
```

Genera:

```text
model_local/datasets/qa_worldcup_generated.jsonl
```

## Fase 2: Fine-tuning LoRA

Ejecuta en Colab o PC con GPU:

```bash
pip install -r backend/requirements-llm-training.txt
python model_local/scripts/train_lora_template.py
```

## Fase 3: Inferencia local barata

Para producción barata, mejor usar un modelo GGUF cuantizado con `llama-cpp-python` y conectar `backend/llm/local_llm.py`.

Ejemplo `.env`:

```env
LOCAL_MODEL_PATH=C:/modelos/Phi-3-mini-4k-instruct-q4.gguf
LOCAL_MODEL_CTX=4096
LOCAL_MODEL_THREADS=6
```

Después llama:

```json
POST /api/qa
{"question":"¿quién es el máximo goleador?", "use_local_model":true}
```
