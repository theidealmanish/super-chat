from .session import CURSOR as C

C.execute("USE ROLE ACCOUNTADMIN")
C.execute("""
    CREATE OR REPLACE TABLE DOCS_CHUNKS_TABLE (
        chunk_id INTEGER AUTOINCREMENT START 1 INCREMENT 1 PRIMARY KEY,
        bot_id INTEGER NOT NULL REFERENCES BOTS(bot_id) ON DELETE CASCADE,
        main_url VARCHAR(16777216) NOT NULL,
        source_url VARCHAR(16777216) NOT NULL,
        chunk_text TEXT NOT NULL,
        created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
    )
""")

def create_chunk(source_url, chunk_text, bot_id, main_url):
    """
    Create a chunk with auto-generated ID
    """
    C.execute(
        """
        INSERT INTO DOCS_CHUNKS_TABLE (source_url, chunk_text, bot_id, main_url)
        values (%s, %s, %s, %s)
        """,
        (source_url, chunk_text, bot_id, main_url)
    )


