"""Shared exception types for provider pipeline execution."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PipelineExecutionError(Exception):
    """Represents a provider-stage execution failure in the V2 pipeline."""

    stage: str
    provider: str
    message: str
    status_code: int | None = None
    retryable: bool = False
    cause_type: str | None = None

    def __str__(self) -> str:
        return self.message
