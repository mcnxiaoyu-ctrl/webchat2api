from __future__ import annotations

from dataclasses import dataclass


GPT_PROVIDER = "gpt"
GROK_PROVIDER = "grok"
SUPPORTED_PROVIDERS = {GPT_PROVIDER, GROK_PROVIDER}


@dataclass(frozen=True)
class ModelSpec:
    id: str
    provider: str
    owned_by: str
    upstream_model: str | None = None
    default_reasoning_effort: str | None = None

    def model_metadata(self) -> dict[str, object]:
        return {
            "id": self.id,
            "object": "model",
            "created": 0,
            "owned_by": self.owned_by,
            "provider": self.provider,
            "permission": [],
            "root": self.id,
            "parent": None,
        }


GPT_FALLBACK_MODEL_IDS = (
    "auto",
    "gpt-5",
    "gpt-5-thinking",
    "gpt-4o",
    "gpt-4o-mini",
)

GROK_MODEL_SPECS = (
    ModelSpec("grok-4.3", GROK_PROVIDER, "xai", "grok-4.3", "high"),
    ModelSpec("grok-4", GROK_PROVIDER, "xai", "grok-4", "high"),
    ModelSpec("grok-4.20", GROK_PROVIDER, "xai", "grok-4.20", "high"),
    ModelSpec("grok-4.20-reasoning", GROK_PROVIDER, "xai", "grok-4.20-reasoning"),
    ModelSpec("grok-4.20-non-reasoning", GROK_PROVIDER, "xai", "grok-4.20-non-reasoning"),
    ModelSpec("grok-4.20-multi-agent", GROK_PROVIDER, "xai", "grok-4.20-multi-agent"),
)

MODEL_REGISTRY = {spec.id: spec for spec in GROK_MODEL_SPECS}
for model_id in GPT_FALLBACK_MODEL_IDS:
    MODEL_REGISTRY[model_id] = ModelSpec(model_id, GPT_PROVIDER, "chatgpt", model_id)


def normalize_provider(value: object) -> str:
    provider = str(value or "").strip().lower().replace("_", "-")
    if provider in {"", "openai", "chatgpt", "chat-gpt", "gpt"}:
        return GPT_PROVIDER
    if provider in {"grok", "xai", "x-ai"}:
        return GROK_PROVIDER
    return GPT_PROVIDER


def resolve_model(model_id: object) -> ModelSpec:
    model = str(model_id or "auto").strip() or "auto"
    spec = MODEL_REGISTRY.get(model)
    if spec is not None:
        return spec
    if model.startswith("grok-"):
        return ModelSpec(model, GROK_PROVIDER, "xai", model)
    return ModelSpec(model, GPT_PROVIDER, "chatgpt", model)


def grok_model_metadata() -> list[dict[str, object]]:
    return [spec.model_metadata() for spec in GROK_MODEL_SPECS]


def gpt_fallback_model_metadata() -> list[dict[str, object]]:
    return [MODEL_REGISTRY[model_id].model_metadata() for model_id in GPT_FALLBACK_MODEL_IDS]
