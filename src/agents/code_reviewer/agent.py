from langgraph.graph import StateGraph, START, END
from agents.code_reviewer.state import State
from agents.code_reviewer.nodes.security_review.node import security_review
from agents.code_reviewer.nodes.maintainability_review.node import maintainability_review
from agents.code_reviewer.nodes.performance_review.node import performance_review
from agents.code_reviewer.nodes.aggregator.node import aggregator

# Define the StateGraph
builder = StateGraph(State)
builder.add_node('security_review', security_review)
builder.add_node('maintainability_review', maintainability_review)
builder.add_node('performance_review', performance_review)
builder.add_node('aggregator', aggregator)

builder.add_edge(START, 'security_review')
builder.add_edge(START, 'maintainability_review')
builder.add_edge(START, 'performance_review')
builder.add_edge('security_review', 'aggregator')
builder.add_edge('maintainability_review', 'aggregator')
builder.add_edge('performance_review', 'aggregator')
builder.add_edge('aggregator', END)

agent = builder.compile()