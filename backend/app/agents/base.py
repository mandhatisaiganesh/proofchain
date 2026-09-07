"""Base agent configuration and model initialization."""

from __future__ import annotations

import logging
import os
from typing import Optional
from strands import Agent
from strands.models import BedrockModel
from ..config import get_settings

logger = logging.getLogger(__name__)


def get_bedrock_model() -> Optional[BedrockModel]:
    """
    Attempt to initialize AWS Bedrock model using environment credentials.
    Returns None if AWS credentials are not configured or invocation fails.
    """
    settings = get_settings()
    # Check if AWS credentials or profile are present
    if not (os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE") or os.getenv("AWS_DEFAULT_REGION")):
        return None

    try:
        model = BedrockModel(
            model_id=settings.bedrock_model_id,
            region_name=settings.aws_region,
        )
        return model
    except Exception as e:
        logger.warning(f"Could not initialize BedrockModel ({e}). Using deterministic offline reasoning engine.")
        return None
