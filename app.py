import re
import streamlit as st
from retrieval import retrieve
from llm import answer, answer_stream

st.set_page_config(page_title="Startup Advisor", page_icon="💬", layout="centered")

# Topic shortcuts: (label, icon, accent color, starter prompt)
TOPICS = [
    ("Fundraising", "💰", "#f97316", "How should I approach fundraising for my startup?"),
    ("Growth", "📈", "#a855f7", "What are the best growth strategies for an early-stage startup?"),
    ("Hiring", "🧑‍💼", "#22c55e", "How do I hire my first key employees?"),
    ("PMF", "🎯", "#3b82f6", "How do I find product-market fit?"),
    ("Pitch deck", "📊", "#ec4899", "What should my pitch deck include?"),
]

# Quick-topic chips: label -> prompt
CHIPS = {
    "Pricing & Ownership": "How should I think about pricing and equity ownership?",
    "Technical Foundation": "What technical foundations should an early startup get right?",
    "Compare Advisors": "What are the different schools of thought among startup advisors?",
    "Key Features": "How do I decide which features to build first?",
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #ffffff !important;
    color: #111111;
    font-family: 'Inter', sans-serif;
}
[data-testid="stBottom"], [data-testid="stBottom"] > div {
    background-color: #ffffff !important;
}
[data-testid="stMainBlockContainer"] {
    padding-top: 3rem;
    max-width: 720px;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }

/* ── Headline ── */
.headline {
    text-align: center;
    font-size: 32px;
    font-weight: 600;
    color: #111111;
    margin: 3rem 0 2rem;
    letter-spacing: -0.5px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
}
.headline-logo {
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, #f97316, #ec4899);
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
}

