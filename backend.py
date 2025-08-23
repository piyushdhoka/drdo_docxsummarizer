import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Literal
import re

# Load environment variables
load_dotenv()

# Configure Gemini API
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.getenv("GEMINI_API_KEY")
print(f"DEBUG: API Key loaded: {GEMINI_API_KEY[:10] if GEMINI_API_KEY else 'None'}...")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)

def preprocess_text(text: str) -> str:
    """
    Preprocess text to improve summarization quality.
    
    Args:
        text (str): Raw text to preprocess
        
    Returns:
        str: Cleaned and preprocessed text
    """
    if not text or not text.strip():
        return ""
    
    # Remove excessive whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common noise patterns
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', '', text)
    
    # Fix common OCR issues
    text = re.sub(r'(\w)\|(\w)', r'\1l\2', text)  # Fix | -> l
    text = re.sub(r'(\w)0(\w)', r'\1o\2', text)   # Fix 0 -> o
    
    # Remove page numbers and headers
    text = re.sub(r'Page \d+', '', text)
    text = re.sub(r'^\d+\s*', '', text, flags=re.MULTILINE)
    
    # Clean up bullet points and lists
    text = re.sub(r'^\s*[•\-\*]\s*', '', text, flags=re.MULTILINE)
    
    # Remove excessive newlines
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Ensure proper sentence endings
    text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
    
    return text.strip()

def build_prompt(text, style):
    """Build enhanced prompts for different summary styles with better accuracy."""
    if style == "bullet":
        return f"""Please provide a comprehensive bullet-point summary of the following document. 

Requirements:
- Extract the most important key points and main ideas
- Maintain logical flow and hierarchy
- Use clear, actionable bullet points
- Include relevant facts, figures, and conclusions
- Ensure accuracy and completeness

Document to summarize:
{text}

Please provide a well-structured bullet-point summary:"""
    
    elif style == "abstract":
        return f"""Please write a professional abstract summary of the following document.

Requirements:
- 3-4 concise sentences capturing the essence
- Include main topic, key findings, methodology (if applicable), and conclusions
- Use academic/professional tone
- Maintain factual accuracy
- Highlight the most significant contributions or insights

Document to summarize:
{text}

Please provide a professional abstract:"""
    
    elif style == "detailed":
        return f"""Please provide a comprehensive, detailed summary of the following document.

Requirements:
- Cover main arguments, supporting evidence, and conclusions
- Maintain the document's logical structure
- Include key examples, data points, and references
- Provide context and background information
- Ensure thorough understanding while maintaining clarity
- Highlight relationships between different sections/ideas

Document to summarize:
{text}

Please provide a detailed summary:"""
    
    else:
        return f"""Please provide a comprehensive summary of the following document.

Requirements:
- Identify main themes and key points
- Maintain accuracy and completeness
- Use clear, professional language
- Highlight important conclusions and implications

Document to summarize:
{text}

Please provide a summary:"""

def summarize_text(text: str, style: Literal["bullet", "abstract", "detailed"] = "bullet") -> str:
    """
    Generate a summary of the given text using Google Gemini AI.
    
    Args:
        text (str): The text to summarize
        style (str): The style of summary ("bullet", "abstract", or "detailed")
        
    Returns:
        str: The generated summary
    """
    if not text or not text.strip():
        return "Error: No text provided for summarization"
    
    try:
        # Preprocess text for better quality
        cleaned_text = preprocess_text(text)
        
        if not cleaned_text:
            return "Error: Text preprocessing resulted in empty content"
        
        # Use Gemini 1.5 Flash for better performance
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Build custom prompt based on style
        prompt = build_prompt(cleaned_text, style)
        
        try:
            # Generate summary with safety settings
            response = model.generate_content(
                prompt,
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                ],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Lower temperature for more consistent results
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
            
            if response.text:
                return response.text.strip()
            else:
                return "Error: No summary generated. Please try again."
                
        except Exception as e:
            return f"Error generating summary: {str(e)}"
            
    except Exception as e:
        return f"Error: {str(e)}"

def get_available_models():
    """Get list of available Gemini models."""
    try:
        models = genai.list_models()
        return [model.name for model in models if 'gemini' in model.name.lower()]
    except Exception as e:
        return f"Error retrieving models: {str(e)}"

def evaluate_summary_quality(original_text: str, summary: str) -> dict:
    """
    Evaluate the quality of a generated summary.
    
    Args:
        original_text (str): The original document text
        summary (str): The generated summary
        
    Returns:
        dict: Quality metrics and feedback
    """
    try:
        # Basic metrics
        original_length = len(original_text.split())
        summary_length = len(summary.split())
        compression_ratio = summary_length / original_length if original_length > 0 else 0
        
        # Quality indicators
        quality_score = 0
        feedback = []
        
        # Check compression ratio (ideal: 10-30%)
        if 0.05 <= compression_ratio <= 0.4:
            quality_score += 25
            feedback.append("✅ Good compression ratio")
        elif compression_ratio < 0.05:
            feedback.append("⚠️ Summary might be too brief")
        else:
            feedback.append("⚠️ Summary might be too verbose")
        
        # Check for key content indicators
        key_indicators = ['conclusion', 'summary', 'therefore', 'thus', 'overall', 'key', 'important', 'main']
        if any(indicator in summary.lower() for indicator in key_indicators):
            quality_score += 20
            feedback.append("✅ Contains key content indicators")
        
        # Check structure
        if '•' in summary or '-' in summary or '\n' in summary:
            quality_score += 15
            feedback.append("✅ Well-structured format")
        
        # Check length appropriateness
        if summary_length >= 50:
            quality_score += 20
            feedback.append("✅ Appropriate summary length")
        elif summary_length < 20:
            feedback.append("⚠️ Summary might be too short")
        
        # Check for complete sentences
        sentences = summary.split('.')
        if len(sentences) >= 2:
            quality_score += 20
            feedback.append("✅ Contains complete thoughts")
        
        # Overall assessment
        if quality_score >= 80:
            overall_rating = "Excellent"
        elif quality_score >= 60:
            overall_rating = "Good"
        elif quality_score >= 40:
            overall_rating = "Fair"
        else:
            overall_rating = "Needs Improvement"
        
        return {
            'quality_score': quality_score,
            'overall_rating': overall_rating,
            'compression_ratio': round(compression_ratio * 100, 1),
            'original_length': original_length,
            'summary_length': summary_length,
            'feedback': feedback,
            'suggestions': get_improvement_suggestions(quality_score, compression_ratio)
        }
        
    except Exception as e:
        return {
            'error': f"Error evaluating summary: {str(e)}",
            'quality_score': 0,
            'overall_rating': 'Error'
        }

def get_improvement_suggestions(quality_score: int, compression_ratio: float) -> list:
    """Get suggestions for improving summary quality."""
    suggestions = []
    
    if quality_score < 60:
        suggestions.append("Consider regenerating with a different style")
        suggestions.append("Check if the document text is properly extracted")
    
    if compression_ratio < 0.05:
        suggestions.append("Try 'Detailed' style for more comprehensive summary")
    
    if compression_ratio > 0.4:
        suggestions.append("Try 'Abstract' style for more concise summary")
    
    if quality_score < 40:
        suggestions.append("Verify document format is supported")
        suggestions.append("Ensure document contains readable text content")
    
    return suggestions
