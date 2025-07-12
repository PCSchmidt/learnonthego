"""
Mock services for development testing to minimize API costs
These services simulate AI responses without making expensive API calls
"""

import asyncio
import random
from typing import Dict, Any, List
import tempfile
import os


class MockOpenRouterService:
    """Mock OpenRouter service for cost-free development testing"""
    
    def __init__(self):
        self.mock_responses = {
            "short": """
# Introduction to Machine Learning

Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.

## Key Concepts

**Supervised Learning**: Learning with labeled examples
- Classification: Predicting categories
- Regression: Predicting continuous values

**Unsupervised Learning**: Finding patterns in unlabeled data
- Clustering: Grouping similar data points
- Dimensionality reduction: Simplifying data

## Applications

Machine learning powers many modern technologies:
- Search engines that understand your queries
- Recommendation systems on streaming platforms
- Autonomous vehicles that navigate safely
- Medical diagnosis systems that detect diseases

## Getting Started

Begin your ML journey by learning Python and basic statistics. Practice with datasets and gradually build more complex projects.
""",
            "medium": "This is a medium-length mock lecture content for testing purposes. " * 50,
            "long": "This is a long mock lecture content for comprehensive testing. " * 100
        }
    
    async def generate_lecture_content(
        self, 
        topic: str, 
        duration: int, 
        difficulty: str, 
        content_source: str = None
    ) -> Dict[str, Any]:
        """Generate mock lecture content"""
        
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        # Select content based on duration
        if duration <= 2:
            content = self.mock_responses["short"]
        elif duration <= 5:
            content = self.mock_responses["medium"]
        else:
            content = self.mock_responses["long"]
        
        # Add topic-specific customization
        content = content.replace("Machine Learning", topic.title())
        
        return {
            "content": content,
            "word_count": len(content.split()),
            "estimated_duration": duration,
            "model_used": "mock-gpt-4",
            "tokens_used": len(content.split()) * 1.3,  # Rough token estimate
            "cost_estimate": 0.001  # Mock cost
        }
    
    async def get_available_models(self) -> List[str]:
        """Return mock available models"""
        return ["mock-gpt-4", "mock-claude-3.5", "mock-llama-2"]


class MockTTSService:
    """Mock TTS service for cost-free development testing"""
    
    def __init__(self):
        self.mock_voices = ["Rachel", "Adam", "Domi", "Elli", "Josh"]
    
    async def generate_speech(
        self, 
        text: str, 
        voice: str = "Rachel", 
        user_api_key: str = None
    ) -> Dict[str, Any]:
        """Generate mock audio file"""
        
        # Simulate processing delay
        await asyncio.sleep(1.0)
        
        # Create a mock audio file (empty file for testing)
        temp_dir = "temp_audio"
        os.makedirs(temp_dir, exist_ok=True)
        
        mock_file_path = os.path.join(temp_dir, f"mock_audio_{random.randint(1000, 9999)}.mp3")
        
        # Create a small mock file
        with open(mock_file_path, "wb") as f:
            # Write minimal MP3 header (not a real MP3, just for testing)
            f.write(b"MOCK_AUDIO_DATA")
        
        character_count = len(text)
        estimated_cost = character_count * 0.0001  # Mock cost calculation
        
        return {
            "audio_file_path": mock_file_path,
            "character_count": character_count,
            "voice_used": voice,
            "duration_seconds": len(text.split()) * 0.5,  # Rough duration estimate
            "cost_estimate": estimated_cost,
            "file_size_bytes": 1024  # Mock file size
        }
    
    async def get_available_voices(self) -> List[str]:
        """Return mock available voices"""
        return self.mock_voices


class MockPDFService:
    """Mock PDF service for testing"""
    
    async def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract mock text from PDF"""
        
        # Simulate processing delay
        await asyncio.sleep(0.3)
        
        mock_text = """
This is mock text extracted from a PDF document for testing purposes.

Chapter 1: Introduction
This chapter covers the basic concepts and provides an overview of the subject matter.

Chapter 2: Advanced Topics
Here we dive deeper into more complex areas and provide detailed explanations.

Conclusion
This document provides a comprehensive overview of the topic with practical examples.
"""
        
        return {
            "text": mock_text,
            "page_count": 3,
            "word_count": len(mock_text.split()),
            "character_count": len(mock_text),
            "extraction_method": "mock_pdfplumber"
        }


# Environment variable to enable mock mode
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"


def get_openrouter_service():
    """Factory function to return real or mock service based on environment"""
    if MOCK_MODE:
        return MockOpenRouterService()
    else:
        from .openrouter_service import OpenRouterService
        return OpenRouterService()


def get_tts_service():
    """Factory function to return real or mock TTS service"""
    if MOCK_MODE:
        return MockTTSService()
    else:
        from .tts_service import TTSService
        return TTSService()


def get_pdf_service():
    """Factory function to return real or mock PDF service"""
    if MOCK_MODE:
        return MockPDFService()
    else:
        from .pdf_service import PDFService
        return PDFService()
