import streamlit as st
from llama_index.core import VectorStoreIndex
from llama_index.readers.notion import NotionPageReader
from dotenv import load_dotenv
import os
import logging
import sys
import torch
import util
from Chroma import ChromaHandler

torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)] 

# Setup logging and environment
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
load_dotenv()

# Page config
st.set_page_config(page_title="Notion Q&A Chat", layout="wide")
st.title("💬 Chat with Notion Data")

# Load API key
integration_token = os.getenv("NOTION_API_KEY")

# Initialize Chroma
@st.cache_resource
def get_chroma_index():
    st.info("🔄 Initializing Chroma and loading Notion data...")
    
    # Setup vector DB
    chroma_db = ChromaHandler('rocky')

    # Load documents from Notion
    reader = NotionPageReader(integration_token=integration_token)
    
    # Hardcoded for now, or you can use a Streamlit input
    # add all pages
    page_ids = util.extract_notion_ids()[:3]
    documents = reader.load_data(page_ids=page_ids)
    logging.info(f"Loaded {len(documents)} documents")
    # Create index
    index = VectorStoreIndex(documents, storage_context=chroma_db.storage_context)
    return index

index = get_chroma_index()
query_engine = index.as_query_engine()

# Chat History
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

# Get user input
user_input = st.chat_input("Ask a question:")

if user_input:
    # Show user message
    st.chat_message("user").markdown(user_input)

    # Get the answer
    with st.spinner("Thinking..."):
        response = query_engine.query(user_input)
        answer = response.response

        # Show bot answer
        st.chat_message("assistant").markdown(answer)

        # Add user and bot messages to session state for history
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": answer})

