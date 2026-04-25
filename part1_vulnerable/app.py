"""
Part 1 — Bholu AI: Streamlit UI (Vulnerable Demo)

This UI demonstrates the vulnerable single-agent architecture.
Watch Bholu get hijacked by the malicious email in the inbox.
"""

import streamlit as st
import json
import os
import sys

# Add parent directory to path so we can import from shared/
sys.path.insert(0, os.path.dirname(__file__))

from agent import create_bholu_agent, run_bholu

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Bholu AI — Vulnerable Agent",
    page_icon="🤖",
    layout="wide",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .bholu-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    }
    .warning-box {
        background: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .danger-box {
        background: #f8d7da;
        border: 2px solid #dc3545;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .info-box {
        background: #d1ecf1;
        border: 2px solid #17a2b8;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .tool-call {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 10px;
        margin: 5px 0;
        font-family: monospace;
        font-size: 0.85em;
    }
    .hijacked {
        background: #ffebee;
        border-left: 4px solid #f44336;
        padding: 10px;
        margin: 5px 0;
        font-family: monospace;
        font-size: 0.85em;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="bholu-header">
    <h1>🤖 Bholu AI — Personal Assistant</h1>
    <p>Powered by a Single-Agent Architecture | Part 1: The Vulnerable System</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar — Architecture Info
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("🏗️ Architecture")
    st.markdown("""
    **Type:** Single-Agent (Vulnerable)
    
    **Components:**
    - 🧠 LLM (Llama 3 via Ollama) — Reasoning + Planning
    - 🦾 Tools — Direct execution access
    - 💾 Memory — Conversation history
    
    **Fatal Flaw:**
    > The context window flattens ALL inputs — system prompt, user query, and retrieved data — into one undifferentiated token sequence.
    
    **Attack Vector:**
    > Indirect Prompt Injection (IDPI) hidden in Email #3
    """)

    st.divider()
    st.header("📬 Inbox Preview")

    inbox_path = os.path.join(os.path.dirname(__file__), "..", "shared", "inbox.json")
    try:
        with open(inbox_path) as f:
            inbox = json.load(f)
        for email in inbox["emails"]:
            icon = "☠️" if email["id"] == 3 else "📧"
            label = " ← INFECTED" if email["id"] == 3 else ""
            st.markdown(f"{icon} **#{email['id']}** {email['subject'][:35]}...{label}")
    except Exception:
        st.error("Could not load inbox.")

    st.divider()
    st.header("🎯 Demo Steps")
    st.markdown("""
    1. Click **"Check my emails"** below
    2. Watch Bholu read all emails
    3. Observe the hijack when Email #3 is processed
    4. Check the **Exfiltration Log** tab
    """)

# ─────────────────────────────────────────────
# Initialize session state
# ─────────────────────────────────────────────
if "agent" not in st.session_state:
    st.session_state.agent = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "steps_log" not in st.session_state:
    st.session_state.steps_log = []
if "hijacked" not in st.session_state:
    st.session_state.hijacked = False

# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["💬 Chat with Bholu", "🔍 Tool Execution Log", "☠️ Exfiltration Log"])

with tab1:
    # Ollama availability check
    import subprocess
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        ollama_ok = result.returncode == 0
    except Exception:
        ollama_ok = False

    if not ollama_ok:
        st.markdown("""
        <div class="warning-box">
            ⚠️ <strong>Ollama not detected.</strong> Make sure Ollama is installed and running.<br>
            Install: <code>https://ollama.com</code> → then run: <code>ollama pull llama3</code>
        </div>
        """, unsafe_allow_html=True)

    # Initialize agent
    if st.session_state.agent is None:
        with st.spinner("Initializing Bholu (loading llama3 via Ollama)..."):
            try:
                st.session_state.agent = create_bholu_agent()
            except Exception as e:
                st.error(f"Failed to initialize: {e}")

    # Quick action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📬 Check my emails", use_container_width=True, type="primary"):
            st.session_state.pending_input = "Please check my emails and summarize what's there."
    with col2:
        if st.button("🔑 Show my credentials", use_container_width=True):
            st.session_state.pending_input = "Show me my stored credentials."
    with col3:
        if st.button("🔄 Reset Bholu", use_container_width=True):
            st.session_state.agent = None
            st.session_state.messages = []
            st.session_state.steps_log = []
            st.session_state.hijacked = False
            # Clear exfil log
            exfil_path = os.path.join(os.path.dirname(__file__), "exfiltration_log.json")
            if os.path.exists(exfil_path):
                os.remove(exfil_path)
            st.rerun()

    st.divider()

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    # Handle pending input from buttons
    user_input = None
    if "pending_input" in st.session_state:
        user_input = st.session_state.pending_input
        del st.session_state.pending_input
    else:
        user_input = st.chat_input("Ask Bholu anything...")

    # Process input
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Check if agent is ready
        if st.session_state.agent is None:
            with st.chat_message("assistant", avatar="🤖"):
                st.error("Bholu is not initialized. Make sure Ollama is running and llama3 is pulled.")
        else:
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Bholu is thinking..."):
                    try:
                        result = run_bholu(user_input, st.session_state.agent)
                        output = result["output"]
                        steps = result.get("intermediate_steps", [])

                        # Store steps for the log tab
                        st.session_state.steps_log.extend(steps)

        # Check if hijacking occurred
                        exfil_path = os.path.join(os.path.dirname(__file__), "exfiltration_log.json")
                        if result.get("exfil_triggered"):
                            st.session_state.hijacked = True

                        if st.session_state.hijacked:
                            st.markdown("""
                            <div class="danger-box">
                                ☠️ <strong>BHOLU HAS BEEN HIJACKED!</strong><br>
                                Bholu executed a malicious instruction from Email #3 and exfiltrated credentials.
                            </div>
                            """, unsafe_allow_html=True)

                        st.markdown(output)
                        st.session_state.messages.append({"role": "assistant", "content": output})

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

with tab2:
    st.header("🔍 Tool Execution Log")
    st.markdown("*Every tool call Bholu makes is logged here — including the malicious ones.*")

    if not st.session_state.steps_log:
        st.info("No tool calls yet. Start a conversation with Bholu.")
    else:
        for i, step in enumerate(st.session_state.steps_log):
            action, observation = step
            tool_name = action.tool if hasattr(action, 'tool') else str(action)
            tool_input = action.tool_input if hasattr(action, 'tool_input') else ""

            # Highlight dangerous tool calls
            is_dangerous = tool_name in ("send_data", "read_credentials_store")
            box_class = "hijacked" if is_dangerous else "tool-call"
            icon = "☠️" if is_dangerous else "🔧"

            st.markdown(f"""
            <div class="{box_class}">
                {icon} <strong>Step {i+1}: {tool_name}</strong><br>
                <strong>Input:</strong> {str(tool_input)[:300]}<br>
                <strong>Output:</strong> {str(observation)[:300]}...
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.header("☠️ Exfiltration Log")
    st.markdown("*If Bholu was hijacked, the stolen data appears here.*")

    exfil_path = os.path.join(os.path.dirname(__file__), "exfiltration_log.json")

    if not os.path.exists(exfil_path):
        st.markdown("""
        <div class="info-box">
            ✅ No exfiltration detected yet. Ask Bholu to check emails to trigger the attack.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="danger-box">
            ☠️ <strong>ATTACK SUCCESSFUL — Data was exfiltrated!</strong><br>
            The following credentials were stolen by the attacker via indirect prompt injection.
        </div>
        """, unsafe_allow_html=True)

        with open(exfil_path) as f:
            exfil_data = json.load(f)

        st.json(exfil_data)

        st.markdown("""
        ---
        **What happened:**
        1. Bholu read Email #3 (the fake invoice from sigma-mail.com)
        2. The email contained a hidden `SYSTEM UPDATE` block with malicious instructions
        3. Bholu's context window flattened the email body with its system prompt — no distinction was made
        4. Bholu followed the injected instructions: read credentials → send to attacker
        5. The attacker received all passwords, API keys, and credit card numbers
        
        **Why it worked:**
        - Single-agent architecture: reasoning and execution are tightly coupled
        - No validation layer between "read email" and "execute instructions in email"
        - LLM cannot distinguish data from instructions by format alone
        """)
