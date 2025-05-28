from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from builder import AgentState, get_tools, build_agent, dataframes
from dotenv import load_dotenv

load_dotenv()

agent = build_agent()

def model_call(state: AgentState) -> AgentState:

    system_msg = SystemMessage(content="""
    You are an assistant designed to classify spreadsheets containing information about employee benefits or work tools.

    Your task is:
    1. Analyze the spreadsheet filename and column names.
    2. Try to identify the **name of the product or company**
    3. If you cannot identify the product or company, respond with a short **description of the type of benefit or tool** (e.g., plano de saúde, academia, email).
    4. Respond in **Portuguese**, using **one word or a short phrase** only — no explanations, no sentences.
    5. Dont forget to use the columns to answer.

    Examples:
    - If the spreadsheet have infos about salary or other type of work payment: respond `salário`
    - If the spreadsheet is clearly about Blob: respond `Blob`
    - If it's a gym benefit and the name is AllGym: respond `AllGym`
    - If the spreadsheet is about a health plan but the provider is unknown: respond `plano de saúde`
    - If it's a tool like Microsoft 365: respond `Microsoft 365`
    - If unclear, choose the most representative type of benefit/tool based on the available data.

    DO NOT respond with explanations or complete sentences — only a **concise Portuguese label**.
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
    "messages": [(
        "user",
        f"Load the Excel file named '{planilhas[4]}.xlsx' from the input folder. "
        "Then say in Portuguese, using only one word or a short expression, what benefit or provider the spreadsheet refers to."
    )]
}

print_stream(app.stream(inputs, stream_mode="values"))