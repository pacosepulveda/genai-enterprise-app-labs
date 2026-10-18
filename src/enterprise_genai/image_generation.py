"""Image generation helpers used by M04-P03 and the later Create surface."""

from __future__ import annotations

import base64
import json
import time
from typing import Literal

import boto3

from enterprise_genai.config import get_settings


AspectRatio = Literal["16:9", "1:1", "21:9", "2:3", "3:2", "4:5", "5:4", "9:16", "9:21"]
OutputFormat = Literal["png", "jpeg"]


def _image_runtime():
    settings = get_settings()
    session = boto3.Session(
        profile_name=settings.aws_profile or None,
        region_name=settings.bedrock_image_region,
    )
    return session.client("bedrock-runtime", region_name=settings.bedrock_image_region)


def generate_image(
    prompt: str,
    *,
    negative_prompt: str | None = None,
    aspect_ratio: AspectRatio = "16:9",
    seed: int = 42,
    output_format: OutputFormat = "png",
    model_id: str | None = None,
) -> dict:
    """Generate one image with the configured Bedrock image model.

    The helper deliberately keeps the model-native request visible instead of
    hiding it behind a framework. This makes prompt, seed, aspect ratio and
    response metadata inspectable during the course.
    """

    if not prompt.strip():
        raise ValueError("prompt cannot be empty")
    if seed < 0 or seed > 4_294_967_295:
        raise ValueError("seed must be between 0 and 4294967295")

    settings = get_settings()
    selected_model = model_id or settings.bedrock_image_model_id
    if not selected_model:
        raise ValueError("BEDROCK_IMAGE_MODEL_ID is not configured")

    payload: dict = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "seed": seed,
        "output_format": output_format,
    }
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt

    started = time.perf_counter()
    response = _image_runtime().invoke_model(
        modelId=selected_model,
        body=json.dumps(payload),
        contentType="application/json",
        accept="application/json",
    )
    client_ms = (time.perf_counter() - started) * 1000

    model_response = json.loads(response["body"].read().decode("utf-8"))
    finish_reasons = model_response.get("finish_reasons", [])
    finish_reason = finish_reasons[0] if finish_reasons else None

    if finish_reason is not None:
        raise RuntimeError(f"Image generation did not complete: {finish_reason}")

    images = model_response.get("images", [])
    if not images:
        raise RuntimeError("Image generation returned no image data")

    image_bytes = base64.b64decode(images[0])
    seeds = model_response.get("seeds", [])
    returned_seed = seeds[0] if seeds else seed

    return {
        "image_bytes": image_bytes,
        "model_id": selected_model,
        "region": settings.bedrock_image_region,
        "seed": returned_seed,
        "requested_seed": seed,
        "aspect_ratio": aspect_ratio,
        "output_format": output_format,
        "finish_reason": finish_reason,
        "latency_ms": round(client_ms),
        "request": payload,
        "response_metadata": response.get("ResponseMetadata", {}),
    }
