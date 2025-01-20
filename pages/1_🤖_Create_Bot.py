import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from src.bots import create_bot, get_bots

# get all bots
bots = get_bots()

# add source
@st.dialog("Add your source")
def add_source():
    name = st.text_input("Name your bot")
    description = st.text_area("Describe your bot")
    image_url = st.text_input("Enter the image url")
    type = st.selectbox("Type of source", ["Website links", "Sitemap"])
    if type == "Website links":
        source = st.text_input("Enter the website links (separated by comma)", placeholder="https://react.dev/docs/form, https://react.dev/docs/input, ...")
    elif type == "Sitemap":
        source = st.text_input("Enter the sitemap url")
    if st.button("Submit"):
        st.session_state.source = {"name": name, "description": description, "image_url": image_url, "type": type, "source": source}
        create_bot(name=name, description=description, image_url=image_url, type=type, source=source)
        st.rerun()
        
st.title("Create bot")

from streamlit_card import card

if st.button("Add Source"):
    add_source()

# Create columns for card layout
cols = st.columns(3)

# Display bots in grid
for idx, bot in enumerate(bots):
    with cols[idx % 3]:
        hasClicked = card(
            key=str(bot["BOT_ID"]),
            title=bot["NAME"],
            text=bot["DESCRIPTION"],
            image=bot["IMAGE_URL"],
            styles={
                "card": {
                    "width": "200px", 
                    "height": "200px",
                    "padding": "10px",
                    "margin": "10px",
                },
            },
            url=f"/Super_Chat?bot_id={str(bot['BOT_ID'])}"
        )
