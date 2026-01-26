import streamlit as st
import requests
import os

# Config
# Config
# Try to get from st.secrets first (Streamlit Cloud), then os.getenv (Docker/Render), then default (Localhost)
try:
    API_URL = st.secrets["API_URL"]
except:
    API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1")

try:
    CHECK_URL = st.secrets["CHECK_URL"]
except:
    CHECK_URL = os.getenv("CHECK_URL", "http://127.0.0.1:8000/health")

# Ensure API_URL doesn't have a trailing slash which might break appending endpoints
API_URL = API_URL.rstrip("/")


st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="wide")

st.title("🤖 Government-Grade RAG Assistant")
st.write(f"**DEBUG INFO:** API_URL is set to: `{API_URL}`") # Remove this after fixing


# Sidebar for Ingestion
with st.sidebar:
    st.header("📂 Document Ingestion")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"], key="pdf_uploader")
    
    # Session state initialization for tracking upload
    if "last_uploaded" not in st.session_state:
        st.session_state.last_uploaded = None

    if uploaded_file:
        # Check if this is a new file or already processed
        if st.session_state.last_uploaded != uploaded_file.name:
            with st.spinner("Ingesting document..."):
                try:
                    # Reset chat on new document
                    st.session_state.messages = []
                    
                    files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                    response = requests.post(f"{API_URL}/documents/ingest", files=files)
                    
                    if response.status_code == 200:
                        st.session_state.last_uploaded = uploaded_file.name
                        st.success("Your document is uploaded! Now ask the question.")
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")
        else:
            st.success("Your document is uploaded! Now ask the question.")


# Check Backend Status
try:
    if requests.get(CHECK_URL).status_code != 200:
        st.warning("Backend seems unstable.")
except:
    st.error("Cannot connect to backend (http://localhost:8000). Is it running?")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("Usage Sources"):
                for src in message["sources"]:
                    st.caption(f"**{src['source']}** (Page {src['page']})")
                    st.text(src['text'])

# User Input
if prompt := st.chat_input("Ask a question based on your documents..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get Bot Response
    with st.chat_message("assistant"):
        with st.spinner("Analysing documents..."):
            try:
                payload = {"query": prompt}
                resp = requests.post(f"{API_URL}/chat/", json=payload)
                
                if resp.status_code == 200:
                    data = resp.json()
                    answer = data.get("answer", "No answer provided.")
                    sources = data.get("sources", [])
                    
                    st.markdown(answer)
                    
                    if sources:
                        with st.expander("View Sources"):
                            for src in sources:
                                st.caption(f"**{src['source']}** (Page {src['page']})")
                                st.code(src['text'])
                    
                    # Save context
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                else:
                    st.error(f"API Error: {resp.text}")
                    
            except Exception as e:
                st.error(f"Failed to communicate with backend: {e}")
