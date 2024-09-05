import logging
import re

logger = logging.getLogger(__name__)

def generate_documentation(analyzed_code, config=None):
    """
    Generate documentation from analyzed code.
    
    Args:
    analyzed_code (dict): Analyzed code structure
    config (dict, optional): Configuration options for customizing the output
    
    Returns:
    dict: Generated documentation
    """
    documentation = {}
    
    for file_path, file_info in analyzed_code.items():
        if isinstance(file_info, dict) and 'error' in file_info:
            documentation[file_path] = {'error': file_info['error']}
        elif isinstance(file_info, dict):
            documentation[file_path] = {
                'module_docstring': file_info.get('module_docstring', ''),
                'inferred_description': file_info.get('inferred_description', ''),
                'imports': generate_imports_doc(file_info.get('imports', [])),
                'classes': file_info.get('classes', {}),  # Keep as a dictionary
                'functions': file_info.get('functions', {}),  # Keep as a dictionary
                'global_variables': generate_global_variables_doc(file_info.get('global_variables', []))
            }
        else:
            documentation[file_path] = {'error': f"Unexpected file_info type: {type(file_info)}"}
    
    return documentation

def generate_imports_doc(imports):
    return "\n".join([f"import {imp}" for imp in imports])

def generate_classes_doc(classes):
    doc = ""
    for class_name, class_info in classes.items():
        doc += f"class {class_name}"
        if class_info['base_classes']:
            doc += f"({', '.join(class_info['base_classes'])})"
        doc += ":\n"
        if class_info['docstring']:
            doc += f"    \"\"\"{class_info['docstring']}\"\"\"\n\n"
        elif class_info['inferred_description']:
            doc += f"    # {class_info['inferred_description']}\n\n"
        
        for var in class_info['class_variables']:
            doc += f"    {var}\n"
        
        for method_name, method_info in class_info['methods'].items():
            doc += generate_function_doc(method_name, method_info, indentation=4)
        
        doc += "\n"
    return doc

def generate_functions_doc(functions):
    doc = ""
    for func_name, func_info in functions.items():
        doc += generate_function_doc(func_name, func_info)
    return doc

def generate_function_doc(func_name, func_info, indentation=0):
    indent = " " * indentation
    doc = f"{indent}def {func_name}("
    args = []
    for arg in func_info['args']:
        arg_str = arg['name']
        if 'annotation' in arg:
            arg_str += f": {arg['annotation']}"
        args.append(arg_str)
    doc += ", ".join(args)
    doc += ")"
    if func_info['returns']:
        doc += f" -> {func_info['returns']}"
    doc += ":\n"
    if func_info['docstring']:
        doc += f"{indent}    \"\"\"{func_info['docstring']}\"\"\"\n"
    elif func_info['inferred_description']:
        doc += f"{indent}    # {func_info['inferred_description']}\n"
    doc += "\n"
    return doc

def generate_global_variables_doc(global_variables):
    return "\n".join([f"{var}" for var in global_variables])