import streamlit as st
from datetime import datetime
import re

from tools import calculate, get_current_datetime
from agent_engine import AgentEngine
from agent_runner import AgentRunner
from task_storage import load_tasks, save_task, migrate_session_tasks
from memory import (
    load_memories,
    save_memory,
    get_memory,
    detect_memory_request,
)

st.set_page_config(
    page_title="AURA | Personal AI Agent",
    page_icon="🟠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- AURA AGENT ENGINE --------------------
aura_engine = AgentEngine([calculate, get_current_datetime])
aura_runner = AgentRunner(aura_engine)


def execute_supported_task(goal: str) -> dict:
    """Run a supported local tool task; do not claim unsupported work succeeded."""
    text = goal.strip()
    lowered = text.casefold()

    # Date/time requests are routed only to the registered date-time tool.
    if any(phrase in lowered for phrase in (
        "current date", "current time", "date and time", "what time is it",
        "today's date", "todays date", "what is the date",
    )):
        return aura_runner.run_tool_task(
            goal=text,
            tool_name="get_current_datetime",
            arguments={},
        )

    # Accept common arithmetic wording and Unicode math symbols.
    match = re.search(
        r"\b(?:calculate|compute|what is|what's)\s+(.+?)"
        r"(?:\s+and\s+(?:verify|check|show|explain)\b.*)?[?.!]*$",
        text,
        re.IGNORECASE,
    )
    if match:
        expression = match.group(1).strip().rstrip("?.!")
        expression = (expression.replace("×", "*")
                                .replace("÷", "/")
                                .replace("−", "-")
                                .replace("–", "-"))
        if re.fullmatch(r"[0-9\s()+\-*/%.*]+", expression):
            return aura_runner.run_tool_task(
                goal=text,
                tool_name="calculate",
                arguments={"expression": expression},
            )

    return {
        "goal": text,
        "complete": False,
        "failed": True,
        "message": (
            "AURA currently supports arithmetic and current date/time tasks. "
            "Examples: 'Calculate 250 × 48 and verify the result' or "
            "'What is the current date and time?'"
        ),
        "steps": [],
    }


# -------------------- THEME --------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --orange: #F97316;
        --orange-hover: #EA580C;
        --orange-soft: #FFF1E7;
        --orange-border: #FED7AA;
        --page: #F7F8FA;
        --surface: #FFFFFF;
        --text: #182230;
        --muted: #697586;
        --border: #E7EAF0;
        --green: #15803D;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: var(--text);
    }

    .stApp {
        background: var(--page);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: rgba(247, 248, 250, 0.92);
    }

    [data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.2rem;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--muted);
    }

    h1, h2, h3 {
        font-family: 'Manrope', sans-serif !important;
        color: var(--text);
        letter-spacing: -0.035em;
    }

    h1 { font-weight: 800 !important; }
    h2, h3 { font-weight: 700 !important; }

    .brand-row {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 2px 18px 2px;
    }

    .brand-mark {
        width: 44px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 14px;
        background: linear-gradient(145deg, #FB923C, #EA580C);
        color: white;
        font-size: 23px;
        font-weight: 800;
        box-shadow: 0 7px 18px rgba(249, 115, 22, 0.22);
    }

    .brand-name {
        font-family: 'Manrope', sans-serif;
        font-weight: 800;
        font-size: 24px;
        color: #182230;
        line-height: 1.1;
        letter-spacing: -0.04em;
    }

    .brand-subtitle {
        color: #8792A2;
        font-size: 10px;
        letter-spacing: 0.16em;
        font-weight: 700;
        margin-top: 4px;
    }

    .eyebrow {
        color: var(--orange-hover);
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 32px 34px;
        border: 1px solid #F6D7C2;
        border-radius: 24px;
        background: linear-gradient(115deg, #FFFFFF 0%, #FFF8F2 65%, #FFEDD9 100%);
        margin: 4px 0 24px 0;
        box-shadow: 0 8px 26px rgba(24, 34, 48, 0.035);
    }

    .hero:after {
        content: "";
        position: absolute;
        width: 230px;
        height: 230px;
        border-radius: 50%;
        right: -75px;
        top: -100px;
        border: 35px solid rgba(249, 115, 22, 0.07);
        pointer-events: none;
    }

    .hero h1 {
        font-size: clamp(30px, 3.3vw, 43px);
        margin: 0 0 10px 0;
        line-height: 1.12;
    }

    .hero p {
        max-width: 650px;
        color: #687385;
        font-size: 15px;
        line-height: 1.7;
        margin: 0 0 18px 0;
    }

    .hero-status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #FFFFFF;
        color: #9A4A12;
        border: 1px solid #F7D2B5;
        border-radius: 999px;
        padding: 7px 12px;
        font-size: 12px;
        font-weight: 700;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        display: inline-block;
        background: #F97316;
        border-radius: 50%;
    }

    .metric-card {
        min-height: 124px;
        padding: 20px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        box-shadow: 0 3px 12px rgba(24, 34, 48, 0.025);
    }

    .metric-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
    }

    .metric-label {
        color: var(--muted);
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.025em;
    }

    .metric-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 34px;
        background: var(--orange-soft);
        color: var(--orange-hover);
        border-radius: 11px;
        font-size: 16px;
    }

    .metric-value {
        font-family: 'Manrope', sans-serif;
        font-size: 25px;
        font-weight: 800;
        color: var(--text);
        margin-top: 13px;
        line-height: 1.2;
    }

    .metric-note {
        font-size: 11px;
        color: #8792A2;
        margin-top: 6px;
    }

    .section-heading {
        margin: 30px 0 14px 0;
    }

    .section-heading h3 {
        font-size: 20px;
        margin: 0 0 4px 0;
    }

    .section-heading p {
        color: var(--muted);
        font-size: 13px;
        margin: 0;
    }

    .capability-card {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 20px;
        min-height: 165px;
        box-shadow: 0 3px 12px rgba(24, 34, 48, 0.02);
    }

    .capability-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 42px;
        height: 42px;
        background: var(--orange-soft);
        color: var(--orange-hover);
        border-radius: 13px;
        font-size: 20px;
        margin-bottom: 13px;
    }

    .capability-title {
        font-weight: 800;
        font-size: 15px;
        margin-bottom: 7px;
        color: var(--text);
    }

    .capability-copy {
        font-size: 12px;
        color: var(--muted);
        line-height: 1.65;
    }

    .panel {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 3px 12px rgba(24, 34, 48, 0.02);
    }

    .panel-title {
        font-size: 15px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .panel-subtitle {
        color: var(--muted);
        font-size: 12px;
        line-height: 1.6;
    }

    .small-pill {
        display: inline-block;
        border-radius: 999px;
        padding: 5px 9px;
        background: #FFF1E7;
        color: #C2410C;
        font-size: 11px;
        font-weight: 700;
    }

    .stButton > button, .stFormSubmitButton > button {
        border-radius: 11px;
        min-height: 42px;
        font-weight: 700;
        border: 1px solid var(--orange);
        background: var(--orange);
        color: #FFFFFF;
        transition: all 0.18s ease;
    }

    .stButton > button:hover, .stFormSubmitButton > button:hover {
        border-color: var(--orange-hover);
        background: var(--orange-hover);
        color: #FFFFFF;
        box-shadow: 0 5px 14px rgba(249, 115, 22, 0.18);
    }

    .stButton > button:focus, .stFormSubmitButton > button:focus {
        box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.2);
    }

    [data-testid="stChatMessage"] {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 14px;
        box-shadow: 0 2px 8px rgba(24, 34, 48, 0.02);
    }

    [data-testid="stChatInput"] {
        border-color: #E7EAF0;
        background: #FFFFFF;
        border-radius: 14px;
    }

    input, textarea, [data-baseweb="select"] > div {
        border-radius: 10px !important;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        background: #FFFFFF;
        color: var(--text);
        border-color: var(--border);
    }

    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 16px;
    }

    [data-testid="stExpander"] {
        border: 1px solid var(--border);
        border-radius: 13px;
        background: #FFFFFF;
    }

    [data-testid="stProgressBar"] > div > div > div {
        background: var(--orange);
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    hr {
        border-color: var(--border);
    }

    .footer {
        color: #8792A2;
        font-size: 11px;
        text-align: center;
        padding: 10px 0 0 0;
    }

    @media (max-width: 700px) {
        .hero { padding: 24px; }
        .metric-card { padding: 15px; }
        .metric-value { font-size: 22px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- SESSION STATE --------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi! I'm AURA. I can help you work through goals, "
                "ideas, and tasks. My live AI engine is not connected yet."
            ),
        }
    ]

