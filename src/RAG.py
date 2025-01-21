from trulens.apps.custom import instrument
from trulens.providers.cortex.provider import Cortex
from trulens.core.guardrails.base import context_filter
from trulens.core import Feedback
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from snowflake.cortex import complete
import numpy as np
from .session import SESSION as S, SVC
from .bots import get_bot
from .preprocess import get_urls_from_sitemap, fetch_article_content

provider = Cortex(S, "mistral-large2")


class RAG:
    def __init__(self, bot_id, model_name, num_chunks, session=S):
        """
        Initialize the Retrieval-Augmented Generation (RAG) system.
        """
        self.bot = get_bot(bot_id)
        self.model_name = model_name
        self.num_chunks = num_chunks
        self.columns = ["chunk_text", "source_url", "bot_id"]
        self.session = session

    def create_chunks(self, sitemap_url):
        """
        Process a sitemap or list of URLs, split the content into chunks, and store in the database.
        """
        if "sitemap.xml" in sitemap_url:
            urls = get_urls_from_sitemap(sitemap_url)
        else:
            urls = sitemap_url.split(",").trim()

        for url in urls:
            content = fetch_article_content(url)
            if content:
                # Split content into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=512, chunk_overlap=128)
                chunks = text_splitter.split_text(content['content'])

                for chunk in chunks:
                    print(chunk)
                    # Store each chunk in the database
                    self.session.sql(
                        """
                        INSERT INTO CHUNKS (bot_id, source_url, chunk_text)
                        VALUES (?, ?, ?)
                        """,
                        params=[self.bot['BOT_ID'],
                                content["source_url"], chunk]
                    ).collect()
                    self.session.sql("COMMIT").collect()
                    print("Chunk created successfully.")
                    print("===================================")

    @instrument
    def retrieve_context(self, query):
        """
        Retrieve relevant text chunks from the database using Cortex Search.
        """
        filter_obj = {"@eq": {"bot_id": str(self.bot['BOT_ID'])}}
        response = SVC.search(
            query, self.columns, filter=filter_obj, limit=self.num_chunks, session=self.session
        )
        return json.loads(response.model_dump_json())['results']

    @instrument
    def generate_completion(self, query, context_str, chat_history=None):
        """
        Generate a response to the query using the provided context and chat history.
        """
        if chat_history is None:
            chat_history = []

        # send entire page for better context in terms of coding docs
        full_context = []
        urls = set(context['source_url'] for context in context_str)
        for url in urls:
            web_content = fetch_article_content(url)
            full_context.append(
                {"content": web_content, "source_url": url})

        prompt = f"""
        You are an expert chat assistant, you can find your identity in between <identity> and </identity> (That's what you call yourself),
        that extracts information from the CONTEXT provided
        between <context> and </context> tags.
        You offer a chat experience considering the information included in the CHAT HISTORY
        provided between <chat_history> and </chat_history> tags.
        
        When answering the question contained between <question> and </question> tags,
        be concise and do not hallucinate. Don't add your belief, make it more relevant to
        the context provided. Please provide the answer based on the content inside the 
        <context> and </context> tags. If there is no information in the context i.e [], say you don't have the information gracefully.
        Strictly, your answer should be based on CONTEXT.If you are to generate code, make it same as they are in the context, 
        only correct it if necessary syntatically.

        
        Don't say I am just an AI or AI assistant. Don't let the user know that you are an AI, or AI assistant.

        Do not mention the CONTEXT used in your answer.
        Do not mention the CHAT HISTORY used in your answer.
        Make the answer DESCRIPTIVE, and EXPLAINING, don't make it vague and short (make it at least 100 words).

        
        Provide all the sources as Source: with relevant URLs of the context you are using, that are clickable. 
        Only answer the question if you can extract it from the CONTEXT provided.
        
        <identity>
        Name: {self.bot['NAME']}
        Description: {self.bot['DESCRIPTION']}
        </identity> 
        <chat_history>
        {chat_history}
        </chat_history>
        <context>          
        {full_context}
        </context>
        <question>  
        {query}
        </question>
        <Source>
        {urls}
        </Source>
        Answer:
        """
        # Generate response using the LLM
        response = complete(self.model_name, prompt, session=self.session)
        return response

    @instrument
    def query(self, query, chat_history):
        """
        Perform a complete query by retrieving relevant chunks and generating a response.
        """
        # Step 1: Retrieve context
        retrieved_context = self.retrieve_context(query)
        # Step 2: Generate response
        response = self.generate_completion(
            query=query, context_str=retrieved_context, chat_history=chat_history)
        return response


# Feedback Function for Context Filtering
f_context_relevance_score = Feedback(
    provider.context_relevance, name="Context Relevance"
)


class SuperRAG(RAG):
    @instrument
    @context_filter(f_context_relevance_score, threshold=0.75, keyword_for_prompt="query")
    def retrieve_context(self, query):
        """
        Retrieve relevant text from the vector store with filtering applied.
        """
        return super().retrieve_context(query)
