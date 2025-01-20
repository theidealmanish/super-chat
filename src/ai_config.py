from .session import SESSION as S
from .session import SVC as SVC
import streamlit as st

NUM_CHUNKS = 5
COLUMNS = ["chunk_text", "source_url", "bot_id"]

S.sql("USE ROLE ACCOUNTADMIN").collect()
S.sql("""
    CREATE OR REPLACE TABLE CHUNKS (
        chunk_id INTEGER AUTOINCREMENT START 1 INCREMENT 1 PRIMARY KEY,
        bot_id INTEGER NOT NULL REFERENCES BOTS(bot_id) ON DELETE CASCADE,
        source_url VARCHAR(16777216) NOT NULL,
        chunk_text TEXT NOT NULL,
        created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
    )
""").collect()

def create_chunk(source_url, chunk_text, bot_id):
    """
    Create a chunk with auto-generated ID
    """
    S.sql(
        """
        INSERT INTO CHUNKS (bot_id, source_url, chunk_text)
        values (%s, %s, %s)
        """,
        (bot_id, source_url, chunk_text)
    ).collect()
    print("Chunk created successfully")

def get_similar_chunks(query):
    """
    Get similar chunks to the query
    """
    filter_obj = {"@eq": {"bot_id": st.query_params["bot_id"]} }
    response = SVC.search(query, COLUMNS, filter=filter_obj, limit=NUM_CHUNKS)
    print(response)
    return response.model_dump_json()  


def generate_prompt(question):
    """
    Generate prompt for the question
    """
    prompt_context = get_similar_chunks(question)
    prompt = f"""
           You are an expert chat assistance that extracs information from the CONTEXT provided
           between <context> and </context> tags.
           When ansering the question contained between <question> and </question> tags
           be concise and do not hallucinate. 
           If you don´t have the information just say so.
           Only anwer the question if you can extract it from the CONTEXT provideed.
           
           Do mention the CONTEXT used in your answer, with it's source URL in the url format.
    
           <context>          
           {prompt_context}
           </context>
           <question>  
           {question}
           </question>
           Answer: 
           """
    print("prompt: ", prompt)
    print("prompt context: ", prompt_context)

    