if "task_history" not in st.session_state:
    st.session_state.task_history = load_tasks()

if "tasks_run" not in st.session_state:
    st.session_state.tasks_run = 0

if "navigation_target" not in st.session_state:
    st.session_state.navigation_target = "Dashboard"

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand-row">
            <div class="brand-mark">A</div>
            <div>
                <div class="brand-name">AURA</div>
                <div class="brand-subtitle">PERSONAL AI AGENT</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown("**WORKSPACE**")
    page = st.radio(
        "Navigate",
        [
            "Dashboard",
            "AI Chat",
            "Task Center",
            "Execution Logs",
            "Memory Center",
            "System Status",
        ],
        label_visibility="collapsed",
        key="sidebar_page",
    )
    if st.session_state.navigation_target != "Dashboard" and page == "Dashboard":
        page = st.session_state.navigation_target
        st.session_state.navigation_target = "Dashboard"

    st.divider()
    st.markdown("**BUILD STATUS**")
    st.markdown(
        '<span class="small-pill">Prototype · v1</span>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.caption("Python foundation")
    st.progress(0.25)
    st.caption("AI integration pending")

# -------------------- DASHBOARD --------------------
if page == "Dashboard":
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">YOUR PERSONAL AI WORKSPACE</div>
            <h1>Meet your intelligence layer.</h1>
            <p>
                Plan your next move, organize tasks, and bring your tools
                together in one calm, focused workspace.
            </p>
            <span class="hero-status">
                <span class="status-dot"></span>
                Interface online · AI connection not yet verified
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metrics = st.columns(4)
    metric_data = [
        ("TASKS CREATED", str(st.session_state.tasks_run), "▤", "Recorded in this session"),
        ("CHAT MESSAGES", str(len(st.session_state.messages)), "◌", "Conversation history"),
        ("REGISTERED TOOLS", "2", "⌘", "Calculator and date/time"),
        ("AI CONNECTION", "Pending", "✳", "Not yet verified"),
    ]
    for col, (label, value, icon, note) in zip(metrics, metric_data):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-top">
                        <div class="metric-label">{label}</div>
                        <div class="metric-icon">{icon}</div>
                    </div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-note">{note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="section-heading">
            <h3>Inside AURA</h3>
            <p>The core building blocks of your agent.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    capabilities = st.columns(3)
    capability_data = [
        ("✳", "AI reasoning", "Interpret requests and choose actions. Live model connection is still pending."),
        ("⌘", "Tool execution", "A Python tool foundation exists; interface integration is the next step."),
        ("▣", "Persistent memory", "A memory module exists; management controls are not connected yet."),
    ]
    for col, (icon, title, description) in zip(capabilities, capability_data):
        with col:
            st.markdown(
                f"""
                <div class="capability-card">
                    <div class="capability-icon">{icon}</div>
                    <div class="capability-title">{title}</div>
                    <div class="capability-copy">{description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="section-heading">
            <h3>Quick start</h3>
            <p>Choose where you want to continue.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    quick1, quick2 = st.columns(2)
    with quick1:
        with st.container(border=True):
            st.markdown("**💬 Start a conversation**")
            st.caption("Write down an idea or the task you want to solve.")
            if st.button("Go to AI Chat →", key="quick_chat", use_container_width=True):
                st.session_state["navigation_target"] = "AI Chat"
                st.rerun()
    with quick2:
        with st.container(border=True):
            st.markdown("**📋 Organize a task**")
            st.caption("Record a goal and track its current development status.")
            if st.button("Open Task Center →", key="quick_tasks", use_container_width=True):
                st.session_state["navigation_target"] = "Task Center"
                st.rerun()

# -------------------- AI CHAT --------------------
elif page == "AI Chat":
    st.markdown('<div class="eyebrow">AURA WORKSPACE</div>', unsafe_allow_html=True)
    st.title("AI Chat")
    st.caption("A focused place to work through your ideas with AURA.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Message AURA…")

    if prompt:
        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        memory_request = detect_memory_request(prompt)

        if memory_request:
            key, value = memory_request
            response_text = save_memory(key, value)
        else:
            response_text = (
                "Your message has been captured in this session. "
                "The live AI reasoning engine is not connected yet, so I haven't "
                "processed this request with a language model."
            )

        with st.chat_message("assistant"):
            if memory_request:
                st.success(response_text)
            else:
                st.info(response_text)

        st.session_state.messages.append(
            {"role": "assistant", "content": response_text}
        )
# -------------------- TASK CENTER --------------------
elif page == "Task Center":
    st.markdown('<div class="eyebrow">PLAN & ORGANIZE</div>', unsafe_allow_html=True)
    st.title("Task Center")
    st.caption("Run supported tasks through AURA's local tool engine and inspect the execution report.")

    with st.container(border=True):
        with st.form("task_form", clear_on_submit=True):
            goal = st.text_area(
                "What do you want AURA to accomplish?",
                placeholder="Example: Calculate 250 × 48 and verify the result.",
                height=110,
            )
            submitted = st.form_submit_button("▶  Run task", use_container_width=True)

    if submitted:
        if not goal.strip():
            st.error("Enter a goal before running a task.")
        else:
            with st.spinner("AURA is processing your task..."):
                report = execute_supported_task(goal)

            task = {
                "goal": goal.strip(),
                "status": "Completed" if report["complete"] else "Failed",
                "created": datetime.now().strftime("%d %b %Y · %I:%M %p"),
                "report": report,
            }
            st.session_state.task_history.append(task)
            save_task(task)  # Save the task permanently to JSON
            st.session_state.tasks_run += 1

            if report["complete"]:
                st.success("Task completed!")
                result = report["steps"][2]["result"]
                st.metric("Execution result", result)
            else:
                st.error("AURA could not complete this task.")
                st.warning(report.get("message", "Review the execution report below."))

            with st.expander("Execution details", expanded=True):
                for index, step in enumerate(report.get("steps", []), start=1):
                    st.markdown(f"**Step {index}: {step['description']}**")
                    st.caption(f"Status: {step['status']}")
                    if step.get("result") is not None:
                        st.write(step["result"])

    st.markdown("### Your tasks")
    if st.session_state.task_history:
        for index, task in enumerate(reversed(st.session_state.task_history), start=1):
            with st.expander(f"{index:02d} · {task['goal']}"):
                st.markdown(f"**Status:** {task['status']}")
                st.caption(f"Created {task['created']}")
                report = task.get("report", {})
                if report.get("message"):
                    st.warning(report["message"])
                for step in report.get("steps", []):
                    st.write(f"**{step['status'].upper()}** — {step['description']}")
                    if step.get("result") is not None:
                        st.caption(str(step["result"]))
    else:
        with st.container(border=True):
            st.caption("Your task list is empty. Run a supported task above to get started.")

# -------------------- EXECUTION LOGS --------------------
elif page == "Execution Logs":
    st.markdown(
        '<div class="eyebrow">OBSERVABILITY</div>',
        unsafe_allow_html=True,
    )
    st.title("Execution Logs")
    st.caption(
        "Inspect AURA's recorded tasks, execution steps, results, and failures."
    )

    if not st.session_state.task_history:
        with st.container(border=True):
            st.info("No execution events yet. Run a task in Task Center.")
    else:
        for index, task in enumerate(
            reversed(st.session_state.task_history), start=1
        ):
            report = task.get("report", {})

            with st.expander(
                f"{index:02d} · {task['goal']} · {task['status']}",
                expanded=(index == 1),
            ):
                st.caption(f"Recorded: {task['created']}")
                st.markdown(f"**Status:** {task['status']}")

                if report.get("message"):
                    st.warning(report["message"])

                steps = report.get("steps", [])

                if steps:
                    st.markdown("#### Execution steps")

                    for step_number, step in enumerate(steps, start=1):
                        status = step.get("status", "unknown").upper()
                        description = step.get("description", "Unnamed step")

                        st.markdown(f"**{step_number}. {description}**")
                        st.caption(f"Status: {status}")

                        result = step.get("result")
                        if result is not None:
                            st.code(str(result))

                else:
                    st.caption(
                        "No detailed execution report was recorded for this task."
                    )


# -------------------- MEMORY CENTER --------------------
elif page == "Memory Center":
    st.markdown(
        '<div class="eyebrow">PERSONAL CONTEXT</div>',
        unsafe_allow_html=True,
    )
    st.title("Memory Center")
    st.caption(
        "Save, retrieve, and review facts that AURA can remember across sessions."
    )

    memories = load_memories()

    # Save a memory
    with st.container(border=True):
        st.markdown("### Save a memory")
        with st.form("save_memory_form", clear_on_submit=True):
            memory_key = st.text_input(
                "Memory name",
                placeholder="e.g. My project",
            )
            memory_value = st.text_area(
                "Information to remember",
                placeholder="e.g. AURA AI Agent",
                height=90,
            )
            save_clicked = st.form_submit_button(
                "Save memory",
                use_container_width=True,
            )

        if save_clicked:
            if not memory_key.strip() or not memory_value.strip():
                st.error("Enter both a memory name and its information.")
            else:
                result = save_memory(
                    memory_key.strip(),
                    memory_value.strip(),
                )
                st.success(result)
                st.rerun()

    # Search and retrieve a memory
    with st.container(border=True):
        st.markdown("### Retrieve a memory")

        if memories:
            selected_key = st.selectbox(
                "Choose a saved memory",
                options=sorted(memories.keys()),
                key="memory_lookup_key",
            )

            if st.button("Retrieve memory", use_container_width=True):
                value = get_memory(selected_key)
                st.markdown(f"**{selected_key}**")
                st.info(value)
        else:
            st.caption("No memories saved yet.")

    # Display all persistent memories
    st.markdown("### Stored memories")

    memories = load_memories()

    if memories:
        st.caption(f"{len(memories)} saved memor{'y' if len(memories) == 1 else 'ies'}")

        for key, value in sorted(memories.items()):
            with st.expander(key):
                st.write(value)
    else:
        with st.container(border=True):
            st.info(
                "Your memory store is empty. Save your first memory above."
            )


# -------------------- SYSTEM STATUS --------------------
elif page == "System Status":
    st.markdown('<div class="eyebrow">HEALTH & CAPABILITIES</div>', unsafe_allow_html=True)
    st.title("System Status")
    st.caption("Development component overview. These are not live health checks.")

    components = [
        ("Streamlit interface", "Available", "success"),
        ("Python environment", "Available", "success"),
        ("Calculator / date-time tools", "Implemented", "success"),
        ("Task planner", "Implemented", "success"),
        ("Agent engine / runner", "Connected to Task Center", "success"),
        ("Persistent memory UI", "Integration pending", "pending"),
        ("Gemini connection", "Not verified", "pending"),
        ("Autonomous multi-step execution", "Not implemented", "pending"),
    ]

    with st.container(border=True):
        for name, status, kind in components:
            left, right = st.columns([2, 3])
            with left:
                st.markdown(f"**{name}**")
            with right:
                if kind == "success":
                    st.markdown(f'<span style="color:#15803D;font-weight:700">● {status}</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span style="color:#B45309;font-weight:700">● {status}</span>', unsafe_allow_html=True)
            st.divider()

# -------------------- FOOTER --------------------
st.markdown(
    """
    <div class="footer">
        AURA · Personal AI Agent &nbsp; · &nbsp; Orange / White Edition
        <br>Interface prototype — agent capabilities are being connected progressively.
    </div>
    """,
    unsafe_allow_html=True,
)
