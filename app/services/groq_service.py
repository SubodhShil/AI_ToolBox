"""
Groq Service Module - Direct integration with Groq API for all AI features
"""

import os
import json
import re
from typing import Dict, Any, List, Optional
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GroqService:
    """Service class for interacting with Groq API"""
    
    # Available Groq models
    MODELS = {
        "openai/gpt-oss-120b": "GPT OSS 120B - Best for text tasks",
        "meta-llama/llama-4-maverick-17b-128e-instruct": "Llama 4 Maverick - Best for vision/image tasks",
        "llama-3.3-70b-versatile": "Llama 3.3 70B - Versatile",
    }
    
    # Model for text operations
    TEXT_MODEL = "openai/gpt-oss-120b"
    # Model for image/vision operations  
    IMAGE_MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"
    # Default model
    DEFAULT_MODEL = "openai/gpt-oss-120b"
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in your .env file.")
        self.client = Groq(api_key=self.api_key)
    
    def _call_groq(self, messages: List[Dict[str, str]], model: str = None, temperature: float = 1, max_tokens: int = 8192, use_reasoning: bool = True) -> str:
        """Make a call to the Groq API"""
        model = model or self.DEFAULT_MODEL
        
        try:
            # Build parameters
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_completion_tokens": max_tokens,
                "top_p": 1,
                "stream": False,
                "stop": None,
            }
            
            # Add reasoning_effort for models that support it
            if use_reasoning and "gpt-oss" in model:
                params["reasoning_effort"] = "medium"
            
            completion = self.client.chat.completions.create(**params)
            return completion.choices[0].message.content
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    def _extract_json(self, content: str) -> Dict[str, Any]:
        """Extract JSON from a response that might be wrapped in markdown code blocks"""
        # Try to extract JSON if it's wrapped in markdown code blocks
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        
        # Also try without the json tag
        if not json_match:
            json_match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
        
        return json.loads(content)
    
    # ==================== GRAMMAR CHECK ====================
    def check_grammar(self, text: str, model: str = None) -> Dict[str, Any]:
        """Check grammar and return detailed corrections"""
        
        prompt = f"""You are a professional editor and an expert grammar tutor. Check the following text for grammar and spelling errors, factual errors, word choice issues, and suggest better word combinations.
        
Original text: {text}

Provide your response in the following JSON format:

```json
{{
  "corrected_text": "The corrected version of the text with ONLY grammatical errors fixed. DO NOT completely paraphrase the text.",
  "corrections": [
    {{
      "error": "The original error text (the exact part of the sentence that is incorrect)",
      "suggestion": "The corrected version of that specific part",
      "type": "The type of error (e.g., spelling, grammar, punctuation, subject-verb agreement, verb tense, noun form, article usage, factual error, word choice, word combination)",
      "explanation": "A brief, clear explanation of why this specific part is an error and how the suggestion fixes it.",
      "grammar_rule": {{
        "rule_name": "A concise name for the grammar rule that was violated",
        "description": "A detailed but simple, beginner-friendly explanation of the grammar rule.",
        "correct_examples": ["Example 1", "Example 2"],
        "incorrect_examples": ["Incorrect example 1", "Incorrect example 2"]
      }}
    }}
  ]
}}
```

IMPORTANT INSTRUCTIONS:
1. For the "corrected_text", maintain the original text structure and only fix actual errors. DO NOT completely rewrite or paraphrase the text.
2. Only suggest complete paraphrasing when the correction type is specifically "word combination".
3. For grammatical errors, make minimal changes necessary to fix the specific issue.
4. Identify actual errors only - don't suggest stylistic changes unless they're grammatically incorrect.
5. For each correction, the "error" field must contain the exact text from the original that contains the error.

If there are no errors in the original text, return the original text as "corrected_text" and an empty array for "corrections".
Ensure the JSON is well-formed."""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self._call_groq(messages, model=model or self.TEXT_MODEL, temperature=1)
            result = self._extract_json(response)
            
            # Ensure required fields exist
            if "corrected_text" not in result:
                result["corrected_text"] = text
            if "corrections" not in result:
                result["corrections"] = []
            
            return {
                "original_text": text,
                "corrected_text": result["corrected_text"],
                "corrections": result["corrections"]
            }
        except json.JSONDecodeError:
            # If JSON parsing fails, return the response as corrected text
            return {
                "original_text": text,
                "corrected_text": response if 'response' in dir() else text,
                "corrections": []
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== CHAT ====================
    def chat(self, message: str, conversation_history: List[Dict[str, str]] = None, model: str = None) -> Dict[str, Any]:
        """Chat with AI assistant"""
        
        system_prompt = """You are a helpful, friendly, and knowledgeable AI assistant. You provide accurate, 
thoughtful responses to user questions. You're designed to be helpful, harmless, and honest.
If you don't know something, admit it rather than making up information.
If the question is unclear, ask for clarification. If the question is inappropriate, politely decline to answer."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                messages.append(msg)
        
        messages.append({"role": "user", "content": message})
        
        try:
            response = self._call_groq(messages, model=model or self.TEXT_MODEL, temperature=1)
            return {"response": response}
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== PARAPHRASE ====================
    def paraphrase(self, text: str, style: str, model: str = None) -> Dict[str, Any]:
        """Paraphrase text in a specified style"""
        
        prompt = f"""You are an expert language paraphraser. Your task is to paraphrase the given text according to the specified style.

Original text: {text}
Style: {style}

Style Guidelines:
- Fluency: Make the text flow naturally and smoothly, focusing on readability.
- Humanize: Make the text sound more conversational, warm, and relatable.
- Formal: Use professional language, avoid contractions, and maintain a respectful tone.
- Academic: Use scholarly language, precise terminology, and complex sentence structures.
- Simple: Use straightforward language, short sentences, and common words.
- Creative: Use vivid language, metaphors, and unique expressions.
- Shorten: Condense the text while preserving the key information.

Provide only the paraphrased text without any additional comments or explanations."""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self._call_groq(messages, model=model or self.TEXT_MODEL, temperature=1)
            return {
                "original_text": text,
                "paraphrased_text": response.strip(),
                "style": style
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== PLAGIARISM CHECK ====================
    def check_plagiarism(self, text: str, model: str = None) -> Dict[str, Any]:
        """Check text for plagiarism/AI-generated content"""
        
        prompt = f"""You are a plagiarism detection system. Given the input text, you must:

1. Check if the text is likely AI-generated or copied from online sources.
2. Compare it to your training data and common knowledge sources (e.g., Wikipedia, essays, articles).
3. Analyze for typical AI-generated patterns like:
   - Balanced paragraph structure with intro-middle-conclusion
   - Transition phrases like "In conclusion", "On the one hand...", etc.
   - Overly clean grammar without typos
   - High-level vocabulary but no personal tone
   - Generic or commonly seen ChatGPT-style answers
   - Wordy, robotic, or unnaturally perfect phrasing

Return a JSON object with the following fields:
- plagiarism_score: A number from 0 to 100 indicating the likelihood of plagiarism or AI-generation
- flagged_sentences: An array of sentences that appear to be copied or AI-generated
- feedback: Detailed explanation of why certain parts were flagged and suggestions for improvement

Here is the text to analyze:
{text}

Respond with ONLY a valid JSON object following this format:
```json
{{
  "plagiarism_score": 78,
  "flagged_sentences": [
    "Artificial intelligence is transforming every industry in the modern world.",
    "In conclusion, technology will shape the future of education."
  ],
  "feedback": "These sentences appear overly generic and match patterns often seen in AI-generated or public content. Consider personalizing or adding specific references."
}}
```"""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self._call_groq(messages, model=model or self.TEXT_MODEL, temperature=1)
            result = self._extract_json(response)
            
            # Ensure required fields exist
            if "plagiarism_score" not in result:
                result["plagiarism_score"] = 0
            if "flagged_sentences" not in result:
                result["flagged_sentences"] = []
            if "feedback" not in result:
                result["feedback"] = "No issues detected in the text."
            
            return {
                "original_text": text,
                "plagiarism_score": result["plagiarism_score"],
                "flagged_sentences": result["flagged_sentences"],
                "feedback": result["feedback"]
            }
        except json.JSONDecodeError:
            return {
                "original_text": text,
                "plagiarism_score": 0,
                "flagged_sentences": [],
                "feedback": "Unable to analyze text. Please try again."
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== YOUTUBE SUMMARIZATION ====================
    def summarize_youtube(self, transcript: str, video_title: str = "", model: str = None) -> Dict[str, Any]:
        """Summarize YouTube video transcript"""
        
        title_context = f"\nVideo Title: {video_title}" if video_title else ""
        
        prompt = f"""You are an expert content summarizer. Your task is to create a comprehensive yet concise summary of the following YouTube video transcript.
{title_context}

Transcript:
{transcript}

Please provide:
1. A brief overview (2-3 sentences)
2. Key points discussed in the video (bullet points)
3. Main takeaways or conclusions

Format your response clearly with headers."""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self._call_groq(messages, model=model or self.TEXT_MODEL, temperature=1, max_tokens=2048)
            return {
                "summary": response,
                "title": video_title or "YouTube Video Summary"
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== IMAGE ANALYSIS ====================
    def analyze_image(self, image_url: str, prompt: str = "Describe this image in detail.", model: str = None) -> Dict[str, Any]:
        """Analyze an image using the vision model"""
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ]
        
        try:
            # Use the image model for vision tasks
            completion = self.client.chat.completions.create(
                model=model or self.IMAGE_MODEL,
                messages=messages,
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )
            return {"analysis": completion.choices[0].message.content}
        except Exception as e:
            return {"error": str(e)}


# Singleton instance for easy import
_groq_service = None

def get_groq_service() -> GroqService:
    """Get or create the Groq service singleton"""
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqService()
    return _groq_service
