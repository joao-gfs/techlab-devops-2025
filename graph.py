from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from builder import AgentState, get_tools, build_agent, dataframes

agent = build_agent()

def model_call(state: AgentState) -> AgentState:
    response = agent.invoke(state['messages'])

    return {"messages": [response]}

def should_continue(state: AgentState):
    files_to_read = len(state.get('files_to_read', []))
    files_to_process = len(state.get('files_to_process', []))

    if files_to_process == 0:
        return "end"
    else:
        return "continue"
    
graph = StateGraph(AgentState)
graph.add_node("our_agent", model_call)

tools = get_tools()
tool_node = ToolNode(tools)
graph.add_node("tools", tool_node)

graph.set_entry_point("our_agent")

graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "continue": "tools",
        "end": END
    }
)
graph.add_edge("tools", "our_agent")

app = graph.compile()

def print_stream(stream):
    for s in stream:
        message = s['messages'][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

inputs = {"messages": [("user", "Open Dados Colaboradores.xlsx and list the columns.")]}
print_stream(app.stream(inputs, stream_mode="values"))

print(dataframes)