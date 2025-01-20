import streamlit as st
from src.bots import get_bot
import time

if "bot_id" in st.query_params:
    bot_id = st.query_params["bot_id"]
    bot = get_bot(bot_id)

    st.title("💬 Super Chat")
    st.write(f"Bot Name: {bot['NAME']}")
    st.write("Super Chat")

    st.text_area("Chat with bot", height=100)
    st.button("Send")


else:
    st.error("Please select a bot first from Create or Choose Bot page")
    time.sleep(2)
    st.switch_page("pages/1_🤖_Create_Bot.py")