/* ── Input card ── */
.st-key-input_card {
    background: #f5f5f5;
    border: 1px solid #e0e0e0;
    border-radius: 14px;
    padding: 6px 14px 10px;
    margin-bottom: 1.25rem;
}
/* text input inside the card */
.st-key-input_card [data-testid="stTextInput"] > div,
.st-key-input_card [data-baseweb="input"],
.st-key-input_card [data-baseweb="base-input"] {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.st-key-input_card [data-testid="stTextInput"] input {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    color: #111111 !important;
    font-size: 1.05rem !important;
    box-shadow: none !important;
    padding: 8px 4px !important;
    -webkit-text-fill-color: #111111 !important;
    caret-color: #111111 !important;
}
.st-key-input_card [data-testid="stTextInput"] input::placeholder {
    color: #999 !important;
    -webkit-text-fill-color: #999 !important;
}

/* circular icon buttons */
.st-key-input_card [data-testid="stButton"] button {
    border-radius: 50% !important;
    width: 34px !important;
    height: 34px !important;
    min-height: 34px !important;
    padding: 0 !important;
    border: none !important;
    font-size: 0.95rem !important;
    line-height: 1 !important;
    display: flex !important;
    align-items: center;
    justify-content: center;
    transition: transform 0.12s, filter 0.12s;
}
.st-key-input_card [data-testid="stButton"] button:hover {
    transform: scale(1.12);
    filter: brightness(1.1);
}
.st-key-topic_0 button { background: #f97316 !important; }
.st-key-topic_1 button { background: #a855f7 !important; }
.st-key-topic_2 button { background: #22c55e !important; }
.st-key-topic_3 button { background: #3b82f6 !important; }
.st-key-topic_4 button { background: #ec4899 !important; }

/* send button — far right */
.st-key-send_btn button {
    background: #e0e0e0 !important;
    color: #111111 !important;
}
.st-key-send_btn button:hover {
    background: #f97316 !important;
    color: #fff !important;
}

/* ── Chip buttons ── */
.st-key-chip_row [data-testid="stButton"] button {
    background: #ffffff !important;
    border: 1px solid #e0e0e0 !important;
    color: #333333 !important;
    border-radius: 999px !important;
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    padding: 6px 14px !important;
    transition: background 0.15s, border-color 0.15s;
}
.st-key-chip_row [data-testid="stButton"] button:hover {
    background: #f5f5f5 !important;
    border-color: #bbb !important;
    color: #111 !important;
}

/* ── Footer ── */
.footer-note {
    text-align: center;
    color: #999999;
    font-size: 0.75rem;
    margin-top: 1.5rem;
}

/* ── Chat view ── */
[data-testid="stChatMessage"] {
    background: #f5f5f5 !important;
    border-radius: 12px !important;
    margin-bottom: 0.5rem;
}
[data-testid="stChatInput"] {
    background: #f5f5f5 !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #111111 !important;
    caret-color: #111111 !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #999 !important; }
[data-testid="stChatInput"] button { background: #e0e0e0 !important; }
[data-testid="stChatInput"] button:hover { background: #f97316 !important; }

/* sources */
.source-card {
    background: #fafafa;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 6px;
}
.source-name { font-size: 0.8rem; font-weight: 600; color: #111111; margin-bottom: 4px; }
.source-text { font-size: 0.75rem; color: #666666; line-height: 1.5; }
[data-testid="stExpander"] {
    background: transparent !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


def display_name(filename):
    name = filename.removesuffix(".txt")
    name = re.sub(r"^[a-z0-9]+_com_(.+?)(?:_html)?$", r"\1", name)
    return name.replace("_", " ").title()


def render_sources(chunks):
    if not chunks:
        return
    with st.expander("Sources", expanded=False):
        html = ""
        for chunk in chunks:
            name = display_name(chunk["source"])
            snippet = chunk["text"][:200].strip() + "…"
            html += f'<div class="source-card"><div class="source-name">{name}</div><div class="source-text">{snippet}</div></div>'
        st.markdown(html, unsafe_allow_html=True)


def submit(text):
    if text and text.strip():
        st.session_state.pending = text.strip()


def _submit_from_input():
    submit(st.session_state.get("landing_text", ""))


if "messages" not in st.session_state:
    st.session_state.messages = []

pending = st.session_state.pop("pending", None)
show_landing = not st.session_state.messages and not pending

if show_landing:
    # ── Landing / welcome screen ──
    st.markdown('<div class="headline"><span class="headline-logo">🚀</span>What can I help with?</div>', unsafe_allow_html=True)

    with st.container(key="input_card"):
        st.text_input(
            "question", key="landing_text", label_visibility="collapsed",
            placeholder="Ask anything about your startup…", on_change=_submit_from_input,
        )
        cols = st.columns([1, 1, 1, 1, 1, 4, 1], vertical_alignment="center")
        for i, (label, icon, color, prompt) in enumerate(TOPICS):
            with cols[i]:
                if st.button(icon, key=f"topic_{i}", help=label):
                    submit(prompt)
                    st.rerun()
        with cols[-1]:
            if st.button("↑", key="send_btn", help="Send"):
                submit(st.session_state.get("landing_text", ""))
                st.rerun()

    with st.container(key="chip_row"):
        chip_cols = st.columns(len(CHIPS))
        for col, (label, prompt) in zip(chip_cols, CHIPS.items()):
            with col:
                if st.button(label, key=f"chip_{label}"):
                    submit(prompt)
                    st.rerun()

    st.markdown('<div class="footer-note">Startup Advisor may make mistakes.</div>', unsafe_allow_html=True)

else:
    # ── Chat view ──
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                render_sources(msg["sources"])

    if pending:
        st.session_state.messages.append({"role": "user", "content": pending})
        with st.chat_message("user"):
            st.write(pending)
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                chunks = retrieve(pending, k=4)
            history = st.session_state.messages[:-1][-6:]
            response = st.write_stream(answer_stream(pending, chunks, history))
            render_sources(chunks)
        st.session_state.messages.append({
            "role": "assistant", "content": response, "sources": chunks,
        })

    if follow_up := st.chat_input("Ask a follow-up…"):
        submit(follow_up)
        st.rerun()

    st.markdown('<div class="footer-note">Startup Advisor may make mistakes.</div>', unsafe_allow_html=True)
