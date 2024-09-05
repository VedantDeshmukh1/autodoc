from .analyzer import analyze_code
from .generator import generate_documentation
from .interactive import create_interactive_docs
import logging
import os

__all__ = ['autodoc']

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def autodoc(code_path, output_path, config=None):
    """
    Analyze code and create interactive documentation.
    
    Args:
    code_path (str): Path to the code file or directory
    output_path (str): Path to store the generated documentation
    config (dict, optional): Configuration options for customizing the output
    """
    try:
        logger.info(f"Starting AutoDoc for {code_path}")
        
        if not os.path.exists(code_path):
            raise FileNotFoundError(f"The specified path does not exist: {code_path}")
        
        logger.info(f"Analyzing code at {code_path}")
        analyzed_code = analyze_code(code_path)
        
        logger.info("Generating documentation")
        documentation = generate_documentation(analyzed_code, config)
        
        logger.info(f"Creating interactive docs at {output_path}")
        create_interactive_docs(documentation, output_path, config)
        
        logger.info("Documentation generation complete")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        raise