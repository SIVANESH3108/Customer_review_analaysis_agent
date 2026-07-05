import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
import google.generativeai as genai
import json
import logging
from config import Config

logger = logging.getLogger(__name__)

if Config.GEMINI_API_KEY:
    genai.configure(api_key=Config.GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY is not set. Gemini API calls will fail.")

def analyze_reviews(reviews_text):
    if not Config.GEMINI_API_KEY:
        raise Exception("Gemini API key is missing. Please configure it in .env file.")

    prompt = f"""You are an expert customer review analyst.

Analyze the following customer reviews.

Return ONLY JSON.

{{
"summary":"",
"overall_sentiment":"",
"positive_percentage":"",
"negative_percentage":"",
"neutral_percentage":"",
"positive_points":[],
"negative_points":[],
"top_complaints":[],
"keywords":[],
"suggestions":[],
"rating":"",
"business_recommendation":""
}}

Customer Reviews:

{reviews_text}
"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        text = response.text
        
        # Strip potential markdown formatting from JSON output
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text.strip())
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON. Response: {text}")
        raise Exception("Failed to parse AI response. Ensure AI returns valid JSON.")
    except Exception as e:
        logger.error(f"Error communicating with Gemini: {e}")
        raise e
