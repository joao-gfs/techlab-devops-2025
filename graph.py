from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from builder import AgentState, get_tools, build_agent, dataframes
from dotenv import load_dotenv

load_dotenv()

agent = build_agent()

def model_call(state: AgentState) -> AgentState:

    system_msg = SystemMessage(content="""
    You are an assistant designed to help with spreadsheet data manipulation.
    Use the tools available to best responde the requests.
    """)

    response = agent.invoke([system_msg] + state['messages'])

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

planilhas = ['Beneficio 1 - Unimed', 'Beneficio 2 - Gympass', 'Dados Colaboradores', 'Ferramenta 1 - Github', 'Ferramenta 2 - Google workspace']

inputs = {
    "messages": [
        HumanMessage(
            content=(
                f"Load the Excel files named '{planilhas[2]}.xlsx' and '{planilhas[1]}' from the input folder. "
                "Identify what columns on each file represent the identity document. "
                "Use the identified columns to merge the files. "
                "Save the merged file with the name 'final.xlsx'."
            )
        )
    ]
}

print_stream(app.stream(inputs, stream_mode="values"))