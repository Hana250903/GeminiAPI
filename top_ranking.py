import json
import requests
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai

# Gemini model setup
model = genai.GenerativeModel('gemini-2.0-flash')

# Pydantic model
class TopRanking(BaseModel):
    keyword_name: str
    rank: int
    search_volume: int

# Generate keywords and call external API
def top_ranking():
    prompt = (
    f"Act as an SEO analytics assistant. Without requiring any user input, provide a list of the top 10 trending keywords in the SEO or digital marketing domain."
    "Respond in JSON format as an object with 3 fields: 'keyword_name' (string), 'rank' (integer) and 'search_volume' (integer)."
    "Respond only in JSON format, as an array of objects with the three fields above."
    )

    gemini_response_schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "keyword_name": {"type": "STRING"},
                "rank": {"type": "INTEGER"},
                "search_volume": {"type": "INTEGER"}
            },
            "required": ["keyword_name", "rank", "search_volume"]
        }
    }

    gemini_response = model.generate_content(
        contents=prompt,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": gemini_response_schema,
        },
    )

    raw_keywords_data = json.loads(gemini_response.text)
    my_keywords: list[TopRanking] = [TopRanking(**item) for item in raw_keywords_data]

    return {
        "message": "Keywords generated and sent successfully.",
        "generated_keywords_count": len(my_keywords),
        "items": raw_keywords_data
    }