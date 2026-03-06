from langchain_ollama import ChatOllama
from agents.code_reviewer.state import State, MaintainabilityReview
from agents.code_reviewer.nodes.maintainability_review.prompt import SYSTEM_PROMPT, USER_PROMPT

llm = ChatOllama(model="qwen2.5-coder:1.5b", temperature=0)

def maintainability_review(state: State):
    code = state['code']
    messages = [("system", SYSTEM_PROMPT), ("user", USER_PROMPT.format(code=code))]
    llm_with_structured_output = llm.with_structured_output(schema=MaintainabilityReview)
    schema = llm_with_structured_output.invoke(messages)
    return {'maintainability_review': schema}