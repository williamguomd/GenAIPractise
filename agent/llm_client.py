"""
LLM Client - Handles communication with LLM APIs
"""

import os
from pathlib import Path
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load .env file from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)


class LLMClient:
    """Client for interacting with LLM APIs"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.client = None
        
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
    
    async def chat(self, user_message: str, system_message: Optional[str] = None) -> str:
        """Send a chat message to the LLM and get a response"""
        if not self.client:
            raise ValueError(
                "OpenAI API key not configured. "
                "Set OPENAI_API_KEY environment variable or create a .env file."
            )
        
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": user_message})
        
        # Note: OpenAI client is synchronous, but we're using async for consistency
        # In production, you might want to use async OpenAI client
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )
        
        return response.choices[0].message.content

