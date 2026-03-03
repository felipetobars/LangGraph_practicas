import os, re
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
# Pendiente de ajustar el path a la base de datos vectorial y al PDF de ejemplo
DB_DIR = "notebooks/chroma_db_rag"
PDF_PATH = './Mobile_Site_Speed_Playbook.pdf'

embeddings = OllamaEmbeddings(model="paraphrase-multilingual:latest")

# CARGA O CREACIÓN DE LA BASE DE DATOS VECTORIAL CON CHROMA
if os.path.exists(DB_DIR):
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    print("--- Base de Datos existente cargada---")
else:
    print("--- Procesando PDF ---")
    loader = PyPDFLoader(PDF_PATH)
    data = loader.load()

    def clean_text(text):
        text = re.sub(r'\n\d+\s*\n', '\n', text)
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        return " ".join(text.split())

    data_filtered = [doc for doc in data if len(doc.page_content.strip()) > 10]
    for doc in data_filtered:
        doc.page_content = clean_text(doc.page_content)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,        
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(data_filtered)

    vectorstore = Chroma.from_documents(
        documents=chunks, embedding=embeddings, persist_directory=DB_DIR
    )
    print(f"--- DB creada con {len(chunks)} chunks ---")

# CREACIÓN DEL RETRIEVER CON MMR PARA OBTENER RESPUESTAS MÁS RELEVANTES Y DIVERSAS   
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 8, "fetch_k": 10, "lambda_mult": 0.7})
print(vectorstore._collection.count())
print("--- Base de Datos existente cargada ---")

@tool
def file_search(query: str) -> str:
    """Responde preguntas sobre el contenido del documento."""
    docs = retriever.invoke(query)
    return "\n\n".join([doc.page_content for doc in docs])