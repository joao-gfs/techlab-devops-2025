from typing import Annotated, Sequence, TypedDict
from langchain_groq import ChatGroq
from tools.data_manipulation import add_two_columns, get_columns, open_excel


tools = [add_two_columns, get_columns, open_excel]




