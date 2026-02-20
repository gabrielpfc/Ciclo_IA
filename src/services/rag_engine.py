import os
import chromadb
from chromadb.utils import embedding_functions
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from src.config import VECTOR_DB_PATH

# Inicializa o Banco Vetorial (Persistente no Disco D)
chroma_client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
collection = chroma_client.get_or_create_collection(name="memoria_sistema")

def extract_text_from_file(uploaded_file):
    """Extrai texto de PDF, TXT ou Imagens (OCR)."""
    text = ""
    file_type = uploaded_file.type
    
    try:
        # PDF
        if "pdf" in file_type:
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            for page in doc:
                text += page.get_text()
                
        # Imagens (OCR)
        elif "image" in file_type:
            image = Image.open(uploaded_file)
            text = pytesseract.image_to_string(image, lang='por+eng')
            
        # Texto Simples / Código
        else:
            text = uploaded_file.read().decode("utf-8")
            
    except Exception as e:
        return f"[Erro na leitura do arquivo: {str(e)}]"
        
    return text

def add_to_memory(content, source="chat"):
    """Salva informação no banco vetorial."""
    if not content.strip(): return
    
    collection.add(
        documents=[content],
        metadatas=[{"source": source}],
        ids=[f"{source}_{hash(content)}"]
    )

def recall_memory(query, n_results=3):
    """Busca informações relevantes no banco."""
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    if results['documents']:
        return "\n".join(results['documents'][0])
    return ""
