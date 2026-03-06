from langchain_ollama import ChatOllama
from agents.code_reviewer.nodes.aggregator.prompt import SYSTEM_PROMPT, USER_PROMPT

llm_aggregator = ChatOllama(model="qwen2.5:7b", temperature=0)

def aggregator(state):
    security_review = state['security_review']
    maintainability_review = state['maintainability_review']
    performance_review = state['performance_review']
    messages = [("system", SYSTEM_PROMPT), ("user", USER_PROMPT.format(security_review=security_review, maintainability_review=maintainability_review, performance_review=performance_review))]
    response = llm_aggregator.invoke(messages)
    return {'final_review': response.text}