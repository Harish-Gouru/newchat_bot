import streamlit as st
import ollama

# 1. Set up clean page structure
st.set_page_config(
    page_title="Simple ChatGPT Clone", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Initialize simple session state memory for active chat
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 3. Apply custom dark mode design specs and hover actions
st.markdown("""
<style>
    .stApp {
        background-color: #212121;
        color: #ececef;
        font-family: ui-sans-serif, system-ui, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: none;
    }
    .stTextInput input {
        background-color: #2f2f2f !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: 1px solid #424242 !important;
    }
    .landing-user-greeting {
        text-align: center;
        font-size: 38px;
        color: #ffffff;
        margin-top: 18vh;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    .landing-title {
        text-align: center;
        font-size: 32px;
        font-weight: 500;
        margin-top: 5px;
        margin-bottom: 30px;
        color: #88888d;
    }
    
    /* Interactive Hover Container for Chat Elements */
    .bubble-wrapper {
        position: relative;
        margin-bottom: 15px;
        clear: both;
    }
    .chat-bubble-user {
        background-color: #2f2f2f;
        padding: 12px 20px;
        border-radius: 20px;
        max-width: 75%;
        margin: 8px 0 2px auto;
        color: #ececec;
        text-align: left;
    }
    
    /* Hidden Action Menu Box by Default */
    .bubble-actions {
        display: none;
        text-align: right;
        margin-right: 15px;
        font-size: 12px;
    }
    .bubble-actions a {
        color: #88888d !important;
        text-decoration: none !important;
        margin-left: 12px;
        cursor: pointer;
    }
    .bubble-actions a:hover {
        color: #ffffff !important;
    }
    
    /* Reveal Option Triggers when cursor hovers on wrapper container */
    .bubble-wrapper:hover .bubble-actions {
        display: block;
    }

    .chat-bubble-ai {
        background-color: transparent;
        padding: 12px 0px;
        max-width: 100%;
        margin: 12px 0;
        color: #ececec;
    }
    
    /* Clean Chat Input box framing */
    div[data-testid="stChatInput"] {
        border-radius: 28px !important;
        background-color: transparent !important;
        border: 1px solid #424242 !important;
    }
    
    .sidebar-label {
        font-size: 11px;
        font-weight: bold;
        color: #666;
        margin-top: 15px;
        margin-bottom: 5px;
    }
    
    /* Subtle, low-profile secondary sidebar buttons */
    .sidebar-clear-btn button {
        background-color: transparent !important;
        color: #88888d !important;
        border: 1px solid #2d2d2d !important;
        font-size: 13px !important;
        border-radius: 6px !important;
        padding: 4px 10px !important;
    }
    .sidebar-clear-btn button:hover {
        color: #ffffff !important;
        border-color: #424242 !important;
        background-color: #2f2f2f !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR FRAMEWORK 
# ==========================================
with st.sidebar:
    if st.button("➕ New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    search_term = st.text_input("🔍 Search chats", placeholder="Search chats...", label_visibility="collapsed")
    
    # Minimal clear chat option container
    st.markdown('<div class="sidebar-clear-btn">', unsafe_allow_html=True)
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-label">CHATS</div>', unsafe_allow_html=True)
    
    for past_idx, past_chat in enumerate(st.session_state.chat_history):
        if not search_term or search_term.lower() in past_chat["title"].lower():
            if st.button(f"💬 {past_chat['title'][:22]}...", key=f"history_{past_idx}", use_container_width=True):
                st.session_state.messages = past_chat["messages"]
                st.rerun()

# ==========================================
# MAIN CHAT AREA DISPLAY TERMINAL
# ==========================================
if not st.session_state.messages:
    st.markdown("<div class='landing-user-greeting'>Hello User</div>", unsafe_allow_html=True)
    st.markdown("<div class='landing-title'> From where can we start today?</div>", unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="bubble-wrapper">
                <div class="chat-bubble-user">{msg["content"]}</div>
                <div class="bubble-actions">
                    <a>✏️ Edit</a>
                    <a>📋 Copy</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif msg["role"] == "assistant":
            st.markdown(f'<div class="chat-bubble-ai"><b>🤖 AI:</b><br><br>{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 100px;'></div>", unsafe_allow_html=True)

# ==========================================
# USER INPUT & CHAT RESPONSE LOGIC
# ==========================================
if user_input := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    if len(st.session_state.messages) == 1:
        st.session_state.chat_history.append({
            "title": user_input[:25],
            "messages": st.session_state.messages
        })
    st.rerun()

# Trigger response stream if user just sent a message
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        response_wrapper = st.empty()
        full_response = ""
        
        try:
            stream = ollama.chat(
                model="qwen2.5:3b",
                messages=st.session_state.messages,
                options={"temperature": 0.2},
                stream=True
            )
            for chunk in stream:
                full_response += chunk["message"]["content"]
                response_wrapper.markdown(full_response + "▌")
            response_wrapper.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.rerun()
            
        except Exception as e:
            st.error(f"Local Service Connection Error: {e}")