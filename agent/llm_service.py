"""
LLM Service - Provides LangChain-based LLM services
"""

import os
from typing import Optional
from pathlib import Path
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from agent.logger_config import get_logger

logger = get_logger(__name__)

# Load .env file from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)


class LLMService:
    """Service for interacting with LLMs using LangChain"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the LLM service
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name (defaults to OPENAI_MODEL env var or 'gpt-4o')
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4o')
        
        if not self.api_key:
            logger.error("LLM service initialized without API key")
            raise ValueError(
                "OpenAI API key not configured. "
                "Set OPENAI_API_KEY environment variable or create a .env file."
            )
        
        # Initialize LangChain LLM
        logger.debug(f"Initializing LLM service with model: {self.model}")
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=0.7,
            openai_api_key=self.api_key
        )
    
    def invoke(self, prompt: str, images: Optional[list] = None) -> str:
        """
        Invoke the LLM with a prompt (synchronous)
        
        Args:
            prompt: The prompt to send to the LLM
            images: Optional list of base64-encoded images (with data URI prefix)
        
        Returns:
            LLM response content as string
        """
        if images:
            # Use vision model with images
            logger.debug(f"Invoking LLM with {len(images)} image(s)")
            from langchain_core.messages import HumanMessage
            
            content = [{"type": "text", "text": prompt}]
            for img in images:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": img}
                })
            
            message = HumanMessage(content=content)
            response = self.llm.invoke([message])
        else:
            logger.debug(f"Invoking LLM with text prompt (length: {len(prompt)})")
            response = self.llm.invoke(prompt)
        
        result = response.content if hasattr(response, 'content') else str(response)
        logger.debug(f"LLM response received (length: {len(result)})")
        return result
    
    async def ainvoke(self, prompt: str, images: Optional[list] = None) -> str:
        """
        Invoke the LLM with a prompt (asynchronous)
        
        Args:
            prompt: The prompt to send to the LLM
            images: Optional list of base64-encoded images (with data URI prefix)
        
        Returns:
            LLM response content as string
        """
        if images:
            # Use vision model with images
            logger.debug(f"Invoking LLM (async) with {len(images)} image(s)")
            from langchain_core.messages import HumanMessage
            
            content = [{"type": "text", "text": prompt}]
            for img in images:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": img}
                })
            
            message = HumanMessage(content=content)
            response = await self.llm.ainvoke([message])
        else:
            logger.debug(f"Invoking LLM (async) with text prompt (length: {len(prompt)})")
            response = await self.llm.ainvoke(prompt)
        
        result = response.content if hasattr(response, 'content') else str(response)
        logger.debug(f"LLM response received (async, length: {len(result)})")
        return result

