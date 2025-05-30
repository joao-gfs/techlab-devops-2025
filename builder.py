from langchain.tools import tool
from settings import INPUT_DIR, OUTPUT_DIR
from typing_extensions import Annotated, Sequence, TypedDict, List
from langchain_core.messages import BaseMessage
from langchain_core.messages import ToolMessage
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def build_agent(tools) -> ChatGroq:
    agent = ChatGroq(
        model='llama3-70b-8192',
        temperature=0
    ).bind_tools(tools)

    return agent
