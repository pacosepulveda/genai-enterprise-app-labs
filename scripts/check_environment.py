#!/usr/bin/env python
"""Preflight checks for the course Codespace."""

from pathlib import Path
import importlib
import os
import platform
import sqlite3

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]


def result(ok: bool, label: str, detail: str = "") -> None:
    mark = "✓" if ok else "✗"
    suffix = f" — {detail}" if detail else ""
    print(f"{mark} {label}{suffix}")


def check_import(module: str) -> bool:
    try:
        importlib.import_module(module)
        result(True, f"Python package: {module}")
        return True
    except Exception as exc:  # diagnostic script: report rather than fail early
        result(False, f"Python package: {module}", str(exc))
        return False


def main() -> int:
    failures = 0
    print("Enterprise GenAI Course — environment check\n")
    result(True, "Python", platform.python_version())

    for module in ["boto3", "streamlit", "torch", "sklearn", "langchain", "langgraph", "chromadb"]:
        failures += not check_import(module)

    db_path = ROOT / "data" / "enterprise.db"
    if db_path.exists():
        try:
            with sqlite3.connect(db_path) as conn:
                count = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
            result(True, "Enterprise database", f"{count} sample customers")
        except Exception as exc:
            result(False, "Enterprise database", str(exc))
            failures += 1
    else:
        result(False, "Enterprise database", "run python scripts/init_database.py")
        failures += 1

    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
    profile = os.getenv("AWS_PROFILE") or None
    api_key_present = bool(os.getenv("AWS_BEARER_TOKEN_BEDROCK"))

    try:
        import boto3

        session = boto3.Session(profile_name=profile, region_name=region)

        if api_key_present:
            result(True, "Bedrock API key", "AWS_BEARER_TOKEN_BEDROCK is available")
        else:
            identity = session.client("sts").get_caller_identity()
            result(True, "AWS credentials", f"account {identity['Account']}")

        bedrock = session.client("bedrock", region_name=region)
        model_count = len(bedrock.list_foundation_models().get("modelSummaries", []))
        result(True, "Bedrock access", f"{model_count} foundation models visible in {region}")

        runtime = session.client("bedrock-runtime", region_name=region)
        model_id = os.getenv(
            "BEDROCK_TEXT_MODEL_ID",
            "us.anthropic.claude-haiku-4-5-20251001-v1:0",
        ).strip()

        response = runtime.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": "Reply with exactly: BEDROCK_OK"}]}],
            inferenceConfig={"maxTokens": 20, "temperature": 0},
        )
        text = response["output"]["message"]["content"][0]["text"].strip()
        result("BEDROCK_OK" in text, "Bedrock model invocation", f"{text} — {model_id}")
        failures += "BEDROCK_OK" not in text
    except Exception as exc:
        result(False, "AWS / Bedrock", str(exc))
        failures += 1

    print("\nResult:", "READY" if failures == 0 else f"{failures} check(s) require attention")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
