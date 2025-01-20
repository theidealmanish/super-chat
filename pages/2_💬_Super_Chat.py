import streamlit as st

if "bot_id" in st.query_params:
    st.write(f"Bot ID: {st.query_params['bot_id']}")

    st.write("Super Chat")


    st.text_area("Chat with bot", height=100)
    st.button("Send")


else:
    st.switch_page("pages/1_🤖_Create_Bot.py")


