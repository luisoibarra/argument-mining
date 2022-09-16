from pathlib import Path
from typing import Match
from nbconvert.exporters import PythonExporter
import re

def export_notebook_as_module(notebook_path: Path, new_params: dict = None, new_cap_variables: dict = None, param_dict_name: str='params'):
    """
    Exports a python notebook as an importable .py module. All calls to defined functions
    are commented. The elements of new_params are added to the params ditctionary
    
    notebook_path: Path to the notebook
    new_params: New values to add to the params dictionary in the notebook
    param_dict_name: Name of the parameter dictionary in the notebook
    """
    new_params = {} if new_params is None else new_params
    new_cap_variables = {} if new_cap_variables is None else new_cap_variables
    
    exporter = PythonExporter()
    content, _ = exporter.from_file(notebook_path.open())

    # Commenting function calls
    first_order_function_call_regex = r'^(?P<f_name>[a-zA-Z]\w*)\((?P<any_args>[\'"\w,.\[\] \t]*)\)[ \t]*$'
    regex = re.compile(first_order_function_call_regex, re.MULTILINE)
    def comment(match: Match):
        line = match.group()
        return f"#  {line}"
    result = regex.sub(comment, content)
    
    # Adding/Updating variables
    first_order_variable_def = r'^(?P<v_name>[a-zA-Z_]\w*) *=(?P<value>.*)'
    regex = re.compile(first_order_variable_def, re.MULTILINE)
    def change_value(match: Match):
        match_dict = match.groupdict()
        v_name, v_value = match_dict['v_name'], match_dict['value']
        if v_name in new_cap_variables:
            value = new_cap_variables.pop(v_name)
            return f"{v_name} = {value}"
        return match.group()
    result: str = regex.sub(change_value, result)
    # Add variables that weren't in the file
    first_match = regex.search(result)
    start = first_match.start() if first_match else 0 
    end = first_match.end() if first_match else 0 
    definition_string = "\n".join(f"{name} = {value}" for name, value in new_cap_variables.items())
    match = result[start:end]
    result = result.replace(match, match + "\n" + definition_string, 1)
    
    # Adding new params
    param_dict_regex = fr"^{param_dict_name}[ \t]*=[ \t]*{{"
    regex = re.compile(param_dict_regex, re.MULTILINE)
    match = regex.search(result)
    result = __parse_dictionary(match, result, new_params)
    
    destiny = (notebook_path / ".." / (notebook_path.stem + ".py")).resolve()
    destiny.write_text(result)
    
def __parse_dictionary(definition_start_match, text, new_content_dict):
    initial = definition_start_match.regs[0][0]
    changed = False
    open_br = 0
    for i, c in enumerate(text[initial:], start=initial):
        if c == '{':
            changed = True
            open_br += 1
        elif c == '}':
            changed = True
            open_br -= 1
        assert open_br >= 0, "Invalid Python Program. Curly braces aren't balanced"
        if changed and open_br == 0:
            final = i+1
            break
    else:
        assert False, "Invalid Python Program. Curly braces aren't balanced"

    new_params = "\nnew_params = {\n" + "\n".join([f"    '{key}': {value}," for key, value in new_content_dict.items()]) + "\n}\n"
    new_params += "params.update(new_params)"    

    find_and_replace = text[initial:final]
    text = text.replace(find_and_replace, find_and_replace + new_params)    
    return text
    
if __name__ == "__main__":
    import sys
    # export_notebook_as_module(Path(__file__, "..", "../segmenter/models/segmenter.ipynb").resolve())

    if len(sys.argv) > 1:
        export_notebook_as_module(Path(sys.argv[1]))
    else:
        print("Usage: python3 notebook_utils.py PATH_TO_NOTEBOOK")
