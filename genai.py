import streamlit as st
from openai import OpenAI
import httpx


import os

# OpenAI API Key - Replace with your actual API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


# Page configuration
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide"
)


# Custom CSS for ChatGPT-like styling with improved text visibility
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background-color: #f7f7f8;
    }
   
    .main-header {
        text-align: center;
        color: #1a1a2e;
        padding: 20px;
        font-size: 2rem;
        font-weight: 600;
    }
   
    /* All text elements */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown h1,
    .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #1a1a2e !important;
    }
   
    /* Chat messages */
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 12px;
        margin-bottom: 1rem;
        padding: 1rem;
    }
   
    [data-testid="stChatMessage"] p {
        color: #1a1a2e !important;
        font-size: 1rem;
        line-height: 1.7;
    }
   
    /* Text inputs */
    .stTextInput > div > div > input {
        background-color: #ffffff;
        color: #1a1a2e;
        border: 2px solid #10A37F;
        border-radius: 0.75rem;
        padding: 12px 16px;
        font-size: 1rem;
    }
   
    .stTextInput > div > div > input::placeholder {
        color: #6b7280;
    }
   
    /* Chat input */
    [data-testid="stChatInput"] textarea {
        background-color: #ffffff !important;
        color: #1a1a2e !important;
        border: 2px solid #10A37F !important;
        border-radius: 0.75rem;
        font-size: 1rem;
    }
   
    /* Buttons */
    .stButton > button {
        background-color: #10A37F;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
   
    .stButton > button:hover {
        background-color: #0d8a6a;
    }
   
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1a2e;
    }
   
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #ffffff !important;
    }
   
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
   
    [data-testid="stSidebar"] .stTextInput > div > div > input {
        background-color: #2d2d44;
        color: #ffffff;
        border: 1px solid #4a4a6a;
    }
   
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #2d2d44;
        color: #ffffff;
    }
   
    /* Slider */
    [data-testid="stSidebar"] .stSlider label {
        color: #ffffff !important;
    }
   
    /* Info boxes */
    .stAlert {
        background-color: #e8f4f0;
        color: #1a1a2e;
        border: 1px solid #10A37F;
    }
   
    /* Links */
    a {
        color: #10A37F !important;
    }
   
    /* Spinner text */
    .stSpinner > div {
        color: #1a1a2e;
    }
</style>
""", unsafe_allow_html=True)


# Sidebar for settings
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")
   
    # Model selection
    model_option = st.selectbox(
        "🧠 Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        index=0,
        help="Select the GPT model to use"
    )

    # Temperature slider
    temperature = st.slider(
        "🌡️ Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Higher values make output more random, lower values more deterministic"
    )

    st.markdown("---")

    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []


# Main header
st.markdown('<h1 class="main-header">🤖 AI Chat Assistant</h1>', unsafe_allow_html=True)


# Configure OpenAI
try:
    # Initialize the client with timeout settings
    http_client = httpx.Client(timeout=60.0)
    client = OpenAI(api_key=OPENAI_API_KEY, http_client=http_client)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Send a message..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                try:
                    # Build messages for OpenAI API
                    messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
                    for msg in st.session_state.messages:
                        messages.append({"role": msg["role"], "content": msg["content"]})
                    
                    # Generate response
                    response = client.chat.completions.create(
                        model=model_option,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=4096
                    )
                    
                    assistant_response = response.choices[0].message.content
                    
                    # Display response
                    st.markdown(assistant_response)
                    
                    # Add assistant response to messages
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_response
                    })
                    
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "rate" in error_msg.lower():
                        st.warning("⏳ Rate limit exceeded. Please wait a moment and try again.")
                        with st.expander("Error Details"):
                            st.code(error_msg)
                    elif "401" in error_msg or "invalid" in error_msg.lower():
                        st.error("🔑 Invalid API key. Please check your OpenAI API key.")
                    elif "connection" in error_msg.lower() or "connect" in error_msg.lower():
                        st.error("🌐 Connection error. Please check your internet connection or try disabling VPN/proxy.")
                    else:
                        st.error(f"Error generating response: {error_msg}")
                       
except Exception as e:
    st.error(f"Error configuring OpenAI API: {str(e)}")
    st.info("Please check your API key and try again.")


# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #8E8EA0; font-size: 0.8rem;'>"
    "Powered by OpenAI GPT • Built with Streamlit"
    "</p>",
    unsafe_allow_html=True
)
