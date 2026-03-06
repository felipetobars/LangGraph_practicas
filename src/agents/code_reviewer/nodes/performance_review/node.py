from langchain_ollama import ChatOllama
from agents.code_reviewer.state import State, PerformanceReview
from agents.code_reviewer.nodes.performance_review.prompt import SYSTEM_PROMPT, USER_PROMPT

llm = ChatOllama(model="qwen2.5-coder:1.5b", temperature=0)

def performance_review(state: State):
    code = state['code']
    messages = [("system", SYSTEM_PROMPT), ("user", USER_PROMPT.format(code=code))]
    llm_with_structured_output = llm.with_structured_output(schema=PerformanceReview)
    schema = llm_with_structured_output.invoke(messages)
    return {'performance_review': schema}