from src.session import SESSION as S, SVC
import json
import streamlit as st
from snowflake.cortex import complete
import sys
from pathlib import Path
import time
from src.bots import get_bot

sys.path.append(str(Path(__file__).parent.parent))


NUM_CHUNKS = 5
slide_window = 10

st.set_page_config(
    page_title="Super Chat",
    page_icon="💬",
)


# columns to query in the service
COLUMNS = [
    "chunk_text",
    "source_url",
    "bot_id"
]

session = S
svc = SVC

if "bot_id" in st.query_params:
    bot_id = st.query_params["bot_id"]
    bot = get_bot(st.query_params["bot_id"])
    # if no bot
    if bot is None:
        st.error("Bot not found")
        time.sleep(2)
        st.switch_page("1_🤖_Create_or_Choose_Bot.py")

    def config_options():
        st.sidebar.selectbox('Select your model:', (
            'mistral-large2',
            'mistral-large',
        ), key="model_name", index=0)

        st.sidebar.checkbox('Do you want that I remember the chat history?',
                            key="use_chat_history", value=True)
        st.sidebar.button(
            "Start Over", key="clear_conversation", on_click=init_messages)
        st.sidebar.checkbox(
            'Debug: Click to see summary generated of previous conversation', key="debug", value=True)
        st.sidebar.expander("Session State").write(st.session_state)

    def init_messages():
        # Initialize chat history
        if st.session_state.clear_conversation or "messages" not in st.session_state:
            st.session_state.messages = []

    def get_similar_chunks_search_service(query):
        filter_obj = {"@eq": {"bot_id": str(bot_id)}}
        response = svc.search(
            query, COLUMNS, filter=filter_obj, limit=NUM_CHUNKS, session=S)
        print("Similar chunks: ", response)
        return response.model_dump_json()

    def get_chat_history():
        # Get the history from the st.session_stage.messages according to the slide window parameter

        chat_history = []

        start_index = max(0, len(st.session_state.messages) - slide_window)
        for i in range(start_index, len(st.session_state.messages) - 1):
            chat_history.append(st.session_state.messages[i])

        return chat_history

    def summarize_question_with_history(chat_history, question):
        # To get the right context, use the LLM to first summarize the previous conversation
        # This will be used to get embeddings and find similar chunks in the docs for context

        prompt = f"""
            Based on the chat history below and the question, generate a query that extend the question
            with the chat history provided. The query should be in natual language. 
            Answer with only the query. Do not add any explanation.
            
            <chat_history>
            {chat_history}
            </chat_history>
            <question>
            {question}
            </question>
            """

        summary = complete(st.session_state.model_name, prompt, session=S)
        if st.session_state.debug:
            st.sidebar.text(
                "Summary to be used to find similar chunks in the docs:")
            st.sidebar.caption(summary)

        return summary

    # create prompt
    def create_prompt(myquestion):

        if st.session_state.use_chat_history:
            chat_history = get_chat_history()

            if chat_history != []:  # There is chat_history, so not first question
                question_summary = summarize_question_with_history(
                    chat_history, myquestion)
                prompt_context = get_similar_chunks_search_service(
                    question_summary)
            else:
                prompt_context = get_similar_chunks_search_service(
                    myquestion)
        else:
            prompt_context = get_similar_chunks_search_service(myquestion)
            chat_history = ""
        # get the source urls
        json_data = json.loads(prompt_context)
        source_urls = set(item['source_url']
                          for item in json_data['results'])
        prompt = f"""
            You are an expert chat assistant.
            Your identity is in between <identity> and </identity> tags,
            whenever you are asked question about you, like who are you, what is your name etc.,
            you answer based on the <identity> tags.
            
            You extract information from the CONTEXT provided
            between <context> and </context> tags.

            You offer a chat experience considering the information included in the CHAT HISTORY
            provided between <chat_history> and </chat_history> tags.
            When answering the question contained between <question> and </question> tags
            be concise and do not hallucinate. 
            
            You may take reference from the chat history, about what questions where asked.
            To answer questions, you must use the information provided in the CONTEXT in between
            <context> and </context> tags. You may generate answer with around 150+ words. Don't make
            it too long, and don't make it too short and vague. 

            If you are generating the code, make it related to the question asked, and the context provided.
            The generated code should be from the context, you can merge multiple context if necessary. But 
            don't generate code that is not related to the context provided.

            If you don't have the information just say so.
            Don't say you are an AI assistant or a bot. Don't make the questioning person
            aware that you are an AI assistant.
            
            Do not mention the CONTEXT used in your answer.
            Do not mention the CHAT HISTORY used in your asnwer.

            Only answer the question if you can extract it from the CONTEXT provideed.
            
            The source urls are provided in the <source_url> and </source_url> tags. 
            You add the "Source: " as a clickable link after the answers for the user to 
            verify the information.

            <identity>
            Name: {bot['NAME']}
            Description: {bot['DESCRIPTION']}
            </identity>
            <chat_history>
            {chat_history}
            </chat_history>
            <context>          
            {prompt_context}
            </context>
            <source_url>
            {source_urls}
            </source_url>
            <question>  
            {myquestion}
            </question>
            Answer: 
            """
        return prompt, source_urls

    def answer_question(myquestion):
        prompt, source_urls = create_prompt(myquestion)
        response = complete(st.session_state.model_name, prompt, session=S)
        return response, source_urls

    def main():
        st.title(f"💬 Super Chat with {bot['NAME']}")
        config_options()
        init_messages()

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar=message.get("avatar", None)):
                st.markdown(message["content"])

        # Accept user input
        if question := st.chat_input("What do you want to know?"):
            # Add user message to chat history
            st.session_state.messages.append(
                {"role": "user", "content": question})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(question)
            # Display assistant response in chat message container
            with st.chat_message("assistant", avatar=bot['image_url']):
                message_placeholder = st.empty()
                print("question: ", question)

                with st.spinner(f"{bot['NAME']} thinking..."):
                    response, source_urls = answer_question(question)
                    print("response: ", response)
                    message_placeholder.markdown(response)

            st.session_state.messages.append(
                {"role": "assistant", "avatar": bot['image_url'],  "content": response})

else:
    st.error("Bot not found")
    time.sleep(2)
    st.switch_page("./pages/1_🤖_Create_or_Choose_Bot.py")

if __name__ == "__main__":
    main()
