import streamlit as st
import time
from llm.response_generator import ResponseGenerator

# --- PAGE CONFIGURATION ---
# This sets the browser tab title, icon, and layout.
st.set_page_config(
    page_title="Astro E-Commerce Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- CACHING THE CHATBOT MODEL ---
# Using @st.cache_resource ensures our complex ResponseGenerator class is loaded only once.
@st.cache_resource
def load_chatbot():
    """Loads and caches the ResponseGenerator instance for performance."""
    return ResponseGenerator()

# --- HELPER FUNCTION FOR THE TYPING EFFECT ---
def stream_response(text):
    """Yields characters from a string with a small delay to simulate a typing effect."""
    for char in text:
        yield char
        time.sleep(0.01) # Adjust this delay for faster/slower typing

# --- SIDEBAR INFORMATION ---
with st.sidebar:
    st.title("About Astro 🤖")
    st.markdown("""
    Astro is an advanced e-commerce support chatbot built with a Retrieval-Augmented Generation (RAG) system.
    
    It uses a dynamic knowledge base powered by a PostgreSQL database to provide accurate and up-to-date answers.
    """)
    st.markdown("---")
    st.subheader("Project Components:")
    # Updated to reflect the new architecture
    st.markdown("""
    - **UI:** Streamlit
    - **Orchestration:** Prefect
    - **Database:** PostgreSQL with pgvector
    - **LLM:** Google Gemini
    - **Embeddings:** Sentence Transformers
    """)
    st.markdown("---")
    st.markdown("Developed by Vinay.")

# --- MAIN CHAT INTERFACE ---
st.title("Astro E-Commerce Assistant")

# Load the chatbot from the cache
chatbot = load_chatbot()

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm Astro. How can I assist you with our products today?"}
    ]

# Display all past chat messages from the session state
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("Ask about product features or customer opinions..."):
    # Add user message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate and display the assistant's response
    with st.chat_message("assistant", avatar="🤖"):
        # Show a "thinking" spinner while the backend works
        with st.spinner("Astro is thinking..."):
            response_dict = chatbot.generate_answer(prompt)
            response_content = response_dict['answer']
            
            # Use st.write_stream to display the typing effect
            st.write_stream(stream_response(response_content))
            
            # Display the knowledge source in a subtle way
            source_info = f"<small>*(Knowledge source: {response_dict['source_store']})*</small>"
            st.markdown(source_info, unsafe_allow_html=True)
            
    # Add the full assistant response to history (without the source note)
    st.session_state.messages.append({"role": "assistant", "content": response_content})