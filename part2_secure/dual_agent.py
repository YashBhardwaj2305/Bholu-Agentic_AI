"""
Part 2 — Dual-Agent Orchestrator

Coordinates the full Planner → Validator → Executor pipeline.

Flow:
  User Request
      ↓
  [Planner Agent] — reasons, produces JSON plan (NO tools)
      ↓
  [JSON Schema Validator] — deterministic check (THE WALL)
      ↓ PASS                    ↓ REJECT
  [Executor Agent]          Return rejection reason
  (runs the action)
      ↓
  Result to user
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))

from planner import PlannerAgent
from validator import DeterministicValidator
from executor import ExecutorAgent


class DualAgentSystem:
    """
    The secure Dual-Agent Planner–Executor framework.
    Orchestrates the full pipeline for a single user request.
    """

    def __init__(self):
        self.planner = PlannerAgent()
        self.validator = DeterministicValidator()
        self.executor = ExecutorAgent()
        self.pipeline_log = []  # Full audit trail

    def run(self, user_request: str) -> dict:
        """
        Process a user request through the full secure pipeline.

        Returns a dict with:
            - user_request: str
            - planner_output: dict (raw + parsed plan)
            - validation_result: ValidationResult
            - execution_result: dict or None
            - final_response: str
            - pipeline_stages: list of stage summaries
        """
        pipeline_stages = []

        # ── Stage 1: Planner ────────────────────────────────────────────
        stage1 = {"stage": "PLANNER", "status": None, "details": None}

        # If the request involves emails, first fetch them as context
        context_data = ""
        if any(word in user_request.lower() for word in ["email", "inbox", "mail", "message"]):
            # Read emails as raw data (not as instructions)
            inbox_path = os.path.join(os.path.dirname(__file__), "..", "shared", "inbox.json")
            try:
                with open(inbox_path) as f:
                    inbox = json.load(f)
                context_data = json.dumps(inbox, indent=2)
            except Exception:
                context_data = ""

        planner_output = self.planner.plan(user_request, context_data=context_data)
        stage1["status"] = "COMPLETED" if planner_output["parsed_plan"] else "PARSE_ERROR"
        stage1["details"] = planner_output
        pipeline_stages.append(stage1)

        if planner_output["parse_error"]:
            return {
                "user_request": user_request,
                "planner_output": planner_output,
                "validation_result": None,
                "execution_result": None,
                "final_response": f"Planner failed to produce valid JSON: {planner_output['parse_error']}",
                "pipeline_stages": pipeline_stages,
            }

        # ── Stage 2: Validator (The Wall) ───────────────────────────────
        stage2 = {"stage": "VALIDATOR", "status": None, "details": None}

        validation_result = self.validator.validate(planner_output["raw_output"])
        stage2["status"] = "PASSED" if validation_result.passed else "REJECTED"
        stage2["details"] = {
            "passed": validation_result.passed,
            "action": validation_result.action,
            "rejection_reason": validation_result.rejection_reason,
            "rejection_category": validation_result.rejection_category,
        }
        pipeline_stages.append(stage2)

        if not validation_result.passed:
            final_response = (
                f"🚫 ACTION BLOCKED by Deterministic Validator\n\n"
                f"Category: {validation_result.rejection_category}\n"
                f"Reason: {validation_result.rejection_reason}\n\n"
                f"The Planner attempted to plan action '{validation_result.action}', "
                f"which was rejected before reaching the Executor."
            )
            return {
                "user_request": user_request,
                "planner_output": planner_output,
                "validation_result": validation_result,
                "execution_result": None,
                "final_response": final_response,
                "pipeline_stages": pipeline_stages,
            }

        # ── Stage 3: Executor ───────────────────────────────────────────
        stage3 = {"stage": "EXECUTOR", "status": None, "details": None}

        execution_result = self.executor.execute(validation_result)
        stage3["status"] = "SUCCESS" if execution_result["success"] else "FAILED"
        stage3["details"] = execution_result
        pipeline_stages.append(stage3)

        if execution_result["success"]:
            final_response = execution_result["output"]
        else:
            final_response = f"Execution failed: {execution_result['error']}"

        result = {
            "user_request": user_request,
            "planner_output": planner_output,
            "validation_result": validation_result,
            "execution_result": execution_result,
            "final_response": final_response,
            "pipeline_stages": pipeline_stages,
        }

        self.pipeline_log.append(result)
        return result
