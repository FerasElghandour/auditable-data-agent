"""Load selected notebook definitions without running data acquisition or training."""
import ast
import json
from pathlib import Path

def definitions(names, namespace):
    notebook = json.loads((Path(__file__).parent/'analysis.ipynb').read_text())
    found = set()
    for cell in notebook['cells']:
        if cell['cell_type'] != 'code':
            continue
        tree = ast.parse(''.join(cell['source']))
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
                exec(compile(ast.Module(body=[node], type_ignores=[]), '<notebook definition>', 'exec'), namespace)
                found.add(node.name)
    if found != set(names):
        raise ValueError(f'Missing notebook definitions: {set(names)-found}')
    return namespace
