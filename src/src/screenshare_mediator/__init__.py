"""Synthetic utilities and runtime path for the anonymous scaffold."""

from .audit import AuditLogger
from .capture import SyntheticCaptureAdapter
from .fixture_loader import EXPECTED_SCENARIO_CLASSES, load_fixture_index, validate_fixture_set
from .memory import SessionMemoryGate
from .models import CapturedSession, MediatedSession, OutputGuardContext, OutputGuardDecision, PolicyDecision, RuntimeResult
from .output_guard import OutputGuard
from .policy import ConsentPolicyEngine
from .redaction import RedactionEngine
from .runtime import RuntimeMediator, assistant_candidate_output

__all__ = [
    "AuditLogger",
    "CapturedSession",
    "ConsentPolicyEngine",
    "EXPECTED_SCENARIO_CLASSES",
    "MediatedSession",
    "OutputGuard",
    "OutputGuardContext",
    "OutputGuardDecision",
    "PolicyDecision",
    "RedactionEngine",
    "RuntimeMediator",
    "RuntimeResult",
    "SessionMemoryGate",
    "SyntheticCaptureAdapter",
    "assistant_candidate_output",
    "load_fixture_index",
    "validate_fixture_set",
]
