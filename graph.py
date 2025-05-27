from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from builder import AgentState, get_tools, build_agent, dataframes
from dotenv import load_dotenv

load_dotenv()

agent = build_agent()

def model_call(state: AgentState) -> AgentState:
    response = agent.invoke(state['messages'])

    print("\n\n++++++ STATE +++++++")
    print(state['files_to_process'])
    print(state['files_to_read'])
    print(state['temp_data'])
    print("+++++ EndState +++++\n\n")

    return {"messages": [response]}
    
def should_continue(state: AgentState) -> str: 
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls: 
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

graph.add_edge("our_agent", END)

app = graph.compile()

def print_stream(stream):
    for s in stream:
        message = s['messages'][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

#inputs = {"messages": [("user", "Open Dados Colaboradores.xlsx and say what are the columns the columns.")]}

inputs = {
    "messages": [("user", "Open Exemplo de Resultado.xlsx and say what are their columns.")],
    "files_to_read": ["Exemplo de Resultado.xlsx"],
    "files_to_process": [],
    "temp_data": []
}

print_stream(app.stream(inputs, stream_mode="values"))