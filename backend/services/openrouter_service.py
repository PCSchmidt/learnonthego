"""
OpenRouter LLM Service for LearnOnTheGo
Provides AI-powered lecture content generation using OpenRouter's unified API
Uses direct HTTP requests for maximum control and transparency
"""

import os
import json
import logging
from typing import Dict, List, Optional
import httpx

logger = logging.getLogger(__name__)

class OpenRouterService:
    """
    Service for generating lecture content using OpenRouter's direct API
    
    OpenRouter provides access to 100+ models from providers like:
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude 3.5 Sonnet, Haiku)
    - Meta (Llama models)
    - Google (Gemini)
    - And many more...
    
    Uses direct HTTP requests for maximum control and cost transparency
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Get one at https://openrouter.ai")
        
        # OpenRouter API endpoint
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Default model - Claude 3.5 Sonnet is excellent for content generation
        self.default_model = "anthropic/claude-3.5-sonnet"
        
        # Default headers for all requests
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://learnonthego.app",  # Your app URL
            "X-Title": "LearnOnTheGo",  # Your app name
        }
    
    async def generate_lecture_content(
        self,
        topic: str,
        duration: int,
        difficulty: str,
        user_context: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate structured lecture content using OpenRouter LLM
        
        Args:
            topic: The lecture topic/subject
            duration: Desired duration in minutes (5-60)
            difficulty: beginner, intermediate, or advanced
            user_context: Optional additional context from user
            
        Returns:
            Dictionary with lecture sections (intro, main_content, examples, conclusion)
        """
        
        # Calculate approximate word count (150 words per minute for speech)
        target_words = duration * 150
        
        # Create structured prompt for lecture generation
        prompt = self._create_lecture_prompt(topic, duration, difficulty, target_words, user_context)
        
        try:
            # Prepare the request payload
            payload = {
                "model": self.default_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert educational content creator who generates engaging, factual, and well-structured audio lectures. Focus on clarity, engagement, and educational value."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": target_words + 500,  # Some buffer for structure
                "temperature": 0.7,  # Balanced creativity and consistency
            }
            
            # Make direct API call to OpenRouter
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Add usage and cost information if available
                usage_info = result.get("usage", {})
                
                # Parse the structured response
                parsed_content = self._parse_lecture_content(content)
                
                # Add metadata
                parsed_content["usage"] = usage_info
                parsed_content["model_used"] = self.default_model
                
                return parsed_content
            
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_info = e.response.json()
                error_detail = f": {error_info.get('error', {}).get('message', str(e))}"
            except:
                error_detail = f": HTTP {e.response.status_code}"
            
            raise Exception(f"OpenRouter API request failed{error_detail}. Check your API key at https://openrouter.ai")
        
        except Exception as e:
            raise Exception(f"OpenRouter API request failed: {str(e)}. Check your API key at https://openrouter.ai")
    
    def _create_lecture_prompt(
        self, 
        topic: str, 
        duration: int, 
        difficulty: str, 
        target_words: int,
        user_context: Optional[str] = None
    ) -> str:
        """Create a structured prompt for lecture generation"""
        
        context_section = ""
        if user_context:
            context_section = f"\n\nAdditional Context:\n{user_context}"
        
        return f"""
Create an engaging audio lecture on "{topic}" with the following specifications:

**Requirements:**
- Duration: {duration} minutes (~{target_words} words)
- Difficulty Level: {difficulty}
- Format: Audio-optimized (conversational, clear transitions)
- Structure: Introduction (10%) → Main Content (60%) → Examples (20%) → Conclusion (10%)

**Content Guidelines:**
- Use conversational tone suitable for audio learning
- Include clear transitions between sections
- Provide concrete examples and practical applications
- Ensure factual accuracy and cite key concepts
- Make it engaging for someone listening during a walk/commute

**Difficulty Level Guidelines:**
- Beginner: Basic concepts, simple explanations, minimal jargon
- Intermediate: Some technical terms, assumes basic knowledge
- Advanced: Complex concepts, technical depth, assumes expertise

{context_section}

**Output Format:**
Please structure your response with clear section markers:

[INTRODUCTION]
(Brief hook and overview - ~{int(target_words * 0.1)} words)

[MAIN_CONTENT]
(Core concepts and information - ~{int(target_words * 0.6)} words)

[EXAMPLES]
(Practical examples and applications - ~{int(target_words * 0.2)} words)

[CONCLUSION]
(Summary and key takeaways - ~{int(target_words * 0.1)} words)

Generate the complete lecture content now:
"""
    
    def _parse_lecture_content(self, content: str) -> Dict[str, str]:
        """Parse the structured lecture content into sections"""
        
        sections = {
            "introduction": "",
            "main_content": "",
            "examples": "", 
            "conclusion": "",
            "full_content": content
        }
        
        try:
            # Split content by section markers
            parts = content.split("[")
            
            for part in parts:
                if part.startswith("INTRODUCTION]"):
                    sections["introduction"] = part.replace("INTRODUCTION]", "").strip()
                elif part.startswith("MAIN_CONTENT]"):
                    sections["main_content"] = part.replace("MAIN_CONTENT]", "").strip()
                elif part.startswith("EXAMPLES]"):
                    sections["examples"] = part.replace("EXAMPLES]", "").strip()
                elif part.startswith("CONCLUSION]"):
                    sections["conclusion"] = part.replace("CONCLUSION]", "").strip()
            
            # If parsing fails, put everything in main_content
            if not sections["main_content"] and not sections["introduction"]:
                sections["main_content"] = content
                
        except Exception:
            # Fallback: put all content in main_content
            sections["main_content"] = content
        
        return sections
    
    async def get_available_models(self) -> List[Dict[str, str]]:
        """Get list of available models from OpenRouter"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://openrouter.ai/api/v1/models",
                    headers=self.headers
                )
                response.raise_for_status()
                models = response.json()["data"]
                
                # Filter for models good for content generation
                good_models = [
                    {
                        "id": model["id"],
                        "name": model.get("name", model["id"]),
                        "description": model.get("description", ""),
                        "context_length": model.get("context_length", 0),
                        "pricing": model.get("pricing", {})
                    }
                    for model in models
                    if any(provider in model["id"] for provider in ["anthropic", "openai", "meta-llama", "google"])
                ]
                
                # Sort by quality for content generation (Claude and GPT models first)
                good_models.sort(key=lambda x: (
                    0 if "claude" in x["id"] else
                    1 if "gpt-4" in x["id"] else
                    2 if "gpt-3.5" in x["id"] else
                    3
                ))
                
                return good_models[:15]  # Return top 15 models
                
        except Exception as e:
            # Return default models if API call fails
            return [
                {
                    "id": "anthropic/claude-3.5-sonnet",
                    "name": "Claude 3.5 Sonnet",
                    "description": "Excellent for content generation and educational material",
                    "context_length": 200000,
                    "pricing": {"prompt": "0.000003", "completion": "0.000015"}
                },
                {
                    "id": "openai/gpt-4o",
                    "name": "GPT-4o",
                    "description": "High-quality content generation with multimodal capabilities",
                    "context_length": 128000,
                    "pricing": {"prompt": "0.0025", "completion": "0.01"}
                },
                {
                    "id": "anthropic/claude-3-haiku",
                    "name": "Claude 3 Haiku",
                    "description": "Fast and cost-effective for shorter content",
                    "context_length": 200000,
                    "pricing": {"prompt": "0.00000025", "completion": "0.00000125"}
                }
            ]


# Service instance factory
def create_openrouter_service(api_key: Optional[str] = None) -> OpenRouterService:
    """Create OpenRouter service instance"""
    return OpenRouterService(api_key)
