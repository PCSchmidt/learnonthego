"""
OpenRouter LLM Service for LearnOnTheGo
Handles AI-powered content generation for lectures
"""

import os
import asyncio
from openai import AsyncOpenAI
from typing import Dict, List, Optional, Tuple
import json
from dataclasses import dataclass

@dataclass
class LectureContent:
    """Structured lecture content"""
    title: str
    introduction: str
    main_sections: List[Dict[str, str]]  # [{"title": "...", "content": "..."}]
    examples: List[str]
    conclusion: str
    estimated_duration: int  # in minutes

class OpenRouterService:
    """Service for generating lecture content using OpenRouter API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
        
        # Initialize OpenAI client with OpenRouter endpoint
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        
        # Available models - starting with cost-effective options
        self.models = {
            "default": "anthropic/claude-3.5-haiku",  # Fast and cost-effective
            "creative": "anthropic/claude-3-opus",    # More creative/detailed
            "fast": "openai/gpt-3.5-turbo",          # Very fast and cheap
            "advanced": "openai/gpt-4-turbo",        # Most capable
        }
    
    async def generate_lecture(
        self,
        topic: str,
        duration: int = 10,
        difficulty: str = "intermediate",
        style: str = "educational",
        model_preference: str = "default"
    ) -> LectureContent:
        """Generate a complete lecture on the given topic"""
        
        # Create the prompt for lecture generation
        prompt = self._create_lecture_prompt(topic, duration, difficulty, style)
        
        try:
            # Generate content using OpenRouter
            response = await self.client.chat.completions.create(
                model=self.models.get(model_preference, self.models["default"]),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educator who creates engaging, fact-filled lectures. Always structure your response as valid JSON with the exact format requested."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000,
            )
            
            # Parse the response
            content = response.choices[0].message.content
            lecture_data = json.loads(content)
            
            # Convert to structured format
            return LectureContent(
                title=lecture_data["title"],
                introduction=lecture_data["introduction"],
                main_sections=lecture_data["main_sections"],
                examples=lecture_data["examples"],
                conclusion=lecture_data["conclusion"],
                estimated_duration=lecture_data["estimated_duration"]
            )
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to generate lecture content: {e}")
    
    def _create_lecture_prompt(
        self, 
        topic: str, 
        duration: int, 
        difficulty: str, 
        style: str
    ) -> str:
        """Create a detailed prompt for lecture generation"""
        
        difficulty_instructions = {
            "beginner": "Use simple language, basic concepts, and plenty of analogies. Avoid jargon.",
            "intermediate": "Include some technical terms with explanations. Build on foundational knowledge.",
            "advanced": "Use appropriate technical terminology. Assume prior knowledge in the field."
        }
        
        return f"""Create a comprehensive {duration}-minute lecture on "{topic}" for {difficulty} level learners.

REQUIREMENTS:
- Target duration: {duration} minutes
- Difficulty level: {difficulty} - {difficulty_instructions.get(difficulty, '')}
- Style: {style}
- Include practical examples and real-world applications
- Make it engaging and memorable

RESPONSE FORMAT (must be valid JSON):
{{
    "title": "Engaging lecture title",
    "introduction": "Hook the audience in 2-3 sentences",
    "main_sections": [
        {{"title": "Section 1 Title", "content": "Detailed content for this section"}},
        {{"title": "Section 2 Title", "content": "Detailed content for this section"}},
        {{"title": "Section 3 Title", "content": "Detailed content for this section"}}
    ],
    "examples": [
        "Real-world example 1 with specific details",
        "Real-world example 2 with specific details"
    ],
    "conclusion": "Strong conclusion that reinforces key takeaways",
    "estimated_duration": {duration}
}}

Generate content that would take approximately {duration} minutes to read aloud at a normal speaking pace (150-160 words per minute).
"""

    async def test_connection(self) -> Dict[str, str]:
        """Test the OpenRouter connection"""
        try:
            response = await self.client.chat.completions.create(
                model=self.models["fast"],
                messages=[
                    {"role": "user", "content": "Say 'OpenRouter connection successful!' in exactly those words."}
                ],
                max_tokens=50
            )
            
            return {
                "status": "success",
                "message": response.choices[0].message.content.strip(),
                "model": self.models["fast"]
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Connection failed: {str(e)}"
            }
