from agents.support.state import State
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from agents.support.nodes.conversation.tools import file_search
from langchain_core.messages import AIMessage
from agents.support.nodes.conversation.prompt import SYSTEM_PROMPT

llm = ChatOllama(model="qwen2.5:7b", temperature=0)


agent_rag = create_agent(
    model=llm,
    tools=[file_search],
)

def conversation(state: State):    
    new_state: State = {}

    history = state['messages'] 
    last_message = history[-1]  
    customer_name = state.get("customer_name", "unknown customer")
    ai_message = agent_rag.invoke({"messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": last_message.content}]})

    # Guarda el contenido de todos los mensajes generados por el agente
    ai_contents = [msg.content for msg in ai_message["messages"]]
    print(ai_contents)
    new_state["messages"] = [AIMessage(content=content) for content in ai_contents]
    return new_state