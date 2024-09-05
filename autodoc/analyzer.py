import ast
import os
import logging
import importlib.util
import re
from radon.complexity import cc_visit
from radon.metrics import h_visit
import math

logger = logging.getLogger(__name__)

try:
    from nltk.corpus import wordnet
    WORDNET_AVAILABLE = True
except LookupError:
    logger.warning("NLTK wordnet data not found. Running without enhanced name inference.")
    WORDNET_AVAILABLE = False
except ImportError:
    logger.warning("NLTK not installed. Running without enhanced name inference.")
    WORDNET_AVAILABLE = False

def analyze_code(code_path):
    """
    Analyze the given code and extract relevant information.
    
    Args:
    code_path (str): Path to the code file or directory
    
    Returns:
    dict: Analyzed code structure
    """
    if os.path.isfile(code_path):
        return {code_path: analyze_file(code_path)}
    elif os.path.isdir(code_path):
        return analyze_directory(code_path)
    else:
        raise ValueError(f"Invalid path: {code_path}")

def analyze_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    try:
        tree = ast.parse(content)
        analyzer = CodeAnalyzer(file_path)
        analyzer.visit(tree)
        return analyzer.result
    except SyntaxError as e:
        logger.error(f"Syntax error in file {file_path}: {str(e)}")
        return {"error": str(e)}

