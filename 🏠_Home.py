import streamlit as st
from streamlit_lottie import st_lottie

st.set_page_config(
    page_title="Super Chat",
    page_icon="🤖",
)


st_lottie(
    "https://lottie.host/4558edf0-221f-456b-b543-ad7559ff3ffb/pqfg88ohcA.json",
    height=200,
    loop=True,
    quality="high",
    speed=5
)

st.title('💬 Super Chat')

st.subheader(
    'Talk to Your Website, Simplified!'
)

st.write(
    "Welcome to **Super Chat**, your smart assistant for interacting with website content. Simply provide a sitemap or list of URLs, "
    "and let Super Chat handle the rest. Ask natural language questions, and get precise, contextually relevant answers instantly. "
    "Whether you're diving into complex documentation, exploring a new topic, or just looking for quick insights, Super Chat makes it effortless."
)

st.write(
    "Ready to experience smarter interactions? Ask away, and let Super Chat bring the answers to you!"
)
