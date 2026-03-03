import random
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

gemma3_llm = ChatOllama(model="qwen2.5:7b", temperature=0)


########################################## Clase 4: con TypedDict
# class State(TypedDict):
#     customer_name: str
#     my_age: int
#     courses_taken: List[str]
#     logs: List[str]

# def node_1(state: State):
#     # ESTO ES LA FORMA CORRECTA DE HACERLO, DEVOLVER SOLO LO QUE SE ESTÁ ACTUALIZANDO
#     if state.get("customer_name") is None:
#         return {
#             "customer_name": "Luis Felipe", 
#             "courses_taken": ["Python", "Machine Learning"],
#             "logs": ["Cliente y cursos base establecidos"]}   
#     return {"my_age": 20, 
#             "courses_taken": ["Python", "Machine Learning", "LangGraph"],
#             "logs": ["Edad actualizada y curso de LangGraph agregado"]
#             } 

# def node_2(state: State):
#     courses = state.get("courses_taken", [])
#     logs = state.get("logs", [])
#     if "LangGraph" not in courses:
#         logs.append("Curso de LangGraph agregado")
#         return {"courses_taken": courses + ["LangGraph"], "logs": logs}
#     logs.append("No se agregó ningún curso, ya estaba en la lista")
#     return {"logs": logs}

########################################## Clase 5: con MessagesState
# class State(MessagesState):
#     customer_name: str
#     my_age: int
#     courses_taken: List[str]
#     logs: List[str]

# def node_1(state: State):
#     # ESTO ES LA FORMA CORRECTA DE HACERLO, DEVOLVER SOLO LO QUE SE ESTÁ ACTUALIZANDO
#     history = state.get("messages", [])
#     if state.get("customer_name") is None:
#         ai_msg = AIMessage(content="Cliente no establecido, estableciendo cliente y cursos base")
#         return {"customer_name": "Luis Felipe", 
#                 "courses_taken": ["Python", "Machine Learning"],
#                 "logs": ["Cliente y cursos base establecidos"],
#                 "messages": history + [ai_msg]
#                 }
#     else:
#         ai_msg = AIMessage(content="Cliente ya establecido, actualizando edad y cursos")
#         return {"my_age": 20, 
#                 "courses_taken": ["Python", "Machine Learning", "LangGraph"],
#                 "logs": ["Edad actualizada y curso de LangGraph agregado"],
#                 "messages": history + [ai_msg]
#                 } 

# def node_2(state: State):
#     courses = state.get("courses_taken", [])
#     logs = state.get("logs", [])
#     history = state.get("messages", [])
#     if "LangGraph" not in courses:
#         logs.append("Curso de LangGraph agregado")
#         ai_msg = AIMessage(content="Curso de LangGraph agregado a la lista de cursos")
#         return {"courses_taken": courses + ["LangGraph"], "logs": logs, "messages": history + [ai_msg]}
#     logs.append("No se agregó ningún curso, ya estaba en la lista")
#     ai_msg = AIMessage(content="No se agregó ningún curso, ya estaba en la lista")
#     return {"logs": logs, "messages": history + [ai_msg]}

########################################## Clase 7: Implementando un LLM
# from langchain_google_genai import ChatGoogleGenerativeAI
# import os
# from dotenv import load_dotenv

# load_dotenv()
# gemini25_flash_lite_llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash-lite', google_api_key=os.getenv("GOOGLE_API_KEY"), temperature=0) 

class State(MessagesState):
    customer_name: str
    my_age: int
    courses_taken: List[str]

def node_1(state: State):    
    new_state: State = {}
    if state.get("customer_name") is None:
        new_state["customer_name"] = "Luis Felipe" 
        new_state["courses_taken"] = ["Python", "Machine Learning"]
    else:
        new_state["my_age"] = random.randint(18, 30)
        new_state["courses_taken"] = ["Python", "Machine Learning", "LangGraph"]

    human_msg = HumanMessage(content=f"estado anterior-{state} nuevo estado - {new_state} (extrae la llave y valor, no lo muestres como diccionario)")
    system_prompt = SystemMessage(content="Eres un asistente que usa la información de los estados para entregar solamente una TABLA con la información actualizada y dejar celdas vacías si no hay info (customer_name, courses_taken, my_age).")   
    new_state["messages"] = [system_prompt, human_msg]
    
    ai_message = gemma3_llm.invoke(new_state["messages"])
    new_state["messages"] = [system_prompt, human_msg, ai_message]
    print(new_state)
    return new_state


builder = StateGraph(State)
builder.add_node("node_1", node_1)

builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)

agent = builder.compile()
