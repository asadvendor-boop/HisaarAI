"""Small correlated Cloud Trace surface for the one demo journey."""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import secrets
import threading
from collections.abc import Iterator
from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.trace import NonRecordingSpan, SpanContext, TraceFlags


_configured = False
_lock = threading.Lock()
_project_id = ""


def trace_id_for(correlation_id: str) -> str:
    return hashlib.sha256(correlation_id.encode()).hexdigest()[:32]


def configure_tracing(project_id: str) -> None:
    global _configured, _project_id
    with _lock:
        if _configured:
            return
        provider = TracerProvider(
            resource=Resource.create(
                {"service.name": "hisaarai", "gcp.project_id": project_id}
            )
        )
        provider.add_span_processor(
            SimpleSpanProcessor(CloudTraceSpanExporter(project_id=project_id))
        )
        trace.set_tracer_provider(provider)
        _project_id = project_id
        _configured = True


@contextmanager
def stage_span(
    correlation_id: str,
    stage: str,
    **attributes: Any,
) -> Iterator[None]:
    trace_hex = trace_id_for(correlation_id)
    parent = SpanContext(
        trace_id=int(trace_hex, 16),
        span_id=secrets.randbits(64) or 1,
        is_remote=True,
        trace_flags=TraceFlags(TraceFlags.SAMPLED),
    )
    context = trace.set_span_in_context(NonRecordingSpan(parent))
    safe_attributes = {
        key: value
        for key, value in attributes.items()
        if isinstance(value, (str, bool, int, float))
    }
    with trace.get_tracer("hisaarai").start_as_current_span(
        f"hisaarai.{stage}",
        context=context,
        attributes={"hisaar.correlation_id": correlation_id, **safe_attributes},
    ):
        print(
            json.dumps(
                {
                    "severity": "INFO",
                    "message": f"HisaarAI stage: {stage}",
                    "correlation_id": correlation_id,
                    "stage": stage,
                    "logging.googleapis.com/trace": (
                        f"projects/{_project_id}/traces/{trace_hex}"
                    ),
                    **safe_attributes,
                },
                separators=(",", ":"),
            ),
            flush=True,
        )
        yield
