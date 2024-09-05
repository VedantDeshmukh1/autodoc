# AutoDoc 📚✨

AutoDoc is a powerful Python package that automatically generates interactive documentation for your Python code. It analyzes your code structure, extracts relevant information, and creates user-friendly HTML documentation, making it easier for developers to understand and maintain their projects.

## ✨ Features

- 🔍 Automatic code analysis of Python files and directories
- 🌐 Generation of interactive HTML documentation
- 🧠 Inference of module, class, and function descriptions when docstrings are not present
- 🎨 Syntax highlighting for source code
- 📝 Support for type annotations
- 🧭 Easy-to-navigate documentation structure
- 📱 Responsive design for various screen sizes
- 🧩 Handling of complex code structures, including nested classes and functions
- 📚 Support for module-level, class-level, and function-level documentation

## 🚀 Installation

You can install AutoDoc using pip:


## 🔧 Usage

Using AutoDoc is simple. Here's a quick example:

python
```
from autodoc import generate_docs
Generate documentation for a single file
generate_docs("path/to/your/file.py", output_dir="docs")
Generate documentation for an entire directory
generate_docs("path/to/your/project", output_dir="docs", recursive=True)
```

## 📖 Example

Let's say you have a Python file called `calculator.py`:


python
class Calculator:
def add(self, a: float, b: float) -> float:
"""Add two numbers."""
return a + b
def subtract(self, a: float, b: float) -> float:
"""Subtract b from a."""
return a - b
def multiply(self, a: float, b: float) -> float:
return a b # No docstring, AutoDoc will infer a description


Running AutoDoc on this file:

python
```
from autodoc import generate_docs
generate_docs("calculator.py", output_dir="docs")
```
Ask
Copy
Apply

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

## 📄 License

AutoDoc is released under the MIT License. See the [LICENSE](LICENSE) file for more details.

## 🙏 Acknowledgements

Special thanks to all the contributors who have helped make AutoDoc better!

---

Made with ❤️ by the AutoDoc team
