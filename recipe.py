import os
import json
from datetime import datetime
from dotenv import load_dotenv
# Document Loading
from langchain_community.document_loaders import CSVLoader
# Text Splitting
from langchain_text_splitters import RecursiveCharacterTextSplitter
# Embeddings (NEW PACKAGE)
from langchain_huggingface import HuggingFaceEmbeddings
# Vector Store
from langchain_community.vectorstores import FAISS
# Prompt Template
from langchain_core.prompts import PromptTemplate
# LLM
from langchain_groq import ChatGroq
# Memory
from langchain_classic.memory import ConversationBufferMemory
# Chains
from langchain_classic.chains import ConversationalRetrievalChain

def create_recipegpt_chain():
    # 2. LOAD ENVIRONMENT VARIABLES
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    # 3. CONFIGURATION
    DATASET_PATH = "Dataset.csv"
    FAISS_INDEX_PATH = "faiss_index"
    RECENTS_DIR = "recents"
    os.makedirs(RECENTS_DIR, exist_ok=True)
    # 4. LOAD DATASET
    print("Loading recipe dataset...")
    loader = CSVLoader(DATASET_PATH, encoding="utf-8")
    documents = loader.load()
    # 5. CHUNK DOCUMENTS
    print("Splitting documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    docs = splitter.split_documents(documents)
    # 6. CREATE EMBEDDINGS
    print("Loading embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    # 7. CREATE OR LOAD FAISS INDEX
    if os.path.exists(FAISS_INDEX_PATH):
        print("Loading existing FAISS index...")
        vector_db = FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        print("Creating FAISS index for the first time...")
        vector_db = FAISS.from_documents(docs, embeddings)
        vector_db.save_local(FAISS_INDEX_PATH)
        print("FAISS index saved successfully.")
    # 8. CREATE RETRIEVER
    retriever = vector_db.as_retriever(
        search_kwargs={"k": 5}
    )
    # 9. CUSTOM PROMPT
    prompt_template = """
    You are RecipeGPT AI, a professional chef.
    IMPORTANT RULES:
    1. Answer only using the provided dataset context.
    2. If the answer is not present in the dataset, say:
    "I could not find relevant information in the recipe dataset."
    3. Maintain conversation with the user.
    4. Explain recipes clearly based on user request (simple or detailed).
    5. You need to specialize in the following things:
    - Recipe Generation
    - Ingredient Suggestions
    - Meal Planning
    - Ingredient-Based Recipe Search
    6. For ingredient-based queries, identify recipes that use the mentioned ingredients.
    7. Format answers in a clean, readable way.
    Conversation History:
    {chat_history}
    Context:
    {context}
    Question:
    {question}
    Answer:
    """
    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["chat_history", "context", "question"]
    )
    # 10. LOAD GROQ MODEL
    print("Loading Groq model...")
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=GROQ_API_KEY,
        temperature=0.2
    )
    # 11. MEMORY
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )
    # 12. CONVERSATIONAL RETRIEVAL CHAIN
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": PROMPT},
        return_source_documents=True,
        verbose=False
    )
    print("RecipeGPT is Ready!")
    return qa_chain