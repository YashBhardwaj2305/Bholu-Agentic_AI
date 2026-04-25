"""
Part 2 — Bholu Executor Agent (Secure Framework)

The Executor is the "body" — it executes validated actions.
CRITICAL CONSTRAINT: The Executor ONLY accepts structured JSON from the Validator.
It never reads raw user input or email content directly.
It has no reasoning capability — it just executes what it's told.

The Executor's tool set is RESTRICTED:
- No send_data tool (no exfiltration possible)
- No read_credentials_store tool (no credential access)
- Only the tools that match the allowed schemas
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from validator import ValidationResult

# Paths
INBOX_PATH = os.path.join(os.path.dirname(__file__), "..", "shared", "inbox.json")


class ExecutorAgent:
    """
    The Executor Agent — runs validated, schema-compliant actions only.
    Has no reasoning capability and no access to raw user input.
    """

    def __init__(self):
        # The Executor's tool registry — deliberately limited
        self._tools = {
            "read_emails": self._tool_read_emails,
            "read_file": self._tool_read_file,
            "write_file": self._tool_write_file,
            "send_email": self._tool_send_email,
            "summarize": self._tool_summarize,
        }
        self.execution_log = []

    def execute(self, validation_result: ValidationResult) -> dict:
        """
        Execute a validated action.
        Only accepts ValidationResult objects that have passed=True.

        Returns:
            dict with keys:
                - success: bool
                - output: str
                - action: str
                - error: str or None
        """
        if not validation_result.passed:
            return {
                "success": False,
                "output": None,
                "action": validation_result.action,
                "error": f"Cannot execute: validation failed — {validation_result.rejection_reason}"
            }

        action = validation_result.action
        parameters = validation_result.parameters or {}

        if action not in self._tools:
            return {
                "success": False,
                "output": None,
                "action": action,
                "error": f"No executor tool found for action '{action}'"
            }

        try:
            output = self._tools[action](**parameters)
            log_entry = {
                "action": action,
                "parameters": parameters,
                "success": True,
                "output_preview": str(output)[:200]
            }
            self.execution_log.append(log_entry)
            return {
                "success": True,
                "output": output,
                "action": action,
                "error": None
            }
        except Exception as e:
            log_entry = {
                "action": action,
                "parameters": parameters,
                "success": False,
                "error": str(e)
            }
            self.execution_log.append(log_entry)
            return {
                "success": False,
                "output": None,
                "action": action,
                "error": str(e)
            }

    # ─────────────────────────────────────────────
    # Executor Tools (restricted set)
    # ─────────────────────────────────────────────

    def _tool_read_emails(self, query: str = "all") -> str:
        """Read emails from the inbox."""
        try:
            with open(INBOX_PATH, "r") as f:
                inbox = json.load(f)

            emails = inbox.get("emails", [])

            if query.lower() == "all":
                result = []
                for email in emails:
                    result.append(
                        f"[Email #{email['id']}]\n"
                        f"From: {email['from']}\n"
                        f"Subject: {email['subject']}\n"
                        f"Date: {email['date']}\n"
                        f"Body:\n{email['body']}\n"
                        f"{'='*60}"
                    )
                return "\n\n".join(result)
            else:
                filtered = [
                    e for e in emails
                    if query.lower() in e["subject"].lower()
                    or query.lower() in e["from"].lower()
                ]
                if not filtered:
                    return f"No emails found matching '{query}'."
                result = []
                for email in filtered:
                    result.append(
                        f"[Email #{email['id']}]\n"
                        f"From: {email['from']}\n"
                        f"Subject: {email['subject']}\n"
                        f"Date: {email['date']}\n"
                        f"Body:\n{email['body']}\n"
                        f"{'='*60}"
                    )
                return "\n\n".join(result)

        except FileNotFoundError:
            return "Error: Inbox not found."

    def _tool_read_file(self, filepath: str) -> str:
        """Read a file (non-sensitive paths only — already validated)."""
        try:
            with open(filepath, "r") as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: File '{filepath}' not found."
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def _tool_write_file(self, filepath: str, content: str) -> str:
        """Write content to a file."""
        try:
            with open(filepath, "w") as f:
                f.write(content)
            return f"File '{filepath}' written successfully ({len(content)} characters)."
        except Exception as e:
            return f"Error writing file: {str(e)}"

    def _tool_send_email(self, to: str, subject: str, body: str) -> str:
        """
        Send an email to a trusted recipient.
        (Simulated — logs to file instead of real SMTP)
        """
        log_path = os.path.join(os.path.dirname(__file__), "sent_emails_log.json")
        entry = {"to": to, "subject": subject, "body": body}

        try:
            existing = []
            if os.path.exists(log_path):
                with open(log_path) as f:
                    existing = json.load(f)
            existing.append(entry)
            with open(log_path, "w") as f:
                json.dump(existing, f, indent=2)
        except Exception:
            pass

        return f"Email sent to {to} with subject '{subject}'. [SIMULATION: logged to sent_emails_log.json]"

    def _tool_summarize(self, content: str, format: str = "paragraph") -> str:
        """Return content directly — used for greetings and plain responses too."""
        if format == "bullet_points":
            lines = content.strip().split("\n")
            bullets = [f"• {line.strip()}" for line in lines if line.strip()][:10]
            return "\n".join(bullets) if bullets else content
        else:
            return content
