import os
from agents.support.state import State
from agents.support.routes.intent.prompt import SYSTEM_PROMPT
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from typing import Literal

class RouteIntent(BaseModel):
    step: Literal["conversation", "booking"] = Field('conversation', description="The next step in the routing process")

llm = ChatOllama(model="qwen2.5:7b", temperature=0)
llm_with_structured_output = llm.with_structured_output(schema=RouteIntent)
 

def intent_route(state: State) -> Literal["conversation", "booking"]:
    history = state["messages"]
    schema = llm_with_structured_output.invoke([("system", SYSTEM_PROMPT)] + history)
    if schema.step is not None:
        return schema.step
    return'conversation'