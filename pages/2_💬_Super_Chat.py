import streamlit as st
from snowflake.cortex import complete
from snowflake.core import Root
import json
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

try:
    from src.session import SVC, SESSION
    from src.ai_config import get_similar_chunks, fetch_article_content
    from src.bots import get_bot
except ImportError as e:
    st.error(
        f"Failed to import, reload the page...")
    sys.exit(1)

st.set_page_config(
    page_title="Super Chat",
    page_icon="🤖",
)
# Default Values
NUM_CHUNKS = 5
slide_window = 7


# Columns to query in the service
COLUMNS = [
    "chunk",
    "relative_path",
    "category"
]

session = SESSION
root = Root(session)
svc = SVC


def config_options():
    st.sidebar.selectbox('Select your model:', (
        'mistral-large2', 'mistral-large',
        'mistral-7b'), key="model_name"
    )

    st.sidebar.checkbox('Do you want that I remember the chat history?',
                        key="use_chat_history", value=True)


def init_messages():
    if st.session_state.get("clear_conversation") or "messages" not in st.session_state:
        st.session_state.messages = []


def get_chat_history():
    chat_history = []
    start_index = max(0, len(st.session_state.messages) - slide_window)
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

    if st.session_state.debug:
        st.sidebar.text(
            "Summary to be used to find similar chunks in the docs:")
        st.sidebar.caption(summary)

    summary = summary.replace("'", "")
    return summary


def create_prompt(myquestion, bot):
    if st.session_state.use_chat_history:
        chat_history = get_chat_history()
        if chat_history:
            question_summary = summarize_question_with_history(
                chat_history, myquestion)
            prompt_context = get_similar_chunks(
                question_summary)
        else:
            prompt_context = get_similar_chunks(myquestion)

    else:
        prompt_context = get_similar_chunks(myquestion)

    # Ensure `prompt_context` is properly parsed from JSON
    if isinstance(prompt_context, str):
        prompt_context = json.loads(prompt_context)

    # Extract source URLs
    source_urls = set(chunk["source_url"]
                      for chunk in prompt_context["results"])
    full_context = []
    for url in source_urls:
        content = fetch_article_content(url=url)
        full_context.append(
            {"context": content['content'], "source_url": content['source_url']})
    print(full_context)
    chat_history = ""

    prompt = f"""
            You are an expert chat assistant, you can find your identity in between <identity> and </identity> (That's what you call yourself),
            that extracts information from the CONTEXT provided
            between <context> and </context> tags.
            You offer a chat experience considering the information included in the CHAT HISTORY
            provided between <chat_history> and </chat_history> tags.
            
            When answering the question contained between <question> and </question> tags,
            be concise and do not hallucinate. Don't add your belief, make it more relevant to
            the context provided.

            If you don’t have the information, say you don't have that information, or you don't know.
            Don't say you are just an AI or AI assistant and explain. Keep it clear. 
            Don't let the user know that you are an AI, or AI assistant.

            Do not mention the CONTEXT used in your answer.
            Do not mention the CHAT HISTORY used in your answer.
            Make the answer DESCRIPTIVE, and EXPLAINING, don't make it vague.

            If you are to generate code, make it same as they are, as they
            are the official documentation of the project. Make it real, and exact.
            
            Provide all the sources as Source: with relevant URLs of the context you are using, that are clickable. 
            Only answer the question if you can extract it from the CONTEXT provided.
            
            <identity>
            Name: {bot['NAME']}
            Description: {bot['DESCRIPTION']}
            </identity> 
            <chat_history>
            {chat_history}
            </chat_history>
            <context>          
            {full_context}
            </context>
            <question>  
            {myquestion}
            </question>
            Answer:
           """

    # Ensure `prompt_context` is still parsed as JSON
    source_urls = set(chunk['source_url']
                      for chunk in prompt_context["results"])
    return prompt, source_urls


def answer_question(myquestion, bot):
    prompt, source_urls = create_prompt(myquestion, bot=bot)
    response = complete(st.session_state.model_name, prompt, session=session)
    return response, source_urls


def main():
    if "bot_id" in st.query_params:
        bot_id = st.query_params["bot_id"]
        bot = get_bot(bot_id)

        st.title(f"💬 Super Chat with {bot['NAME']}")

        config_options()
        init_messages()

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if question := st.chat_input("What do you want to know about your products?"):
            st.session_state.messages.append(
                {"role": "user", "avatar": bot['IMAGE_URL'], "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant", avatar=f"{bot['IMAGE_URL']}"):
                message_placeholder = st.empty()
                question = question.replace("'", "")
                with st.spinner(f"{bot['Name']} thinking..."):
                    response, source_urls = answer_question(question, bot=bot)
                    response = response.replace("'", "")
                    message_placeholder.markdown(response)

                st.session_state.messages.append(
                    {"role": "assistant", "content": response})
    else:
        st.error("Please select a bot first from Create or Choose Bot page")
        time.sleep(2)
        st.switch_page("pages/1_🤖_Create_or_Choose_Bot.py")


if __name__ == "__main__":
    main()
