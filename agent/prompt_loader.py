"""
Prompt Loader - Loads and manages prompt templates from YAML files
"""

from pathlib import Path
from typing import Optional
from langchain_core.prompts import PromptTemplate
import yaml
from agent.logger_config import get_logger

logger = get_logger(__name__)


class PromptLoader:
    """Loads prompt templates from YAML files"""
    
    def __init__(self, prompt_dir: Optional[Path] = None):
        """
        Initialize the prompt loader
        
        Args:
            prompt_dir: Directory containing prompt files (defaults to agent/prompt/)
        """
        if prompt_dir is None:
            prompt_dir = Path(__file__).parent / "prompt"
        self.prompt_dir = Path(prompt_dir)
    
    def load_prompt(self, prompt_name: str) -> PromptTemplate:
        """
        Load a prompt template from a YAML file
        
        Args:
            prompt_name: Name of the prompt file (with or without .yaml extension)
        
        Returns:
            PromptTemplate instance
        
        Raises:
            FileNotFoundError: If the prompt file doesn't exist
        """
        # Add .yaml extension if not present
        if not prompt_name.endswith(('.yaml', '.yml')):
            prompt_name += '.yaml'
        
        prompt_file = self.prompt_dir / prompt_name
        
        if not prompt_file.exists():
            logger.error(f"Prompt file not found: {prompt_file}")
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        
        logger.debug(f"Loading prompt from: {prompt_file}")
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
        
        # Extract input variables from the template (look for {variable} patterns)
        import re
        input_vars = set(re.findall(r'\{(\w+)\}', prompt_content))
        logger.debug(f"Found input variables: {input_vars}")
        
        # Create LangChain PromptTemplate
        template = PromptTemplate(
            input_variables=list(input_vars),
            template=prompt_content
        )
        
        logger.info(f"Successfully loaded prompt: {prompt_name}")
        return template

