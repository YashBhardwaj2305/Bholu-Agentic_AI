"""
Part 2 — The JSON Schema Validator (The Deterministic Wall)

This is the security boundary between the Planner and the Executor.
It is NOT probabilistic — it is a deterministic algorithm.

The Planner (AI) produces a JSON action plan.
The Validator checks it against strict schemas.
Only if it passes does the Executor run it.

This moves security from "AI guessing" to "mathematical validation".
"""

import json
import re
from typing import Tuple, Optional
from jsonschema import validate, ValidationError, SchemaError

from schemas import ACTION_SCHEMAS, BLOCKED_ACTIONS


class ValidationResult:
    """Result of a schema validation check."""

    def __init__(
        self,
        passed: bool,
        action: Optional[str] = None,
        parameters: Optional[dict] = None,
        rejection_reason: Optional[str] = None,
        rejection_category: Optional[str] = None,
    ):
        self.passed = passed
        self.action = action
        self.parameters = parameters
        self.rejection_reason = rejection_reason
        self.rejection_category = rejection_category

    def __repr__(self):
        if self.passed:
            return f"ValidationResult(PASSED, action={self.action})"
        return f"ValidationResult(REJECTED, reason={self.rejection_reason})"


class DeterministicValidator:
    """
    The Secure Wall between Planner and Executor.

    Validation pipeline:
    1. Parse JSON (is it valid JSON at all?)
    2. Check for blocked actions (explicit deny list)
    3. Check action is in allowed list
    4. Validate against the action's JSON schema
    5. Run additional semantic checks (e.g., domain allowlist)
    """

    def __init__(self):
        self.validation_log = []  # Audit trail of all validation attempts

    def validate(self, planner_output: str) -> ValidationResult:
        """
        Validate a planner's JSON output.
        Returns a ValidationResult with pass/fail and reason.
        """
        log_entry = {"input": planner_output[:500], "result": None}

        # ── Step 1: Parse JSON ──────────────────────────────────────────
        try:
            action_plan = json.loads(planner_output)
        except json.JSONDecodeError as e:
            result = ValidationResult(
                passed=False,
                rejection_reason=f"Invalid JSON: {str(e)}",
                rejection_category="PARSE_ERROR"
            )
            log_entry["result"] = repr(result)
            self.validation_log.append(log_entry)
            return result

        # ── Step 2: Check for blocked actions ──────────────────────────
        action = action_plan.get("action", "")

        if action in BLOCKED_ACTIONS:
            result = ValidationResult(
                passed=False,
                action=action,
                rejection_reason=(
                    f"Action '{action}' is explicitly blocked. "
                    f"This action is not permitted under any circumstances."
                ),
                rejection_category="BLOCKED_ACTION"
            )
            log_entry["result"] = repr(result)
            self.validation_log.append(log_entry)
            return result

        # ── Step 3: Check action is in allowed list ─────────────────────
        if action not in ACTION_SCHEMAS:
            result = ValidationResult(
                passed=False,
                action=action,
                rejection_reason=(
                    f"Action '{action}' is not in the allowed action list. "
                    f"Allowed actions: {list(ACTION_SCHEMAS.keys())}"
                ),
                rejection_category="UNKNOWN_ACTION"
            )
            log_entry["result"] = repr(result)
            self.validation_log.append(log_entry)
            return result

        # ── Step 4: Validate against JSON schema ────────────────────────
        schema = ACTION_SCHEMAS[action]
        try:
            validate(instance=action_plan, schema=schema)
        except ValidationError as e:
            result = ValidationResult(
                passed=False,
                action=action,
                rejection_reason=f"Schema validation failed: {e.message}",
                rejection_category="SCHEMA_VIOLATION"
            )
            log_entry["result"] = repr(result)
            self.validation_log.append(log_entry)
            return result

        # ── Step 5: Semantic checks ─────────────────────────────────────
        semantic_check = self._semantic_checks(action, action_plan.get("parameters", {}))
        if not semantic_check[0]:
            result = ValidationResult(
                passed=False,
                action=action,
                rejection_reason=semantic_check[1],
                rejection_category="SEMANTIC_VIOLATION"
            )
            log_entry["result"] = repr(result)
            self.validation_log.append(log_entry)
            return result

        # ── All checks passed ───────────────────────────────────────────
        result = ValidationResult(
            passed=True,
            action=action,
            parameters=action_plan.get("parameters", {}),
        )
        log_entry["result"] = repr(result)
        self.validation_log.append(log_entry)
        return result

    def _semantic_checks(self, action: str, parameters: dict) -> Tuple[bool, str]:
        """
        Additional semantic validation beyond JSON schema.
        Returns (passed: bool, reason: str)
        """

        if action == "send_email":
            to = parameters.get("to", "")
            # Double-check domain allowlist (belt-and-suspenders)
            allowed_domains = ["jnu.ac.in", "gmail.com", "trusted-org.com"]
            domain = to.split("@")[-1] if "@" in to else ""
            if domain not in allowed_domains:
                return False, (
                    f"Recipient domain '{domain}' is not in the trusted domain list. "
                    f"Allowed: {allowed_domains}"
                )

        if action == "read_file":
            filepath = parameters.get("filepath", "")
            # Block access to sensitive file patterns
            sensitive_patterns = [
                r"credentials",
                r"password",
                r"secret",
                r"\.env",
                r"private_key",
                r"id_rsa",
                r"\.pem",
                r"token",
            ]
            for pattern in sensitive_patterns:
                if re.search(pattern, filepath, re.IGNORECASE):
                    return False, (
                        f"File path '{filepath}' matches a sensitive pattern ('{pattern}'). "
                        f"Access to sensitive files is not permitted."
                    )

        if action == "write_file":
            filepath = parameters.get("filepath", "")
            # Block writing to system paths
            blocked_paths = ["/etc/", "/sys/", "/proc/", "C:\\Windows\\", "C:\\System32\\"]
            for blocked in blocked_paths:
                if filepath.startswith(blocked):
                    return False, f"Writing to system path '{filepath}' is not permitted."

        return True, "OK"

    def get_audit_log(self) -> list:
        """Return the full validation audit log."""
        return self.validation_log
