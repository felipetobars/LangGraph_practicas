from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from agents.support.nodes.booking.tools import tools
from agents.support.nodes.booking.prompt import prompt_template

llm = ChatOllama(model="qwen2.5:7b", temperature=0)

booking_node = create_agent(
    model=llm,
    tools=tools,
    system_prompt=prompt_template.format(),
)