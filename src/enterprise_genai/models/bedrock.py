"""Small, transparent Bedrock helpers used before introducing frameworks."""

import boto3

from enterprise_genai.config import get_settings


def _session() -> boto3.Session:
    settings = get_settings()
    return boto3.Session(
        profile_name=settings.aws_profile or None,
        region_name=settings.aws_region,
    )


def bedrock_runtime():
    settings = get_settings()
    return _session().client("bedrock-runtime", region_name=settings.aws_region)


def converse_text(
    user_message: str,
    *,
    system_prompt: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 500,
    model_id: str | None = None,
) -> dict:
    """Invoke a Bedrock conversational model and return text plus usage metadata.

    This intentionally exposes the main request/response fields so M01 students
    can see what a framework will later abstract.
    """
    settings = get_settings()
    selected_model = model_id or settings.bedrock_text_model_id
    if not selected_model:
        raise ValueError("BEDROCK_TEXT_MODEL_ID is not configured")

    kwargs = {
        "modelId": selected_model,
        "messages": [{"role": "user", "content": [{"text": user_message}]}],
        "inferenceConfig": {
            "temperature": temperature,
            "maxTokens": max_tokens,
        },
    }
    if system_prompt:
        kwargs["system"] = [{"text": system_prompt}]

    response = bedrock_runtime().converse(**kwargs)
    text = response["output"]["message"]["content"][0]["text"]
    return {
        "text": text,
        "usage": response.get("usage", {}),
        "metrics": response.get("metrics", {}),
        "model_id": selected_model,
    }
