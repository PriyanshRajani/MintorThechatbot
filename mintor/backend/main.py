from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.llms import Ollama

import os
from pathlib import Path

app = FastAPI()

# CORS settings for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request body
class ChatRequest(BaseModel):
    message: str

VECTORSTORE_DIR = "vector_store"
DATA_DIR = "data"
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Initialize global components
vectorstore = None
qa_chain = None

# Load and embed documents from local data/ folder
def load_documents_from_data_dir():
    docs = []
    for file in Path(DATA_DIR).rglob("*"):
        if file.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(file))
            docs.extend(loader.load())
        elif file.suffix.lower() == ".txt":
            try:
                loader = TextLoader(str(file), encoding="utf-8")
                docs.extend(loader.load())
            except Exception as e:
                print(f"⚠️ Skipping file due to encoding error: {file} ({e})")
    return docs

# Create and save vector store
def build_vectorstore():
    print("🔄 Building vector store from data/ folder...")
    raw_docs = load_documents_from_data_dir()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(raw_docs)

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTORSTORE_DIR)
    print("✅ Vector store saved.")
    return vectorstore

# Load vector store from disk (safe pickle deserialization)
def load_vectorstore():
    print("📦 Loading existing vector store...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
    return FAISS.load_local(VECTORSTORE_DIR, embeddings, allow_dangerous_deserialization=True)

# Setup QA chain
def setup_qa_chain(vstore):
    retriever = vstore.as_retriever()
    return RetrievalQA.from_chain_type(
        llm=Ollama(model="mistral"),
        retriever=retriever,
        return_source_documents=True
    )

# Startup logic
if Path(VECTORSTORE_DIR).exists():
    try:
        vectorstore = load_vectorstore()
    except Exception as e:
        print("💥 Failed to load vector store. Rebuilding...")
        vectorstore = build_vectorstore()
else:
    vectorstore = build_vectorstore()

qa_chain = setup_qa_chain(vectorstore)
print("🚀 Mintor QA system ready.")

# Chat endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    message = request.message.strip()
    print(f"🔥 /chat endpoint hit with: {message}")

    if not message:
        print("⚠️ Empty message received.")
        return {"error": "Empty message"}

    try:
        result = qa_chain({"query": message})
        response = result.get("result", "").strip()

        if not response:
            print("⚠️ LLM returned an empty response.")
            return {"response": "Sorry, I couldn't find a good answer to that."}

        print("✅ Mintor reply:", response)
        for doc in result.get("source_documents", []):
            print("📄 Source snippet:", doc.page_content[:200])

        return {"response": response}

    except Exception as e:
        print("💥 Internal server error:", str(e))
        return {"error": "Internal error", "details": str(e)}

# Reload documents and rebuild vector store
@app.post("/reload-docs")
async def reload_docs():
    global vectorstore, qa_chain
    try:
        vectorstore = build_vectorstore()
        qa_chain = setup_qa_chain(vectorstore)
        return {"status": "✅ Vector store reloaded successfully"}
    except Exception as e:
        print("💥 Reload error:", str(e))
        return {"error": "Failed to reload vector store", "details": str(e)}
