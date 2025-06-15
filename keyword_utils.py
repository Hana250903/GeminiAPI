import json
import requests
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai

# External API
EXTERNAL_API_URL = "https://seoboostaiapi-e2bycxbjc4fmgggz.southeastasia-01.azurewebsites.net/api/Keywords"

# Gemini model setup
model = genai.GenerativeModel('gemini-2.0-flash')

# Pydantic model
class Keyword(BaseModel):
    keyword_name: str
    searchVolume: int
    difficulty: Optional[int] = None
    cpc: Optional[float] = None
    competition: Optional[str] = None
    intent: Optional[str] = None
    trending: bool
    rank: int

# Generate keywords and call external API
def generate_and_send_keywords(input_keyword: str):
    prompt = (
        f"List 10 keywords related to '{input_keyword}' with search volume, difficulty, CPC, "
        "competition, intent, trending status and rank. Ensure all requested fields are always present. "
        "Provide realistic but synthetic data for all fields."
    )

    gemini_response_schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "keyword_name": {"type": "STRING"},
                "searchVolume": {"type": "INTEGER"},
                "difficulty": {"type": "INTEGER"},
                "cpc": {"type": "NUMBER"},
                "competition": {"type": "STRING"},
                "intent": {"type": "STRING"},
                "trending": {"type": "BOOLEAN"},
                "rank": {"type": "INTEGER"}
            },
            "required": ["keyword_name", "searchVolume", "difficulty", "cpc", "competition", "intent", "trending", "rank"]
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
    my_keywords: list[Keyword] = [Keyword(**item) for item in raw_keywords_data]

    external_api_results = []

    for keyword in my_keywords:
        payload = {
            "userId": 2,
            "searchKeyword": input_keyword,
            "keyword1": keyword.keyword_name,
            "keyword": keyword.keyword_name,
            "searchVolume": keyword.searchVolume,
            "difficulty": keyword.difficulty if keyword.difficulty is not None else 0,
            "cpc": keyword.cpc if keyword.cpc is not None else 0.0,
            "competition": keyword.competition if keyword.competition is not None else "N/A",
            "intent": keyword.intent if keyword.intent is not None else "N/A",
            "trend": "True" if keyword.trending else "False",
            "rank": keyword.rank if keyword.rank is not None else 0
        }

        try:
            api_response = requests.post(EXTERNAL_API_URL, json=payload)
            if api_response.ok:
                status = "success"
                message = f"Status Code: {api_response.status_code}"
            else:
                status = "failure"
                message = f"Status Code: {api_response.status_code}, Error: {api_response.text}"
        except requests.exceptions.RequestException as req_err:
            status = "failure"
            message = f"Network/Connection Error: {req_err}"
        except Exception as api_exc:
            status = "failure"
            message = f"Unexpected Error: {api_exc}"

        external_api_results.append({
            "keyword": keyword.keyword_name,
            "status": status,
            "message": message
        })

    return {
        "message": "Keywords generated and sent successfully.",
        "generated_keywords_count": len(my_keywords),
        "external_api_status": external_api_results
    }