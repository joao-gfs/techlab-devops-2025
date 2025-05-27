from typing_extensions import Annotated, Sequence, TypedDict, List, Dict
from langchain_core.messages import BaseMessage
from langchain_core.messages import ToolMessage
from langchain_core.messages import SystemMessage
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langchain_groq import ChatGroq

import os
import pandas as pd
from langchain.tools import tool
from settings import INPUT_DIR, OUTPUT_DIR

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    files_to_read: List[str]
    files_to_process: List[str]

def get_tools() -> List[tool]:
    return [load_excel, set_index]


#llama3-8b-8192
def build_agent() -> ChatGroq:
    tools = get_tools()

    agent = ChatGroq(
        model='llama3-70b-8192',
        temperature=0
    ).bind_tools(tools)

    return agent

@tool
def add_file_to_read(state: AgentState, filename: str):
    """Adds a file to the list to read"""

    state['files_to_read'].append(filename)

    return state

@tool
def load_excel(state: AgentState, filename: str) -> AgentState:
    """reads an excel file from the filename and returns a dictionary representing it"""

    path = os.path.join(INPUT_DIR, filename)
    df = pd.read_excel(path)

    state['data_dicts'][filename] = df.to_dict()
    state['files_to_read'].remove(filename)
    state['files_to_process'].append(filename)

    return state

@tool
def set_index(state: AgentState, filename: str, index_col: str) -> AgentState:
    """creates the index of the file dict with a column of it"""
    
    df = pd.DataFrame(state['file_dicts'][filename])

    df.set_index(index_col, inplace=True)
    
    state['file_dicts'][filename] = df.to_dict()
    state['files_to_process'].remove(filename)

    return state