def analyze_directory(dir_path):
    result = {}
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                result[file_path] = analyze_file(file_path)
    return result

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self, file_path):
        self.file_path = file_path
        self.result = {
            'imports': [],
            'classes': {},
            'functions': {},
            'global_variables': [],
            'module_docstring': None,
            'inferred_description': ''
        }
        self.current_class = None
        self.current_function = None
    
    def visit_Module(self, node):
        self.result['module_docstring'] = ast.get_docstring(node)
        self.result['inferred_description'] = self.infer_module_description(node)
        self.generic_visit(node)
    
    def visit_Import(self, node):
        for alias in node.names:
            self.result['imports'].append(alias.name)
    
    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.result['imports'].append(f"{node.module}.{alias.name}")
    
    def visit_ClassDef(self, node):
        class_info = {
            'docstring': ast.get_docstring(node),
            'methods': {},
            'class_variables': [],
            'base_classes': [self.get_base_class_name(base) for base in node.bases],
            'inferred_description': ''
        }
        if not class_info['docstring']:
            class_info['inferred_description'] = self.infer_class_description(node)
        self.current_class = node.name
        self.result['classes'][node.name] = class_info
        self.generic_visit(node)
        self.current_class = None
    
    def visit_FunctionDef(self, node):
        func_info = {
            'docstring': ast.get_docstring(node),
            'args': self.get_function_args(node),
            'returns': self.get_return_annotation(node),
            'decorators': [self.get_decorator_name(d) for d in node.decorator_list],
            'inferred_description': ''
        }
        if not func_info['docstring']:
            func_info['inferred_description'] = self.infer_function_description(node)
        if self.current_class:
            self.result['classes'][self.current_class]['methods'][node.name] = func_info
        else:
            self.result['functions'][node.name] = func_info
        
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = None
    
    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Name):
            if self.current_class:
                self.result['classes'][self.current_class]['class_variables'].append(node.targets[0].id)
            else:
                self.result['global_variables'].append(node.targets[0].id)
    
    def get_function_args(self, node):
        args = []
        for arg in node.args.args:
            arg_info = {'name': arg.arg}
            if arg.annotation:
                arg_info['annotation'] = self.get_annotation(arg.annotation)
            args.append(arg_info)
        if node.args.vararg:
            args.append({'name': f'*{node.args.vararg.arg}'})
        if node.args.kwarg:
            args.append({'name': f'**{node.args.kwarg.arg}'})
        return args
    
    def get_return_annotation(self, node):
        if node.returns:
            return self.get_annotation(node.returns)
        return None
    
    def get_annotation(self, annotation):
        if annotation is None:
            return None
        elif isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            return f'{self.get_annotation(annotation.value)}.{annotation.attr}'
        elif isinstance(annotation, ast.Subscript):
            value = self.get_annotation(annotation.value)
            if isinstance(annotation.slice, ast.Index):
                slice_value = self.get_annotation(annotation.slice.value)
            else:
                slice_value = self.get_annotation(annotation.slice)
            return f'{value}[{slice_value}]'
        elif isinstance(annotation, ast.Constant):
            return repr(annotation.value)
        elif isinstance(annotation, ast.List):
            elements = [self.get_annotation(elt) for elt in annotation.elts]
            return f'[{", ".join(elements)}]'
        elif isinstance(annotation, ast.Tuple):
            elements = [self.get_annotation(elt) for elt in annotation.elts]
            return f'({", ".join(elements)})'
        else:
            return str(annotation)
    
    def get_decorator_name(self, decorator):
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f'{decorator.value.id}.{decorator.attr}'
        return str(decorator)
    
    def get_base_class_name(self, base):
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return f'{base.value.id}.{base.attr}'
        return str(base)
    
    def infer_module_description(self, node):
        classes = [n for n in node.body if isinstance(n, ast.ClassDef)]
        functions = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        imports = [n for n in node.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        global_vars = [n for n in node.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)]
        
        description = f"This module contains:\n"
        description += f"- {len(classes)} classe(s)\n"
        description += f"- {len(functions)} function(s)\n"
        description += f"- {len(imports)} import statement(s)\n"
        description += f"- {len(global_vars)} global variable(s)\n"
        
        if classes:
            description += "\nClasses:\n"
            for cls in classes:
                description += f"- {cls.name}\n"
        
        if functions:
            description += "\nFunctions:\n"
            for func in functions:
                description += f"- {func.name}\n"
        
        # Add complexity analysis
        complexity = self.analyze_complexity(node)
        description += f"\nCode Complexity:\n"
        description += f"- Cyclomatic Complexity: {complexity['cyclomatic']}\n"
        description += f"- Maintainability Index: {complexity['maintainability']}\n"
        
        return description
    
    def infer_class_description(self, node):
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        attributes = [n for n in node.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)]
        
        description = f"This class has {len(methods)} methods and {len(attributes)} attributes.\n"
        
        # Infer class purpose
        class_name = node.name
        purpose = self.infer_purpose_from_name(class_name)
        if purpose:
            description += f"Purpose: {purpose}\n"
        
        # Analyze method names to infer class functionality
        method_names = [m.name for m in methods]
        functionality = self.infer_functionality_from_methods(method_names)
        if functionality:
            description += f"Functionality: {functionality}\n"
        
        return description

    def infer_function_description(self, node):
        args = [arg.arg for arg in node.args.args]
        returns = "a value" if node.returns else "None"
        
        description = f"This function takes {len(args)} arguments and returns {returns}.\n"
        
        # Infer function purpose
        func_name = node.name
        purpose = self.infer_purpose_from_name(func_name)
        if purpose:
            description += f"Purpose: {purpose}\n"
        
        # Analyze function body to infer functionality
        functionality = self.infer_functionality_from_body(node)
        if functionality:
            description += f"Functionality: {functionality}\n"
        
        return description

    def infer_purpose_from_name(self, name):
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+', name)
        purpose = []
        if WORDNET_AVAILABLE:
            for word in words:
                synsets = wordnet.synsets(word.lower())
                if synsets:
                    purpose.append(synsets[0].definition())
        else:
            purpose = words  # Fallback to just using the words themselves
        return ' '.join(purpose) if purpose else None

    def infer_functionality_from_methods(self, method_names):
        functionality = set()
        for name in method_names:
            if name.startswith('get'):
                functionality.add('retrieves data')
            elif name.startswith('set'):
                functionality.add('modifies data')
            elif name.startswith('is') or name.startswith('has'):
                functionality.add('checks conditions')
            elif name.startswith('calc') or name.startswith('compute'):
                functionality.add('performs calculations')
        return ', '.join(functionality) if functionality else None

    def infer_functionality_from_body(self, node):
        functionality = set()
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                if isinstance(n.func, ast.Name):
                    functionality.add(f"calls {n.func.id}")
                elif isinstance(n.func, ast.Attribute):
                    functionality.add(f"uses {n.func.attr}")
        return ', '.join(functionality) if functionality else None

    def analyze_complexity(self, node):
        code = ast.unparse(node)
        complexity = cc_visit(code)
        halstead = h_visit(code)
        
        cyclomatic = sum(c.complexity for c in complexity)
        
        if halstead:
            h_vol = halstead.total.volume
            h_diff = halstead.total.difficulty
            maintainability = (171 - 5.2 * math.log(h_vol) - 0.23 * cyclomatic - 16.2 * math.log(h_diff)) * 100 / 171
        else:
            maintainability = 0
        
        return {
            'cyclomatic': cyclomatic,
            'maintainability': maintainability
        }