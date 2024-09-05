import os
import json
import logging
import shutil
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import markdown2
import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import ast

logger = logging.getLogger(__name__)

def create_interactive_docs(documentation, output_path, config=None):
    env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
    template = env.get_template('template.html')
    
    os.makedirs(output_path, exist_ok=True)
    
    for file_path, file_doc in documentation.items():
        output_file = os.path.join(output_path, f"{os.path.basename(file_path)}.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            content = template.render(
                file_path=file_path,
                module_docstring=markdown2.markdown(file_doc.get('module_docstring') or ''),
                inferred_description=format_inferred_description(file_doc.get('inferred_description', '')),
                imports=generate_imports_html(file_doc['imports']),
                classes=generate_class_html(file_doc['classes']),
                functions=generate_function_html(file_doc['functions']),
                global_variables=generate_global_variables_html(file_doc['global_variables']),
                error=file_doc.get('error'),
                source_code=highlight_code(get_source_code(file_path), 'python')
            )
            f.write(content)
        
        logger.info(f"Generated documentation for {file_path} at {output_file}")
    
    # Generate index.html
    index_template = env.get_template('index.html')
    index_path = os.path.join(output_path, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_template.render(
            files=[os.path.relpath(file, start=os.path.dirname(output_path)) for file in documentation.keys()],
            current_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
    
    logger.info(f"Generated index at {index_path}")
    
    # Copy static files
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    for item in os.listdir(static_dir):
        src = os.path.join(static_dir, item)
        dst = os.path.join(output_path, item)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
    
    logger.info("Copied static files")

def format_inferred_description(description):
    lines = description.split('\n')
    formatted_lines = []
    for line in lines:
        if line.startswith('-'):
            formatted_lines.append(f"<li>{line[1:].strip()}</li>")
        elif line.endswith(':'):
            formatted_lines.append(f"<h4>{line}</h4><ul>")
        elif line.strip() == '':
            formatted_lines.append("</ul>")
        else:
            formatted_lines.append(f"<p>{line}</p>")
    return ''.join(formatted_lines)

def generate_imports_html(imports):
    if not imports:
        return "<p>No imports found.</p>"
    html = "<ul class='imports-list'>"
    for imp in imports:
        html += f"<li><code>{imp}</code></li>"
    html += "</ul>"
    return html

def generate_class_html(classes):
    html = ""
    for class_name, class_info in classes.items():
        html += f"<div class='class' id='class-{class_name}'>"
        html += f"<h3>class {class_name}"
        if class_info.get('base_classes'):
            html += f"({', '.join(class_info['base_classes'])})"
        html += "</h3>"
        
        if class_info.get('docstring'):
            html += f"<div class='docstring'>{markdown2.markdown(class_info['docstring'])}</div>"
        elif class_info.get('inferred_description'):
            html += f"<p class='inferred'><em>{class_info['inferred_description']}</em></p>"
        
        if class_info.get('class_variables'):
            html += "<h4>Class Variables:</h4>"
            html += "<ul>"
            for var in class_info['class_variables']:
                html += f"<li>{var}</li>"
            html += "</ul>"
        
        html += "<h4>Methods:</h4>"
        html += generate_function_html(class_info.get('methods', {}), is_method=True)
        
        html += "</div>"
    return html

def generate_function_html(functions, is_method=False):
    html = ""
    for func_name, func_info in functions.items():
        html += f"<div class='{'method' if is_method else 'function'}' id='{'method' if is_method else 'function'}-{func_name}'>"
        html += f"<h4>{func_name}({generate_function_signature(func_info)})</h4>"
        
        if func_info['docstring']:
            html += f"<div class='docstring'>{markdown2.markdown(func_info['docstring'])}</div>"
        elif func_info['inferred_description']:
            html += f"<p class='inferred'><em>{func_info['inferred_description']}</em></p>"
        
        html += "<h5>Arguments:</h5><ul>"
        for arg in func_info['args']:
            html += f"<li><code>{arg['name']}"
            if 'annotation' in arg:
                html += f": {arg['annotation']}"
            html += "</code></li>"
        html += "</ul>"
        
        if func_info['returns']:
            html += f"<p><strong>Returns:</strong> <code>{func_info['returns']}</code></p>"
        
        if func_info['decorators']:
            html += f"<p><strong>Decorators:</strong> {', '.join(func_info['decorators'])}</p>"
        
        html += "</div>"
    return html

def generate_function_signature(func_info):
    args = []
    for arg in func_info['args']:
        arg_str = arg['name']
        if 'annotation' in arg:
            arg_str += f": {arg['annotation']}"
        args.append(arg_str)
    return ", ".join(args)

def generate_global_variables_html(global_variables):
    if not global_variables:
        return "<p>No global variables found.</p>"
    html = "<ul class='global-variables-list'>"
    for var in global_variables:
        html += f"<li><code>{var}</code></li>"
    html += "</ul>"
    return html

def highlight_code(code, language):
    lexer = get_lexer_by_name(language)
    formatter = HtmlFormatter(style='friendly', linenos=True, cssclass="source")
    return pygments.highlight(code, lexer, formatter)

def get_source_code(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()