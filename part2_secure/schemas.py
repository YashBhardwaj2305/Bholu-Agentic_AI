"""
Part 2 — JSON Action Schemas (The Deterministic Wall)

These schemas define EXACTLY what the Executor is allowed to do.
The Planner must produce a JSON action that matches one of these schemas.
If it doesn't match — the action is REJECTED before execution.

This is the core of the Dual-Agent security model:
  Probabilistic AI reasoning  →  Deterministic schema validation  →  Execution
"""

# ─────────────────────────────────────────────
# Allowed Action Schemas
# Each schema defines one permitted action type.
# ─────────────────────────────────────────────

READ_EMAILS_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "const": "read_emails"},
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": [],
            "additionalProperties": False
        }
    },
    "required": ["action", "parameters"],
    "additionalProperties": False
}

READ_FILE_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "const": "read_file"},
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    # Only allow reading from safe paths — no credentials store
                    "pattern": "^(?!.*credentials)(?!.*password)(?!.*secret)(?!.*token).*$"
                }
            },
            "required": ["filepath"],
            "additionalProperties": False
        }
    },
    "required": ["action", "parameters"],
    "additionalProperties": False
}

WRITE_FILE_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "const": "write_file"},
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["filepath", "content"],
            "additionalProperties": False
        }
    },
    "required": ["action", "parameters"],
    "additionalProperties": False
}

SEND_EMAIL_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "const": "send_email"},
        "parameters": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    # CRITICAL: Only allow sending to trusted domains
                    "pattern": "^[a-zA-Z0-9._%+\\-]+@(jnu\\.ac\\.in|gmail\\.com|trusted-org\\.com)$"
                },
                "subject": {"type": "string", "maxLength": 200},
                "body": {"type": "string", "maxLength": 5000}
            },
            "required": ["to", "subject", "body"],
            "additionalProperties": False
        }
    },
    "required": ["action", "parameters"],
    "additionalProperties": False
}

SUMMARIZE_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "const": "summarize"},
        "parameters": {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "format": {
                    "type": "string",
                    "enum": ["bullet_points", "paragraph", "table"]
                }
            },
            "required": ["content"],
            "additionalProperties": False
        }
    },
    "required": ["action", "parameters"],
    "additionalProperties": False
}

# ─────────────────────────────────────────────
# BLOCKED ACTIONS — These are explicitly forbidden.
# The Executor will NEVER have tools for these.
# ─────────────────────────────────────────────
BLOCKED_ACTIONS = {
    "send_data",           # No arbitrary data exfiltration
    "read_credentials_store",  # Credentials are never accessible to the agent
    "delete_file",         # No destructive file operations
    "execute_code",        # No arbitrary code execution
    "make_http_request",   # No arbitrary outbound requests
}

# ─────────────────────────────────────────────
# Master schema registry
# Maps action name → its JSON schema
# ─────────────────────────────────────────────
ACTION_SCHEMAS = {
    "read_emails": READ_EMAILS_SCHEMA,
    "read_file": READ_FILE_SCHEMA,
    "write_file": WRITE_FILE_SCHEMA,
    "send_email": SEND_EMAIL_SCHEMA,
    "summarize": SUMMARIZE_SCHEMA,
}

# Human-readable descriptions for the UI
ACTION_DESCRIPTIONS = {
    "read_emails": "✅ Read emails from inbox",
    "read_file": "✅ Read a file (non-sensitive paths only)",
    "write_file": "✅ Write content to a file",
    "send_email": "✅ Send email (trusted domains only: jnu.ac.in, gmail.com, trusted-org.com)",
    "summarize": "✅ Summarize content",
    "send_data": "🚫 BLOCKED — Arbitrary data transmission",
    "read_credentials_store": "🚫 BLOCKED — Credentials access",
    "delete_file": "🚫 BLOCKED — Destructive file operations",
    "execute_code": "🚫 BLOCKED — Arbitrary code execution",
    "make_http_request": "🚫 BLOCKED — Arbitrary HTTP requests",
}
