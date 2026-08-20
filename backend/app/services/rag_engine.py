"""Nirnaya RAG Knowledge Engine.

Loads official guidelines (RBI, Cybercrime), chunks them, and builds
a FAISS vector index for retrieval during LangGraph orchestration.
"""

import logging
from pathlib import Path
from typing import List

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent.parent
KNOWLEDGE_DIR = BASE_DIR / "data" / "knowledge"
MODELS_DIR = BASE_DIR / "app" / "ml" / "models"
RAG_INDEX_PATH = MODELS_DIR / "rag_faiss_index"

MODEL_NAME = 'all-MiniLM-L6-v2'

_vectorstore = None


def get_embeddings():
    """Load the embeddings model."""
    # This uses the same underlying sentence-transformers model as semantic_engine
    return HuggingFaceEmbeddings(model_name=MODEL_NAME)


def _build_rag_index():
    """Load documents, chunk them, and build the FAISS index."""
    if not KNOWLEDGE_DIR.exists():
        logger.error(f"Knowledge directory not found: {KNOWLEDGE_DIR}")
        return False
        
    logger.info("Building RAG vector index from knowledge base...")
    
    loader = DirectoryLoader(str(KNOWLEDGE_DIR), glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()
    
    if not documents:
        logger.warning("No markdown documents found in knowledge base.")
        return False
        
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Split into {len(chunks)} chunks.")
    
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(RAG_INDEX_PATH))
    logger.info(f"Saved RAG index to {RAG_INDEX_PATH}")
    return True


def load_rag_index():
    """Load the RAG FAISS index into memory."""
    global _vectorstore
    
    if not RAG_INDEX_PATH.exists():
        success = _build_rag_index()
        if not success:
            return False
            
    if _vectorstore is None:
        embeddings = get_embeddings()
        _vectorstore = FAISS.load_local(str(RAG_INDEX_PATH), embeddings, allow_dangerous_deserialization=True)
        logger.info("Loaded RAG FAISS index.")
        
    return True


def retrieve_knowledge(query: str, top_k: int = 2) -> str:
    """Retrieve relevant knowledge chunks for a given query.
    
    Returns:
        Formatted string containing the retrieved chunks.
    """
    if not query or not load_rag_index():
        return "No relevant guidelines found."
        
    docs = _vectorstore.similarity_search(query, k=top_k)
    
    if not docs:
        return "No relevant guidelines found."
        
    formatted = []
    for i, doc in enumerate(docs):
        source = Path(doc.metadata.get("source", "unknown")).name
        formatted.append(f"--- Document: {source} ---\n{doc.page_content}")
        
    return "\n\n".join(formatted)

if __name__ == "__main__":
    _build_rag_index()
    res = retrieve_knowledge("Who is liable if I share my OTP and lose money?")
    print(res)
