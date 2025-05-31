import pandas as pd
import os
from settings import INPUT_DIR, OUTPUT_DIR
from pprint import pprint
from tools import dataframes

def list_files_in(folder: str) -> list[str]:
    return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

def load_dataframes_cache(filenames, input_dir: str=INPUT_DIR):
    for filename in filenames:
        path = os.path.join(input_dir, filename)
        df = pd.read_excel(path)
        dataframes[filename] = df


def save_all_dataframes(output_dir: str = OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    for name, df in dataframes.items():
        base_name = os.path.splitext(name)[0]
        output_path = os.path.join(output_dir, f"{base_name}.xlsx")
        df.to_excel(output_path, index=False)


def print_stream(stream):
    for s in stream:
        message = s['messages'][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()