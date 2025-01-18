from .session import CURSOR as C

C.execute("USE ROLE ACCOUNTADMIN")

def upload_file(file):
    """
    Upload an image to the database
    """
    C.execute("""
    PUT file://{file} @files
    """)
    C.execute("COMMIT")
    return True
