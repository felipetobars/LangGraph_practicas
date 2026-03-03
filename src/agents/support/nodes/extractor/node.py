import os
from agents.support.state import State
from agents.support.nodes.extractor.prompt import SYSTEM_PROMPT
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()


class ContactInfo(BaseModel):
    "Contact information for a person."

    name: str = Field(description="The name of the person")
    email: str = Field(description="The email address of the person")
    phone: str = Field(description="The phone number of the person")
    tone: int = Field(description="The tone of the conversation (0 is informal, 100 is formal)", ge=0, le=100)
    age: int = Field(description="The age of the person", ge=1, le=120)
    sentiment: str = Field(description="The sentiment of the conversation, e.g., positive, negative, neutral.")

llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash-lite', google_api_key=os.getenv("GOOGLE_API_KEY"), temperature=0) 
llm_with_structured_output = llm.with_structured_output(schema=ContactInfo)

def extractor(state: State):
    history = state['messages']
    customer_name = state.get("customer_name", None)
    new_state: State = {}
    if customer_name is None or len(history) > 10:
        schema = llm_with_structured_output.invoke([("system", SYSTEM_PROMPT)] + history)
        new_state["customer_name"] = schema.name
        new_state["phone"] = schema.phone
        new_state["my_age"] = schema.age
    return new_state