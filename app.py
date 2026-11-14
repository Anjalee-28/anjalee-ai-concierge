import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API Key not found. Please check your .env configuration.")
    st.stop()

client = genai.Client(api_key=api_key)

# Page configuration
st.set_page_config(
    page_title="AI Concierge | Smart Support",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Sleek, Compact & Minimalist SaaS CSS
st.markdown("""
<style>
    @import url('https://googleapis.com');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 14px;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}

    /* Reduce top padding of main container */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 720px !important;
    }

    /* Sleek Midnight Background */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #171923 0%, #0b0c10 75%);
        color: #e2e8f0;
    }

    /* Compact Glassmorphic Header */
    .hero-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 14px 20px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .hero-title {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        color: #f8fafc !important;
        margin: 0 !important;
        letter-spacing: -0.01em;
    }

    .hero-subtitle {
        color: #94a3b8 !important;
        font-size: 0.78rem !important;
        margin: 2px 0 0 0 !important;
    }

    .status-badge {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34d399;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .pulse-dot {
        width: 6px;
        height: 6px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 6px #10b981;
    }

    /* Sleek Pill Buttons */
    .stButton > button {
        background: rgba(255, 255, 255, 0.04) !important;
        color: #cbd5e1 !important;
        border: 1px solid rgba(255, 255, 255, 0.09) !important;
        border-radius: 10px !important;
        padding: 6px 12px !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        min-height: 34px !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background: rgba(99, 102, 241, 0.2) !important;
        border-color: rgba(99, 102, 241, 0.5) !important;
        color: #ffffff !important;
    }

    /* Compact Chat Messages */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.025);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }

    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li {
        font-size: 0.88rem !important;
        line-height: 1.55 !important;
        color: #e2e8f0 !important;
    }

    /* Compact Chat Input */
    [data-testid="stChatInput"] textarea {
        font-size: 0.85rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for Admin / Client Controls
with st.sidebar:
    st.markdown("#### 🎛️ Admin Controls")
    st.caption("Customize AI agent & knowledge base")
    business_name = st.text_input("Brand Name", value="Pera Fashion Store")
    tagline = st.text_input("Subtitle", value="24/7 Smart Customer Support")
    contact_info = st.text_input("Fallback Contact", value="WhatsApp: 077-1234567")
    
    st.divider()
    st.markdown("#### 📂 Knowledge Base")
    uploaded_file = st.file_uploader("Upload Catalog / Policy (PDF, TXT)", type=["pdf", "txt"])
    
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Reset", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        chat_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.get("messages", [])])
        st.download_button("📥 Export", data=chat_str, file_name="transcript.txt", use_container_width=True)

# Load Knowledge Base
knowledge_base = ""
if uploaded_file is not None:
    if uploaded_file.name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            knowledge_base += page.extract_text() or ""
        st.sidebar.success(f"Loaded: {uploaded_file.name}")
    elif uploaded_file.name.endswith(".txt"):
        knowledge_base = uploaded_file.read().decode("utf-8")
        st.sidebar.success(f"Loaded: {uploaded_file.name}")
else:
    try:
        with open("shop_data.txt", "r", encoding="utf-8") as f:
            knowledge_base = f.read()
        st.sidebar.info("Active: Default Store Data")
    except FileNotFoundError:
        st.sidebar.warning("Upload a document in the sidebar.")

# Compact Glassmorphic Header
st.markdown(f"""
<div class="hero-card">
    <div>
        <div class="hero-title">✨ {business_name}</div>
        <div class="hero-subtitle">{tagline}</div>
    </div>
    <div class="status-badge">
        <div class="pulse-dot"></div>
        Online
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": f"Hello! Welcome to **{business_name}**. How can I help you today with our products, pricing, or delivery?"
        }
    ]

# Quick Action Pills
q1, q2, q3 = st.columns(3)
selected_prompt = None
if q1.button("🛍️ View Collection", use_container_width=True):
    selected_prompt = "Show me your available products and prices."
if q2.button("🚚 Delivery Info", use_container_width=True):
    selected_prompt = "How much is delivery and how long does it take?"
if q3.button("🔄 Return Policy", use_container_width=True):
    selected_prompt = "What is your return and exchange policy?"

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# Render Chat History
for message in st.session_state.messages:
    avatar = "✨" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Chat Input Handling
user_input = st.chat_input("Ask a question...")
final_prompt = selected_prompt if selected_prompt else user_input

if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(final_prompt)

    system_instruction = f"""
    You are a sophisticated, polite, and helpful AI concierge for '{business_name}'.
    Answer customer inquiries strictly using the provided Business Knowledge Base below.
    Always respond in clear, professional English, even if the customer writes in Singlish or another language.
    Format responses cleanly using concise bullet points and bold text for prices/items.
    If the answer is not in the knowledge base, politely apologize and provide our support contact: {contact_info}.
    
    Business Knowledge Base:
    {knowledge_base}
    """

    with st.chat_message("assistant", avatar="✨"):
        with st.spinner("Thinking..."):
            models_to_try = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-2.5-flash-lite"]
            reply = None
            last_error = ""

            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=f"{system_instruction}\n\nCustomer Question: {final_prompt}"
                    )
                    reply = response.text
                    break
                except Exception as e:
                    last_error = str(e)
                    continue

            if reply:
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            else:
                st.error(f"Service is temporarily busy. Please try again. ({last_error})")