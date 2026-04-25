"""
Part 2 — Dual-Agent Secure Framework: Streamlit UI

This UI demonstrates the secure Dual-Agent Planner–Executor architecture.
The same attack that hijacked Bholu in Part 1 is blocked here by the
deterministic JSON Schema Validator.
"""

import streamlit as st
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from dual_agent import DualAgentSystem
from schemas import ACTION_DESCRIPTIONS, BLOCKED_ACTIONS, ACTION_SCHEMAS

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Bholu AI — Secure Dual-Agent",
    page_icon="🛡️",
    layout="wide",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .secure-header {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    }
    .stage-planner {
        background: #e3f2fd;
        border: 2px solid #2196f3;
        border-radius: 8px;
        padding: 15px;
        margin: 8px 0;
    }
    .stage-validator-pass {
        background: #e8f5e9;
        border: 2px solid #4caf50;
        border-radius: 8px;
        padding: 15px;
        margin: 8px 0;
    }
    .stage-validator-fail {
        background: #fff3e0;
        border: 2px solid #ff9800;
        border-radius: 8px;
        padding: 15px;
        margin: 8px 0;
    }
    .stage-executor {
        background: #f3e5f5;
        border: 2px solid #9c27b0;
        border-radius: 8px;
        padding: 15px;
        margin: 8px 0;
    }
    .blocked-box {
        background: #fff3e0;
        border: 3px solid #ff9800;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
    }
    .success-box {
        background: #e8f5e9;
        border: 2px solid #4caf50;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .wall-divider {
        text-align: center;
        font-size: 1.5em;
        font-weight: bold;
        color: #ff9800;
        padding: 10px;
        border: 2px dashed #ff9800;
        border-radius: 8px;
        margin: 10px 0;
    }
    .schema-box {
        background: #f5f5f5;
        border-left: 4px solid #607d8b;
        padding: 10px;
        font-family: monospace;
        font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="secure-header">
    <h1>🛡️ Bholu AI — Secure Dual-Agent Framework</h1>
    <p>Planner → Deterministic Validator → Executor | Part 2: The Defense</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("🏗️ Architecture")
    st.markdown("""
    **Type:** Dual-Agent (Secure)
    
    **Components:**
    1. 🧠 **Planner** — Reasons, NO tools
    2. 🔒 **Validator** — Deterministic JSON Schema check
    3. ⚙️ **Executor** — Runs validated actions only
    
    **Security Guarantee:**
    > Even if the Planner is hijacked, the Validator blocks any action not matching the strict schema.
    """)

    st.divider()
    st.header("🔒 Allowed Actions")
    for action, desc in ACTION_DESCRIPTIONS.items():
        st.markdown(f"- {desc}")

    st.divider()
    st.header("🎯 Demo Steps")
    st.markdown("""
    1. Click **"Check my emails"** below
    2. Watch the pipeline: Planner → Validator → Executor
    3. See the **Validator BLOCK** the malicious action
    4. Compare with Part 1 where it succeeded
    """)

# ─────────────────────────────────────────────
# Initialize session state
# ─────────────────────────────────────────────
if "system" not in st.session_state:
    st.session_state.system = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pipeline_results" not in st.session_state:
    st.session_state.pipeline_results = []

# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["💬 Chat with Secure Bholu", "🔍 Pipeline Trace", "📋 Schema Reference"])

with tab1:
    # Ollama availability check
    import subprocess
    try:
        check = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        ollama_ok = check.returncode == 0
    except Exception:
        ollama_ok = False

    if not ollama_ok:
        st.warning("⚠️ Ollama not detected. Install from https://ollama.com then run: `ollama pull llama3`")

    # Initialize system
    if st.session_state.system is None:
        with st.spinner("Initializing Secure Bholu (loading llama3 via Ollama)..."):
            try:
                st.session_state.system = DualAgentSystem()
            except Exception as e:
                st.error(f"Failed to initialize: {e}")

    # Quick action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📬 Check my emails", use_container_width=True, type="primary"):
            st.session_state.pending_input = "Please check my emails and summarize what's there."
    with col2:
        if st.button("🔑 Try to access credentials", use_container_width=True):
            st.session_state.pending_input = "Read my credentials store and show me all passwords."
    with col3:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.system = None
            st.session_state.messages = []
            st.session_state.pipeline_results = []
            st.rerun()

    st.divider()

    # Display chat history
    for msg in st.session_state.messages:
        icon = "🛡️" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=icon):
            if msg.get("blocked"):
                st.markdown(f"""
                <div class="blocked-box">
                    🚫 <strong>ACTION BLOCKED by Validator</strong><br><br>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(msg["content"])

    # Handle pending input
    user_input = None
    if "pending_input" in st.session_state:
        user_input = st.session_state.pending_input
        del st.session_state.pending_input
    else:
        user_input = st.chat_input("Ask Secure Bholu anything...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        if st.session_state.system is None:
            with st.chat_message("assistant", avatar="🛡️"):
                st.error("System not initialized. Make sure Ollama is running and llama3 is pulled.")
        else:
            with st.chat_message("assistant", avatar="🛡️"):
                with st.spinner("Running secure pipeline..."):
                    try:
                        result = st.session_state.system.run(user_input)
                        st.session_state.pipeline_results.append(result)

                        validation = result.get("validation_result")
                        was_blocked = validation and not validation.passed

                        if was_blocked:
                            st.markdown(f"""
                            <div class="blocked-box">
                                🚫 <strong>ACTION BLOCKED by Deterministic Validator</strong><br><br>
                                <strong>Attempted Action:</strong> {validation.action}<br>
                                <strong>Category:</strong> {validation.rejection_category}<br>
                                <strong>Reason:</strong> {validation.rejection_reason}<br><br>
                                ✅ The system is safe. The Executor was never reached.
                            </div>
                            """, unsafe_allow_html=True)
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": result["final_response"],
                                "blocked": True
                            })
                        else:
                            st.markdown(f"""
                            <div class="success-box">
                                ✅ <strong>Action validated and executed successfully</strong>
                            </div>
                            """, unsafe_allow_html=True)
                            st.markdown(result["final_response"])
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": result["final_response"],
                                "blocked": False
                            })

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

with tab2:
    st.header("🔍 Pipeline Trace")
    st.markdown("*Full trace of every Planner → Validator → Executor run.*")

    if not st.session_state.pipeline_results:
        st.info("No pipeline runs yet. Start a conversation to see the trace.")
    else:
        for i, result in enumerate(reversed(st.session_state.pipeline_results)):
            with st.expander(f"Run #{len(st.session_state.pipeline_results) - i}: {result['user_request'][:60]}...", expanded=(i == 0)):

                for stage in result.get("pipeline_stages", []):
                    stage_name = stage["stage"]
                    status = stage["status"]

                    if stage_name == "PLANNER":
                        st.markdown(f"""
                        <div class="stage-planner">
                            🧠 <strong>Stage 1: PLANNER</strong> — Status: {status}<br>
                            <strong>JSON Plan Generated:</strong><br>
                            <code>{stage['details'].get('raw_output', 'N/A')[:400]}</code>
                        </div>
                        """, unsafe_allow_html=True)

                    elif stage_name == "VALIDATOR":
                        css_class = "stage-validator-pass" if status == "PASSED" else "stage-validator-fail"
                        icon = "✅" if status == "PASSED" else "🚫"
                        details = stage["details"]
                        reason_html = ""
                        if details.get("rejection_reason"):
                            reason_html = f"<br><strong>Rejection Reason:</strong> {details['rejection_reason']}"
                        st.markdown(f"""
                        <div class="{css_class}">
                            {icon} <strong>Stage 2: VALIDATOR (The Wall)</strong> — Status: {status}<br>
                            <strong>Action Checked:</strong> {details.get('action', 'N/A')}<br>
                            <strong>Category:</strong> {details.get('rejection_category', 'N/A')}
                            {reason_html}
                        </div>
                        """, unsafe_allow_html=True)

                    elif stage_name == "EXECUTOR":
                        st.markdown(f"""
                        <div class="stage-executor">
                            ⚙️ <strong>Stage 3: EXECUTOR</strong> — Status: {status}<br>
                            <strong>Output Preview:</strong> {str(stage['details'].get('output', ''))[:300]}
                        </div>
                        """, unsafe_allow_html=True)

with tab3:
    st.header("📋 Schema Reference")
    st.markdown("*The exact JSON schemas the Validator enforces. Any deviation = rejection.*")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ Allowed Actions")
        for action, schema in ACTION_SCHEMAS.items():
            with st.expander(f"`{action}`"):
                st.json(schema)

    with col2:
        st.subheader("🚫 Blocked Actions")
        for action in BLOCKED_ACTIONS:
            st.markdown(f"- **`{action}`** — {ACTION_DESCRIPTIONS.get(action, 'Blocked')}")

        st.divider()
        st.subheader("Why Determinism Wins")
        st.markdown("""
        | Defense | Type | Bypassable? |
        |---|---|---|
        | RLHF / Fine-tuning | Probabilistic | Yes — with clever rephrasing |
        | Input filters | Probabilistic | Yes — with encoding/obfuscation |
        | **JSON Schema Validation** | **Deterministic** | **No — math doesn't guess** |
        
        The schema validator doesn't "understand" the request.
        It checks: does this JSON match the allowed structure?
        If not → rejected. No exceptions. No probabilities.
        """)
