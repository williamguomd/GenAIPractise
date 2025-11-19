"""
Video Evaluation Module - Evaluates tennis videos using LLM
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from agent.prompt_loader import PromptLoader
from agent.llm_service import LLMService
from agent.video_processor import VideoProcessor
from agent.logger_config import get_logger

logger = get_logger(__name__)


class VideoEvaluator:
    """Evaluates tennis videos using LLM with structured prompts"""
    
    def __init__(self, prompt_name: str = "tennis_evaluation_prompt", api_key: Optional[str] = None, model: Optional[str] = None, max_frames: int = 10):
        """
        Initialize the video evaluator
        
        Args:
            prompt_name: Name of the prompt file to load (defaults to "tennis_evaluation_prompt")
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name (defaults to OPENAI_MODEL env var or 'gpt-4o')
            max_frames: Maximum number of frames to extract from video (defaults to 10)
        """
        self.llm_service = LLMService(api_key=api_key, model=model)
        self.prompt_loader = PromptLoader()
        self.prompt_template = self.prompt_loader.load_prompt(prompt_name)
        self.video_processor = VideoProcessor(max_frames=max_frames)
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """
        Parse JSON response from LLM
        
        Args:
            content: Raw response content from LLM
        
        Returns:
            Parsed evaluation dictionary
        """
        try:
            # Extract JSON from response (might be wrapped in markdown code blocks)
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                # Try to find JSON object in the response
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                json_str = content[json_start:json_end]
            
            evaluation = json.loads(json_str)
            
            # Normalize keys
            normalized = {}
            for key, value in evaluation.items():
                if "footwork" in key.lower() or "movement" in key.lower():
                    normalized["footwork_movement"] = value
                elif "stroke" in key.lower() or "mechanics" in key.lower():
                    normalized["stroke_mechanics"] = value
                elif "shot" in key.lower() or "quality" in key.lower():
                    normalized["shot_quality"] = value
                elif "overall" in key.lower() or "performance" in key.lower():
                    normalized["overall_performance"] = value
                else:
                    normalized[key] = value
            
            return normalized
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response content: {content[:500]}...")
            return {
                "raw_response": content,
                "error": f"Failed to parse JSON: {str(e)}",
                "stroke_mechanics": "",
                "footwork_movement": "",
                "shot_quality": "",
                "overall_performance": ""
            }
    
    def evaluate(self, video_input: str | Path) -> Dict[str, Any]:
        """
        Evaluate a tennis video
        
        Args:
            video_input: Video file path (Path or str) or video description string
        
        Returns:
            Dictionary containing the evaluation results
        """
        # Check if input is a file path
        video_path = Path(video_input) if isinstance(video_input, str) and Path(video_input).exists() else None
        
        if video_path and video_path.is_file():
            # Process video file: extract frames and encode to base64
            logger.info(f"Processing video file: {video_path}")
            encoded_frames = self.video_processor.process_video(video_path)
            logger.debug(f"Extracted {len(encoded_frames)} frame(s) from video")
            # Format prompt - frames will be sent as images, so no video text needed
            # Only format if template has 'video' variable
            if "video" in self.prompt_template.input_variables:
                formatted_prompt = self.prompt_template.format(video="")
            else:
                formatted_prompt = self.prompt_template.format()
            # Send prompt with images
            logger.info("Sending video evaluation request to LLM")
            response = self.llm_service.invoke(formatted_prompt, images=encoded_frames)
            logger.debug(f"Received LLM response (length: {len(response)})")
        else:
            # Treat as text description
            logger.info(f"Processing text description: {video_input[:100]}...")
            if "video" in self.prompt_template.input_variables:
                formatted_prompt = self.prompt_template.format(video=str(video_input))
            else:
                formatted_prompt = self.prompt_template.format()
            response = self.llm_service.invoke(formatted_prompt)
            logger.debug(f"Received LLM response (length: {len(response)})")
        
        return self._parse_response(response)
    
    async def evaluate_async(self, video_input: str | Path) -> Dict[str, Any]:
        """
        Async version of evaluate method
        
        Args:
            video_input: Video file path (Path or str) or video description string
        
        Returns:
            Dictionary containing the evaluation results
        """
        # Check if input is a file path
        video_path = Path(video_input) if isinstance(video_input, str) and Path(video_input).exists() else None
        
        if video_path and video_path.is_file():
            # Process video file: extract frames and encode to base64
            logger.info(f"Processing video file (async): {video_path}")
            encoded_frames = self.video_processor.process_video(video_path)
            logger.debug(f"Extracted {len(encoded_frames)} frame(s) from video")
            # Format prompt - frames will be sent as images, so no video text needed
            # Only format if template has 'video' variable
            if "video" in self.prompt_template.input_variables:
                formatted_prompt = self.prompt_template.format(video="")
            else:
                formatted_prompt = self.prompt_template.format()
            # Send prompt with images
            logger.info("Sending video evaluation request to LLM (async)")
            response = await self.llm_service.ainvoke(formatted_prompt, images=encoded_frames)
            logger.debug(f"Received LLM response (length: {len(response)})")
        else:
            # Treat as text description
            logger.info(f"Processing text description (async): {video_input[:100]}...")
            if "video" in self.prompt_template.input_variables:
                formatted_prompt = self.prompt_template.format(video=str(video_input))
            else:
                formatted_prompt = self.prompt_template.format()
            response = await self.llm_service.ainvoke(formatted_prompt)
            logger.debug(f"Received LLM response (length: {len(response)})")
        
        return self._parse_response(response)


def evaluate_video(video_input: str, prompt_name: str = "tennis_evaluation_prompt", api_key: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to evaluate a tennis video
    
    Args:
        video_input: Video description, file path, or video data representation
        prompt_name: Name of the prompt file to use (defaults to "tennis_evaluation_prompt")
        api_key: OpenAI API key (optional)
        model: Model name (optional)
    
    Returns:
        Dictionary containing the evaluation results
    """
    evaluator = VideoEvaluator(prompt_name=prompt_name, api_key=api_key, model=model)
    return evaluator.evaluate(video_input)


