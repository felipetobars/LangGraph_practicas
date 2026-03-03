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
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()
import warnings
warnings.filterwarnings("ignore")

# PATHS DE LA BASE DE DATOS VECTORIAL Y EL PDF DE EJEMPLO
DB_DIR = "notebooks/chroma_db_rag"
PDF_PATH = './Mobile_Site_Speed_Playbook.pdf'

# CONFIGURACIÓN DEL LLM CON OLLAMA Y MODELO DE EMBEDDINGS
llm = ChatOllama(model="qwen2.5:7b", temperature=0)
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
# print(vectorstore._collection.count())
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

# DEFINICIÓN DEL ESTADO DE LA APLICACIÓN CON LANGGRAPH

class State(MessagesState):
    customer_name: str
    phone: str
    my_age: int

# ESTRUCTURACIÓN DE LA RESPUESTA DEL MODELO CON GEMINI

class ContactInfo(BaseModel):
    "Contact information for a person."

    name: str = Field(description="The name of the person")
    email: str = Field(description="The email address of the person")
    phone: str = Field(description="The phone number of the person")
    tone: int = Field(description="The tone of the conversation (0 is informal, 100 is formal)", ge=0, le=100)
    age: int = Field(description="The age of the person", ge=1, le=120)
    sentiment: str = Field(description="The sentiment of the conversation, e.g., positive, negative, neutral.")

llm_with_structured_output = ChatGoogleGenerativeAI(model='gemini-2.5-flash-lite', google_api_key=os.getenv("GOOGLE_API_KEY"), temperature=0) 
llm_with_structured_output = llm_with_structured_output.with_structured_output(schema=ContactInfo)

# NODO EXTRACTOR: EXTRAER INFORMACIÓN DE LA CONVERSACIÓN

def extractor(state: State):
    history = state['messages']
    customer_name = state.get("customer_name", None)
    new_state: State = {}
    if customer_name is None or len(history) > 10:
        schema = llm_with_structured_output.invoke(history)
        new_state["customer_name"] = schema.name
        new_state["phone"] = schema.phone
        new_state["my_age"] = schema.age
    return new_state

# NODO CONVERSATION: RESPONDER A LA CONVERSACIÓN Y EXTRAER INFORMACIÓN DEL DOCUMENTO SI ES NECESARIO

def conversation(state: State):    
    new_state: State = {}

    history = state['messages'] 
    last_message = history[-1]  
    customer_name = state.get("customer_name", "unknown customer")
    system_message = f"You are a helpfull assistant that can answer questions about the customer {customer_name}"
    ai_message = agent_rag.invoke({"messages": [{"role": "system", "content": system_message}, {"role": "user", "content": last_message.content}]})
    print(ai_message["messages"][-1].content)
    new_state["messages"] = [AIMessage(content=ai_message["messages"][-1].content)]
    return new_state

# CONSTRUCCIÓN DEL GRAFO DE ESTADOS Y COMPILACIÓN DEL AGENTE

builder = StateGraph(State)
builder.add_node("conversation", conversation)
builder.add_node("extractor", extractor)

builder.add_edge(START, "extractor")
builder.add_edge("extractor", "conversation")
builder.add_edge("conversation", END)

agent = builder.compile()