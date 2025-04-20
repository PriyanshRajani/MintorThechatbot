import os
import PyPDF2
from sentence_transformers import SentenceTransformer
import faiss

model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight, fast

def read_documents_from_folder(folder="data"):
    all_texts = []
    file_sources = []

    if not os.path.exists(folder):
        raise FileNotFoundError(f"Data folder '{folder}' not found.")

    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        text = ""

        if filename.endswith(".pdf"):
            try:
                with open(filepath, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    text = "\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception as e:
                print(f"Failed to read {filename}: {e}")

        elif filename.endswith(".txt"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception as e:
                print(f"Failed to read {filename}: {e}")

        if text:
            # Simple character chunking (upgrade later if needed)
            chunks = [text[i:i+500] for i in range(0, len(text), 500)]
            all_texts.extend(chunks)
            file_sources.extend([filename] * len(chunks))

    if not all_texts:
        raise ValueError("No valid documents found or readable.")

    return all_texts, file_sources

def embed_text_chunks(chunks):
    vectors = model.encode(chunks)
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    return index, vectors
