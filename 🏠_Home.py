import streamlit as st
from streamlit_lottie import st_lottie

st.set_page_config(
    page_title="Super Chat",
    page_icon="🤖",
)


st_lottie(
    "https://lottie.host/4558edf0-221f-456b-b543-ad7559ff3ffb/pqfg88ohcA.json",
    height=300,
    loop=True,
    quality="high",
    speed=5
)

st.title('Super Chat')


st.subheader(
    'Let the website talk to you!'
)
st.write('This is a chatbot that can talk about anything you want. Just ask a question and it will answer you. '
         'If you want to know more about a specific topic, you can ask the chatbot to search for it in the web. '
         'You can also ask the chatbot to tell you a joke or a riddle. Have fun!')
