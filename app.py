import os, sqlite3
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pypdf import PdfReader

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(page_title="Bella Fashion | AI Concierge", page_icon="✨", layout="centered", initial_sidebar_state="collapsed")

def check_order_status(order_id: str) -> str:
    """Fetches real-time order status from SQL database using Order ID."""
    cid = order_id.strip().upper()
    if not cid.startswith("ORD-"): cid = f"ORD-{cid}"
    try:
        conn = sqlite3.connect("bella_store.db")
        row = conn.cursor().execute("SELECT * FROM orders WHERE order_id = ?", (cid,)).fetchone()
        conn.close()
        return f"Order {row[0]} ({row[2]}) for {row[1]}: Status is '{row[3]}'. {row[4]} via {row[5]}." if row else f"Order ID '{cid}' not found."
    except Exception as e:
        return f"DB Error: {e}"

def get_live_inventory() -> str:
    """Fetches products, prices, sizes, colors, and stock status from SQL database."""
    try:
        conn = sqlite3.connect("bella_store.db")
        rows = conn.cursor().execute("SELECT name, price, sizes, colors, stock_status FROM products").fetchall()
        conn.close()
        return "\n".join([f"- {r[0]}: Rs. {r[1]:,.0f} | Sizes: {r[2]} | Colors: {r[3]} | {r[4]}" for r in rows])
    except Exception as e:
        return f"Inventory Error: {e}"

st.markdown("""
<style>
    @import url('https://googleapis.com');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 14px; }
    #MainMenu, footer, header { visibility: hidden; background: transparent !important; }
    .block-container { padding-top: 1.2rem !important; max-width: 680px !important; }
    .stApp { background: radial-gradient(circle at 50% -10%, #1e1b4b 0%, #09090b 65%); color: #f8fafc; }
    .hero-card { background: rgba(255,255,255,0.04); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.09); border-radius: 16px; padding: 15px 20px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; }
    .hero-title { font-size: 1.15rem; font-weight: 700; background: linear-gradient(90deg, #fff, #c7d2fe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-sub { color: #94a3b8; font-size: 0.76rem; margin-top: 2px; }
    .badge { background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.3); color: #34d399; padding: 4px 11px; border-radius: 99px; font-size: 0.72rem; font-weight: 600; display: flex; align-items: center; gap: 6px; }
    .dot { width: 7px; height: 7px; background: #10b981; border-radius: 50%; box-shadow: 0 0 8px #10b981; }
    .stButton > button { background: rgba(255,255,255,0.04) !important; color: #e2e8f0 !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 11px !important; font-size: 0.76rem !important; min-height: 35px !important; }
    .stButton > button:hover { background: rgba(99,102,241,0.25) !important; border-color: #8b5cf6 !important; color: #fff !important; }
    [data-testid="stChatMessage"] { background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.06); border-radius: 15px; padding: 12px 16px; margin-bottom: 8px; }
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li { font-size: 0.87rem !important; line-height: 1.55 !important; color: #f1f5f9 !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("#### 🎛️ Store Admin")
    business_name = st.text_input("Brand Name", "Bella Fashion")
    tagline = st.text_input("Subtitle", "Personal Shopping & Support Concierge")
    contact_info = st.text_input("Support", "WhatsApp: 077-1234567")
    st.divider()
    try:
        conn = sqlite3.connect("bella_store.db")
        st.dataframe(pd.read_sql_query("SELECT order_id, status FROM orders", conn), hide_index=True, use_container_width=True)
        conn.close()
    except Exception: pass
    uploaded_file = st.file_uploader("Upload Policy (PDF/TXT)", type=["pdf", "txt"])
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

extra_docs = ""
if uploaded_file:
    extra_docs = "\n".join([p.extract_text() or "" for p in PdfReader(uploaded_file).pages]) if uploaded_file.name.endswith(".pdf") else uploaded_file.read().decode("utf-8")
elif os.path.exists("shop_data.txt"):
    extra_docs = open("shop_data.txt", "r", encoding="utf-8").read()

st.markdown(f'<div class="hero-card"><div><div class="hero-title">✨ {business_name}</div><div class="hero-sub">{tagline}</div></div><div class="badge"><div class="dot"></div>Online</div></div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": f"Welcome to **{business_name}**! ✨ Ask about our collection, check live stock, or share your **Order ID** to track a delivery."}]

c1, c2, c3 = st.columns(3)
q = None
if c1.button("🛍️ Explore Collection", use_container_width=True): q = "Show me your current products, prices, and stock availability."
if c2.button("📦 Track My Order", use_container_width=True): q = "I would like to track my order status."
if c3.button("🚚 Delivery & Returns", use_container_width=True): q = "What are your delivery charges and return policy?"

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="✨" if m["role"] == "assistant" else "👤"):
        st.markdown(m["content"])

prompt = q or st.chat_input("Ask a question or enter your Order ID...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"): st.markdown(prompt)
    history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:]])
    sys_msg = f"You are an elegant AI Concierge for '{business_name}'. Use `check_order_status(order_id)` if an Order ID is given (ask for Order ID if they want to track without giving one). Use `get_live_inventory()` for product/stock queries. Refer to Policies: {extra_docs}. Reply concisely in polite English using bullet points. Contact: {contact_info}.\nHistory:\n{history}"

    with st.chat_message("assistant", avatar="✨"):
        with st.spinner("Bella AI is typing..."):
            reply, err = None, ""
            for mod in ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-2.5-flash-lite"]:
                try:
                    res = client.models.generate_content(model=mod, contents=f"{sys_msg}\nCustomer: {prompt}", config=types.GenerateContentConfig(tools=[check_order_status, get_live_inventory], temperature=0.3))
                    reply = res.text
                    break
                except Exception as e: err = str(e)
            if reply:
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            else:
                st.error(f"Service temporarily busy. Please try again. ({err})")