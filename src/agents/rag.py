import re, os
from langchain_community.document_loaders import PyPDFLoader
import random
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain.agents import create_agent
import warnings
warnings.filterwarnings("ignore")
DB_DIR = "notebooks/chroma_db_rag"
PDF_PATH = './Mobile_Site_Speed_Playbook.pdf'

llm = ChatOllama(model="qwen2.5:7b", temperature=0)
embeddings = OllamaEmbeddings(model="paraphrase-multilingual:latest")
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
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 8, "fetch_k": 10, "lambda_mult": 0.7})
print(vectorstore._collection.count())
print("--- Base de Datos existente cargada ---")

# CONFIGURACIÓN DE LA TOOL
@tool
def file_search(query: str) -> str:
    """Responde preguntas sobre el contenido del documento."""
    docs = retriever.invoke(query)
    return "\n\n".join([doc.page_content for doc in docs])

agent_rag = create_agent(
    model=llm,
    tools=[file_search],
)

class State(MessagesState):
    customer_name: str
    my_age: int

def node_1(state: State):    
    new_state: State = {}
    if state.get("customer_name") is None:
        new_state["customer_name"] = "Luis Felipe" 
    else:
        new_state["my_age"] = random.randint(18, 30)

    history = state['messages'] 
    last_message = history[-1]  
    ai_message = agent_rag.invoke({"messages": [{"role": "user", "content": last_message.content}]})
    print(ai_message["messages"][-1].content)
    new_state["messages"] = [AIMessage(content=ai_message["messages"][-1].content)]
    return new_state


builder = StateGraph(State)
builder.add_node("node_1", node_1)

builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)

agent = builder.compile()