async def evaluate_video_async(video_input: str, prompt_name: str = "tennis_evaluation_prompt", api_key: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
    """
    Async convenience function to evaluate a tennis video
    
    Args:
        video_input: Video description, file path, or video data representation
        prompt_name: Name of the prompt file to use (defaults to "tennis_evaluation_prompt")
        api_key: OpenAI API key (optional)
        model: Model name (optional)
    
    Returns:
        Dictionary containing the evaluation results
    """
    evaluator = VideoEvaluator(prompt_name=prompt_name, api_key=api_key, model=model)
    return await evaluator.evaluate_async(video_input)


def main():
    """Main method to run video evaluation on video/tennis.mov"""
    import json
    import sys
    from pathlib import Path
    from rich.console import Console
    from rich.json import JSON
    
    console = Console()
    project_root = Path(__file__).parent.parent.parent
    video_file = project_root / "video" / "tennis.mov"
    
    # Check if video file exists
    if not video_file.exists():
        logger.error(f"Video file not found at {video_file}")
        console.print(f"[red]Error: Video file not found at {video_file}[/red]")
        console.print("[yellow]Please ensure video/tennis.mov exists in the project root.[/yellow]")
        sys.exit(1)
    
    logger.info(f"Starting video evaluation for: {video_file.name}")
    console.print(f"[bold cyan]Evaluating video: {video_file.name}[/bold cyan]\n")
    console.print("[dim]Extracting frames and encoding for LLM analysis...[/dim]\n")
    
    try:
        # Run evaluation with video file path (will extract frames automatically)
        # api_key and model are read from .env file via LLMService
        result = evaluate_video(video_file)
        logger.info("Video evaluation completed successfully")
        
        # Display results
        console.print(f"[bold green]Evaluation Results:[/bold green]\n")
        
        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
            if "raw_response" in result:
                console.print(f"\n[dim]Raw response:[/dim]\n{result['raw_response']}")
        else:
            # Pretty print the results
            result_json = json.dumps(result, indent=2)
            console.print(JSON(result_json))
            
    
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        console.print(f"[red]Configuration Error: {str(e)}[/red]")
        console.print("\n[yellow]Make sure OPENAI_API_KEY is set in your .env file or environment.[/yellow]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during evaluation: {e}", exc_info=True)
        console.print(f"[red]Error during evaluation: {str(e)}[/red]")


if __name__ == "__main__":
    main()
