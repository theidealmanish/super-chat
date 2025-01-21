from .session import SESSION as S
from .session import SVC as SVC
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .preprocess import get_urls_from_sitemap, fetch_article_content

NUM_CHUNKS = 5
COLUMNS = ["chunk_text", "source_url", "bot_id"]


def create_chunk(bot_id, sitemap_url):
    """
    process_sitemap
    """
    if "sitemap.xml" in sitemap_url:
        urls = get_urls_from_sitemap(sitemap_url)
    else:
        urls = sitemap_url.split(",")
    for url in urls:
        content = fetch_article_content(url)
        if content:
            # split the content using text splitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=512, chunk_overlap=128)
            chunks = text_splitter.split_text(content['content'])

            for chunk in chunks:
                print(chunk)
                # store it into the database
                S.sql(
                    """
                    INSERT INTO CHUNKS (bot_id, source_url, chunk_text)
                    values (?, ?, ?)
                    """,
                    params=[bot_id, content["source_url"], chunk]
                ).collect()
                S.sql("COMMIT").collect()
                print("Chunk created successfully")


def get_similar_chunks(query):
    """
    Get similar chunks to the query
    """
    filter_obj = {"@eq": {"bot_id": st.query_params["bot_id"]}}
    response = SVC.search(query, COLUMNS, filter=filter_obj, limit=NUM_CHUNKS)
    return response.model_dump_json()
