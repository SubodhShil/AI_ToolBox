import streamlit as st
import sys
import os

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.groq_service import get_groq_service

# Page configuration
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize session state for message processing
if 'processing_done' not in st.session_state:
    st.session_state.processing_done = True

# Initialize Groq service
@st.cache_resource
def init_groq_service():
    try:
        return get_groq_service()
    except ValueError as e:
        st.error(f"Configuration Error: {str(e)}")
        return None

groq_service = init_groq_service()

# Modern CSS styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global styles */
.stApp {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}

/* Hide default Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main container */
.main-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
}

/* Header styling */
.chat-header {
    text-align: center;
    padding: 30px 20px;
    margin-bottom: 30px;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
}

.chat-header h1 {
    font-family: 'Inter', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

.chat-header p {
    font-family: 'Inter', sans-serif;
    color: #a0aec0;
    font-size: 1.1rem;
    margin: 0;
}

/* Chat container */
.chat-container {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    min-height: 400px;
    max-height: 500px;
    overflow-y: auto;
}

/* Message bubbles */
.message-wrapper {
    display: flex;
    margin-bottom: 20px;
    animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.message-wrapper.user {
    justify-content: flex-end;
}

.message-wrapper.assistant {
    justify-content: flex-start;
}

.message-bubble {
    max-width: 75%;
    padding: 15px 20px;
    border-radius: 20px;
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    line-height: 1.6;
    position: relative;
}

.message-bubble.user {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-bottom-right-radius: 5px;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.message-bubble.assistant {
    background: rgba(255, 255, 255, 0.08);
    color: #e2e8f0;
    border-bottom-left-radius: 5px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.message-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    margin: 0 10px;
    flex-shrink: 0;
}

.message-icon.user {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    order: 1;
}

.message-icon.assistant {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Input area styling */
.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 15px !important;
    color: white !important;
    padding: 15px 20px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
}

.stTextInput > div > div > input::placeholder {
    color: #718096 !important;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 30px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
}

/* Secondary button (Clear Chat) */
.clear-btn > button {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    box-shadow: none !important;
}

.clear-btn > button:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    box-shadow: none !important;
}

/* Model info badge */
.model-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(102, 126, 234, 0.1);
    border: 1px solid rgba(102, 126, 234, 0.3);
    border-radius: 20px;
    padding: 8px 16px;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: #a0aec0;
    margin-top: 15px;
}

.model-badge .dot {
    width: 8px;
    height: 8px;
    background: #48bb78;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #718096;
}

.empty-state .icon {
    font-size: 4rem;
    margin-bottom: 20px;
    opacity: 0.5;
}

.empty-state h3 {
    font-family: 'Inter', sans-serif;
    font-size: 1.3rem;
    color: #a0aec0;
    margin-bottom: 10px;
}

.empty-state p {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
}

/* Scrollbar styling */
.chat-container::-webkit-scrollbar {
    width: 6px;
}

.chat-container::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.3);
}

/* Typing indicator */
.typing-indicator {
    display: flex;
    gap: 4px;
    padding: 10px;
}

.typing-indicator span {
    width: 8px;
    height: 8px;
    background: #667eea;
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: rgba(26, 26, 46, 0.95) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

section[data-testid="stSidebar"] .stMarkdown {
    color: #a0aec0;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="chat-header">
    <h1>🤖 AI Chat Assistant</h1>
    <p>Powered by Groq • Lightning-fast AI responses</p>
    <div class="model-badge">
        <span class="dot"></span>
        <span>GPT OSS 120B • Online</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Function to call the chat API
def chat_with_ai(message):
    """Chat with AI using Groq API directly"""
    if groq_service is None:
        return "Error: Groq service not initialized. Please check your API key."
    
    # Convert chat history to the format expected by the service
    conversation_history = []
    for msg in st.session_state.chat_history:
        conversation_history.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    result = groq_service.chat(message, conversation_history)
    
    if "error" in result:
        return f"Error: {result['error']}"
    return result.get("response", "No response received")

# Chat messages container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

if not st.session_state.chat_history:
    # Empty state
    st.markdown("""
    <div class="empty-state">
        <div class="icon">💬</div>
        <h3>Start a conversation</h3>
        <p>Type a message below to begin chatting with the AI assistant</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Display chat messages
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="message-wrapper user">
                <div class="message-bubble user">{message['content']}</div>
                <div class="message-icon user">👤</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message-wrapper assistant">
                <div class="message-icon assistant">🤖</div>
                <div class="message-bubble assistant">{message['content']}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Input area
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        "Message",
        placeholder="Type your message here...",
        key="user_message",
        label_visibility="collapsed"
    )

with col2:
    send_clicked = st.button("Send 🚀", key="send_button", use_container_width=True)

# Action buttons row
col_clear, col_spacer = st.columns([1, 4])

with col_clear:
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat", key="clear_button"):
        st.session_state.chat_history = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Handle send button click
if send_clicked:
    if user_input and st.session_state.processing_done:
        st.session_state.processing_done = False
        
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Get AI response
        with st.spinner(""):
            ai_response = chat_with_ai(user_input)
        
        # Add AI response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        # Reset processing flag
        st.session_state.processing_done = True
        
        # Force a rerun to update the UI
        st.rerun()

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")
    
    st.markdown("**Current Model**")
    st.info("🧠 GPT OSS 120B")
    
    st.markdown("**Provider**")
    st.success("⚡ Groq (Ultra-fast inference)")
    
    st.markdown("---")
    st.markdown("### 📊 Chat Stats")
    st.metric("Messages", len(st.session_state.chat_history))
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; font-size: 0.8rem; padding: 20px 0;">
        Made with ❤️ by Subodh
    </div>
    """, unsafe_allow_html=True)