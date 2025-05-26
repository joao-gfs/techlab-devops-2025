from typing import Annotated, Sequence, TypedDict, Any
from langchain_core.messages import BaseMessage
from langchain_core.messages import ToolMessage
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from tools import add_two_columns, get_columns, load_excel

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    loaded_files: dict[str, str]
    current_df_key: str
    available_columns: dict[str, list[str]]
    last_operation: str
    temp_results: dict[str, Any]

def build_agent() -> ChatGroq:
    tools = [add_two_columns, get_columns, load_excel]

    agent = ChatGroq(
        model='llama3-70b-8192',
    ).bind_tools(tools)

