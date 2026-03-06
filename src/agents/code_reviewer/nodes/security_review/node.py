from langchain_ollama import ChatOllama
from agents.code_reviewer.state import State, SecurityReview
from agents.code_reviewer.nodes.security_review.prompt import SYSTEM_PROMPT, USER_PROMPT

llm = ChatOllama(model="qwen2.5-coder:1.5b", temperature=0)

def security_review(state: State):
    code = state['code']
    messages = [("system", SYSTEM_PROMPT), ("user", USER_PROMPT.format(code=code))]
    llm_with_structured_output = llm.with_structured_output(schema=SecurityReview)
    schema = llm_with_structured_output.invoke(messages)
    return {'security_review': schema}