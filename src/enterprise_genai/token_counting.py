"""Token counting helper for Claude models served through Bedrock Mantle."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

from enterprise_genai.config import get_settings


MANTLE_MODEL_ID = "anthropic.claude-haiku-4-5"


def _session() -> boto3.Session:
    settings = get_settings()
    return boto3.Session(
        profile_name=settings.aws_profile or None,
        region_name=settings.aws_region,
    )


def count_claude_tokens(
    messages: list[dict],
    system_text: str | None = None,
    *,
    model_id: str = MANTLE_MODEL_ID,
) -> int:
    """Count Claude input tokens through Bedrock Mantle using SigV4.

    Claude Haiku 4.5 is served through a geo inference profile on
    ``bedrock-runtime`` and does not support ``bedrock-runtime.CountTokens``.
    AWS exposes Anthropic's token-counting endpoint for this model through
    ``bedrock-mantle`` instead.

    The helper intentionally accepts only the text-only message shape used by
    M05-P01 so the notebook can focus on tokens rather than HTTP signing.
    """

    settings = get_settings()
    region = settings.aws_region
    url = f"https://bedrock-mantle.{region}.api.aws/anthropic/v1/messages/count_tokens"

    payload: dict = {
        "model": model_id,
        "messages": messages,
    }
    if system_text:
        payload["system"] = system_text

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
    }

    session = _session()
    credentials = session.get_credentials()
    if credentials is None:
        raise RuntimeError("AWS credentials are not available")

    request = AWSRequest(method="POST", url=url, data=body, headers=headers)
    SigV4Auth(credentials.get_frozen_credentials(), "bedrock-mantle", region).add_auth(request)
    prepared = request.prepare()

    http_request = urllib.request.Request(
        url,
        data=body,
        headers=dict(prepared.headers.items()),
        method="POST",
    )

    try:
        with urllib.request.urlopen(http_request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Bedrock Mantle token counting failed with HTTP {exc.code}: {error_body}"
        ) from exc

    if "input_tokens" not in result:
        raise RuntimeError(f"Unexpected token-count response: {result}")

    return int(result["input_tokens"])
