import uuid
from datetime import datetime
from .session import SESSION
from .session import CURSOR as C

C.execute("USE ROLE ACCOUNTADMIN")
C.execute("""
    CREATE TABLE IF NOT EXISTS BOTS (
        bot_id INTEGER AUTOINCREMENT START 1 INCREMENT 1 PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        type VARCHAR(50) NOT NULL,
        image TEXT,
        source TEXT NOT NULL,
        created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
    )
""")

def create_bot(name, description, type, source):
    """
    Create a bot with auto-generated ID
    """
    
    C.execute("""
        INSERT INTO BOTS (bot_id, name, description, type, source, created_at) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (name, description, type, source))
    
    C.execute("COMMIT")
    return True

def get_bots():
    """
    Get all bots
    """
    C.execute("SELECT * FROM BOTS ORDER BY created_at DESC")
    bots = C.fetchall()
    return bots


