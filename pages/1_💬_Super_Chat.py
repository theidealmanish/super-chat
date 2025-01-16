import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from src.bots import create_bot, get_bots

# get all bots
print(get_bots())

# add source
@st.dialog("Add your source")
def add_source(bot):
    name = st.text_input("Name your bot")
    description = st.text_area("Describe your bot")
    type = st.selectbox("Type of source", ["Website", "Sitemap", "Youtube", "PDF"])
    image = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
    if type == "Website":
        source = st.text_input("Enter the website url")
    elif type == "Sitemap":
        source = st.text_input("Enter the sitemap url")
    elif type == "PDF":
        source = st.file_uploader("Upload the PDF")
    if st.button("Submit"):
        st.session_state.source = {"name": name, "description": description, "type": type, "source": source}
        print(st.session_state.source)
        create_bot(name, description, type, image, source)
        
st.title("Super Chat")

from streamlit_card import card

if st.button("Add Source"):
    add_source("Python")


# Fetch bots from database
bots = [
    {
        "bot_id": 1,
        "name": "Bot 1",
        "description": "This is bot 1",
        "type": "Website",
        "image": "https://static.streamlit.io/examples/cat.jpg",
        "source": "XXXXXXXXXXXXXXXXXXXXXX"
    },
    {
        "bot_id": 2,
        "name": "Bot 2",
        "description": "This is bot 2",
        "type": "Sitemap",
        "image": "https://static.streamlit.io/examples/cat.jpg",
        "source": "XXXXXXXXXXXXXXXXXXXXXX"
    },
    {
        "bot_id": 3,
        "name": "Bot 3",
        "description": "This is bot 3",
        "type": "Youtube",
        "image": "https://static.streamlit.io/examples/cat.jpg",
        "source": "XXXXXXXXXXXXXXXXXXXXXX"
    },
    {
        "bot_id": 4,
        "name": "Bot 4",
        "description": "This is bot 4",
        "type": "PDF",
        "image": "https://static.streamlit.io/examples/cat.jpg",
        "source": "XXXXXXXXXXXXXXXXXXXXXX"
    }
]

# Create columns for card layout
cols = st.columns(2)

# Display bots in grid
for idx, bot in enumerate(bots):
    with cols[idx % 2]:
        hasClicked = card(
            key=bot["name"],
            title=bot["name"],
            text=bot["description"],
            image=bot["image"],
            styles={
                "card": {
                    "width": "300px", 
                    "height": "300px",
                },
            },
            url="https://github.com/gamcoh/st-card"
        )
