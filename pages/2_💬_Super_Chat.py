import streamlit as st
from pathlib import Path
import sys
import time
from snowflake.cortex import complete

# Add parent directory to sys.path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import required modules and the SuperRAG class
try:
    from src.session import SVC, SESSION
    from src.bots import get_bot
    # Assuming SuperRAG is implemented in src/super_rag
    from src.RAG import SuperRAG
except ImportError as e:
    st.error(f"Failed to import, reload the page...")
    sys.exit(1)

# Page Configuration
st.set_page_config(
    page_title="Super Chat",
    page_icon="🤖",
)

# Initialize Session and SVC
session = SESSION
svc = SVC

# Constants
NUM_CHUNKS = 5
SLIDE_WINDOW = 7

# Initialize the SuperRAG instance


def initialize_super_rag(bot_id, model_name="mistral-large2"):
    return SuperRAG(bot_id=bot_id, model_name=model_name, num_chunks=NUM_CHUNKS, session=session)


# Chat History Initialization
def init_messages():
    if st.session_state.get("clear_conversation") or "messages" not in st.session_state:
        st.session_state.messages = []


# Sidebar Configuration
def config_options():
    st.sidebar.selectbox('Select your model:', (
        'mistral-large2', 'mistral-large', 'mistral-7b'), key="model_name"
    )
    st.sidebar.checkbox('Do you want that I remember the chat history?',
                        key="use_chat_history", value=True)
    st.sidebar.button("Start Over", key="clear_conversation",
                      on_click=init_messages)


def get_chat_history():
    chat_history = []
    start_index = max(0, len(st.session_state.messages) - SLIDE_WINDOW)
    for i in range(start_index, len(st.session_state.messages) - 1):
        chat_history.append(st.session_state.messages[i])

    return chat_history


def summarize_question_with_history(chat_history, question):
    prompt = f"""
        Based on the chat history below and the question, generate a query that extend the question
        with the chat history provided. The query should be in natural language. 
        Answer with only the query. Do not add any explanation.
        
        <chat_history>
        {chat_history}
        </chat_history>
        <question>
        {question}
        </question>
        """

    summary = complete(st.session_state.model_name, prompt, session=session)
    return summary


# Streamlit App Logic


def main():
    # Check if bot_id is provided in query parameters
    if "bot_id" in st.query_params:
        bot_id = st.query_params["bot_id"]
        bot = get_bot(bot_id)

        # Initialize the SuperRAG instance
        super_rag = initialize_super_rag(
            bot_id=bot_id, model_name=st.session_state.get("model_name", "mistral-large2"))

        # Set up the page title and bot info
        st.title(f"💬 Super Chat with {bot['NAME']}")

        # Sidebar Configuration
        config_options()

        # Initialize chat history
        init_messages()

        # Display existing messages from chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Handle user input
        if question := st.chat_input("What do you want to know about your products?"):
            # Add user message to chat history
            st.session_state.messages.append(
                {"role": "user",
                 "content": question}
            )
            with st.chat_message("user"):
                st.markdown(question)

            # Generate assistant response using SuperRAG
            with st.chat_message("assistant", avatar=f"{bot['IMAGE_URL']}"):
                message_placeholder = st.empty()
                question = question.replace("'", "")
                with st.spinner(f"{bot['NAME']} is thinking..."):
                    try:
                        # Use SuperRAG's `query` method to generate a response
                        chat_history = summarize_question_with_history(
                            get_chat_history(), question) if st.session_state.use_chat_history else []
                        response = super_rag.query(
                            query=question, chat_history=chat_history)
                        response = response.replace("'", "")
                    except Exception as e:
                        response = f"An error occurred: {str(e)}"

                    message_placeholder.markdown(response)

                # Add assistant response to chat history
                st.session_state.messages.append(
                    {"role": "assistant",
                        "avatar": f"{bot['IMAGE_URL']}",  "content": response}
                )
    else:
        # Redirect to the bot selection page if no bot_id is provided
        st.error("Please select a bot first from the Create or Choose Bot page.")
        time.sleep(2)
        st.switch_page("pages/1_🤖_Create_or_Choose_Bot.py")


if __name__ == "__main__":
    main()
