from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, Sequence, TypedDict


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


def build_agent(tools, qtd_tokens, parallel: bool = True) -> ChatGroq:
    agent = ChatGroq(
        model='llama-3.3-70b-versatile',
        temperature=0,
        max_retries=2,
        max_tokens=qtd_tokens,
    ).bind_tools(tools, parallel_tool_calls=parallel)

    return agent


def make_agent_call(tools: list, qtd_tokens: int, parallel: bool = True):
    agent = build_agent(tools, qtd_tokens, parallel)
    
    def agent_call(state: AgentState) -> AgentState:
        response = agent.invoke(state['messages'])
        return {"messages": [response]}
    
    return agent_call