from dotenv import load_dotenv
from settings import INPUT_DIR
from graph import run_agent, stream_agent_execution
from functions import list_files_in, load_dataframes_cache, save_all_dataframes
from tools import identifier_tools, renamer_tools, eraser_tools, merger_tools, adder_tools
from langchain_core.messages import SystemMessage, HumanMessage


load_dotenv()

spreadsheets = list_files_in(INPUT_DIR)
load_dataframes_cache(spreadsheets)

inputs_identifier = {
    "messages": [
        SystemMessage(
            content=(
"""
You are an assistant designed to help with spreadsheet manipulation.
Use the tools to best responde the requests.
You will receive the name of the sheets, the columns and a sample of the data. You have to identify on each one:
- Identification columns like name, department in the company or documents (CPF, RG, etc)
- Total spendings or salary. There will be ***only one*** of it in each spreadsheet.

Your response should be a list of spreadsheets with the identified columns. Use the following format:

```
[SPREADSHEET_NAME]
columns to be kept: [list of column names]
```

Example:
```
folha_pagamento.xlsx
columns to be kept: ['nome', 'departamento', 'salario_bruto'], remove all others
```

If you believe a file is the main file (the registry), clearly indicate it:
```
cadastro_funcionarios.xlsx (MAIN FILE)
columns to be kept: ['nome', 'cpf', 'departamento', 'salary'], remove all others
```

Be precise and remove ambiguity in your column selection.
"""
            )
        ),
        HumanMessage(
            content=(f"""
                {spreadsheets}
                """
            )
        )
    ]
}
res_identifier = run_agent("identifier", inputs_identifier, identifier_tools, qtd_tokens=1000)
print("[IDENTIFIER:]")
print(res_identifier)

inputs_eraser = {
    "messages": [
        SystemMessage(
            content=(
"""
You are an assistant specialized in spreadsheet manipulation.

Your task is to clean spreadsheet files by removing all unnecessary columns.

You will receive:
- The name of each spreadsheet.
- The list of columns that must be **kept** (separated into identification and total columns).

Important:

- Be precise. Do not remove any columns that are explicitly listed to be kept.
"""
            )
        ),
        HumanMessage(
            content=(
f"""
{res_identifier}

Instructions:
1. For each file, compare the full list of columns in the spreadsheet with the ones that should be kept.
2. Identify which columns are **not listed** and must therefore be removed.
3. Use the `remove_columns` tool, passing:
- The spreadsheet name.
- A list of the columns to **remove** (i.e., all columns not explicitly listed to keep). Example: ['col1', 'col2', 'col3']
"""
            )
        )
    ]
}

res_eraser = run_agent("eraser", inputs_eraser, eraser_tools, qtd_tokens=1000)
print("\n[ERASER]")
print(res_eraser)

inputs_renamer = {
    "messages": [
        SystemMessage(
            content=("""
You are an assistant specialized in spreadsheet manipulation.

Your task is to rename the columns in spreadsheet files.

You will receive:
- The name of each spreadsheet.
- The list of columns of that the file has.
                """
            )
        ),
        HumanMessage(
            content=(f"""
Instructions:
1. For each file, identify what is the spendings columns. The column choosen is 'Monthly value'.
2. Identify on the name of the file what it is about. Ex: , it is Photoshop
3. Rename the column in the file with the subject identified

example:
input:

Spendings - Photoshop.xlsx
columns to be kept: ['name', 'document', 'Monthly value'], remove all others

You should rename 'Monthly Value' with 'Photoshop'

IMPORTANT: 
ignore "remove all others" in the input.
dont rename column on the (MAIN FILE)
now you do it:
{res_identifier}

                """
            )
        )
    ]
}

res_renamer = run_agent("renamer", inputs_renamer, renamer_tools, qtd_tokens=1000)
print("\n[RENAMER]")
print(res_renamer)


inputs_merger = {
    "messages": [
        SystemMessage(
            content=("""
You're an assistant for spreadsheet merging. Use the tools provided to inspect and merge data into a central file called MAIN FILE
                """
            )
        ),
        HumanMessage(
            content=(
    f"""
Merge Instructions:

1. Merge **all** spreadsheets into the one marked **(MAIN FILE)**.
2. Align rows using **both** a name-like column (e.g., Nome, Assinante) **and** a document-like column (e.g., CPF, Documento).
3. Use **sheet_overview** to check columns if needed.
4. Use **merge_files** to merge. Pass column mappings as shown below:

{res_identifier}

Ensure all merges are done **into the MAIN FILE**, using consistent identifiers to avoid duplicates.
Ensure that all files were merged.

IMPORTANT: 
ignore "remove all others" phrase in the input.
You **MUST** pass the name of the file WITH the extension (.xlsx)

when finished, respond simply the name of the main file
    """
            )
        )
    ]
}

res_merger = stream_agent_execution("merger", inputs_merger, merger_tools, qtd_tokens=None, parallel=False)
print("\n[MERGER]")
print(res_merger)


inputs_final_eraser = {
        "messages": [
            SystemMessage(
                content=(
"""
You are an assistant specialized in spreadsheet manipulation.

Your task is to clean spreadsheet files by removing redundant columns.
"""
                )
            ),
            HumanMessage(
                content=(
f"""
Instructions:
1. You will receive the name of a spreadsheet.
2. Identify columns that have the same type of data
3. Remove the redundant one, leaving only one of each type;
Example: ['name', 'person', 'beneficiary']. if all of them are the names of the subjects, you should remove ['person', 'beneficiary'], leavin the first occurrence, ['name']
You can analyse both the column names and sample data to make your decisions

{res_merger}
"""
                )
            )
        ]
    }

res_final_eraser = run_agent("eraser", inputs_final_eraser, eraser_tools, qtd_tokens=1000)
print("\n[FINAL ERASER]")
print(res_final_eraser)

inputs_adder = {
    "messages": [
        SystemMessage(
            content=(
                """
You're an assistant for spreadsheet column adding. Use the tools provided to inspect and sum data in a file
                """
            )
        ),
        HumanMessage(
            content=(
    f"""
Instructions:

1. Analyse the sample data in the file and identify the monetary columns
2. Sum them using the 'add_columns' tools
You **MUST** pass the name of the file WITH the extension (.xlsx)
You dont need to see the result, just sum and finish

File: {res_merger}
    """
            )
        )
    ]
}

res_adder = stream_agent_execution("adder", inputs_adder, adder_tools, qtd_tokens=750)
print("\n[ADDER]")
print(res_adder)

save_all_dataframes()