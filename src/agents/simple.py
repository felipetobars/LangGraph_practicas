from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    customer_name: str
    my_age: int
    courses_taken: List[str]
    logs: List[str]

def node_1(state: State):
    # ESTO ES LA FORMA CORRECTA DE HACERLO, DEVOLVER SOLO LO QUE SE ESTÁ ACTUALIZANDO
    if state.get("customer_name") is None:
        return {
            "customer_name": "Luis Felipe", 
            "courses_taken": ["Python", "Machine Learning"],
            "logs": ["Cliente y cursos base establecidos"]}   
    return {"my_age": 20, 
            "courses_taken": ["Python", "Machine Learning", "LangGraph"],
            "logs": ["Edad actualizada y curso de LangGraph agregado"]
            } 

def node_2(state: State):
    courses = state.get("courses_taken", [])
    logs = state.get("logs", [])
    if "LangGraph" not in courses:
        logs.append("Curso de LangGraph agregado")
        return {"courses_taken": courses + ["LangGraph"], "logs": logs}
    logs.append("No se agregó ningún curso, ya estaba en la lista")
    return {"logs": logs}

builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)

builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_2", END)

agent = builder.compile()