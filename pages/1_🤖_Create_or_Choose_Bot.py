from streamlit_card import card
from src.ai_config import create_chunk
from src.bots import create_bot, get_bots
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Create or Choose bot",
    page_icon="🤖",
)

# get all bots
bots = get_bots()


@st.dialog("Add your source")
def add_source():
    name = st.text_input("Name", placeholder="Terminator")
    tagline = st.text_input("Tagline", placeholder="I'll be back")
    description = st.text_area(
        "Description", placeholder="I'm a bot that can chat with you. Ask me how to disable me.")
    image_url = st.text_input(
        "Image", placeholder="https://terminator.com/cool-guy.jpg") or "https://img.freepik.com/free-vector/graident-ai-robot-vectorart_78370-4114.jpg"
    type = st.selectbox("Type of source", ["Website links", "Sitemap"])
    if type == "Website links":
        source = st.text_input("Enter the website links (separated by comma)",
                               placeholder="https://react.dev/docs/form, https://react.dev/docs/input, ...")
    elif type == "Sitemap":
        source = st.text_input("Enter the sitemap url")

    st.error(
        "We have limited the bot creation due to spamming. Please visit our GitHub to clone the repo and try it.")
    st.markdown(
        "[GitHub Repo](https://github.com/theidealmanish/super-chat)")

    if st.button("Submit", disabled=True):
        with st.spinner("Creating bot..."):
            st.session_state.source = {"name": name, "tagline": tagline, "description": description,
                                       "image_url": image_url, "type": type, "source": source}
            bot_id = create_bot(name=name, tagline=tagline, description=description,
                                image_url=image_url, type=type, source=source)
            create_chunk(bot_id, sitemap_url=source)
            st.rerun()


st.title("🤖 Create or Choose bot")


if st.button("Create a new bot"):
    add_source()

# Create columns for card layout
cols = st.columns(3)

# Display bots in grid
for idx, bot in enumerate(bots):
    with cols[idx % 3]:
        hasClicked = card(
            key=str(bot["BOT_ID"]),
            title=bot["NAME"],
            text=bot["TAGLINE"],
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
