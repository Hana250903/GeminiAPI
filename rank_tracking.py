from dataclasses import asdict, dataclass
import json
import requests
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai

# External API
EXTERNAL_API_URL = "https://seoboostaiapi-e2bycxbjc4fmgggz.southeastasia-01.azurewebsites.net/api/RankTrackings"

# Localhost API
#EXTERNAL_API_URL = "https://localhost:7144/api/RankTrackings"

# Gemini model setup
model = genai.GenerativeModel('gemini-2.0-flash')

# Pydantic model
class RankTracking(BaseModel):
    keyword_name: str
    rank: int

@dataclass
class RankTrackingRequest:
    input_keyword: str
    id: str

class RankTrackingResponse(BaseModel):
    id: str
    keyword_name: str
    rank: int

# Generate keywords and call external API
def rank_tracking(input_keyword: str, userID: int):
    prompt = (
    f"Given the keyword '{input_keyword}', provide its current estimated search engine rank. "
    "Respond in JSON format as an object with two fields: 'keyword_name' (string) and 'rank' (integer). "
    "The rank can range from 1 to several thousand. If the keyword is not ranked, set 'rank' to 0."
    )


    gemini_response_schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "keyword_name": {"type": "STRING"},
                "rank": {"type": "INTEGER"}
            },
            "required": ["keyword_name", "rank"]
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
    my_keywords: list[RankTracking] = [RankTracking(**item) for item in raw_keywords_data]

    external_api_results = []

    for keyword in my_keywords:
        payload = {
            "userId": userID,
            "keyword": input_keyword,
            "rank": keyword.rank,
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

def update_rank_tracking(request_list_of_objects :list[RankTrackingRequest]):
    # Chuyển đổi list[RankTrackingRequest] thành list[dict]
    # để json.dumps có thể serialize
    request_as_dicts = [asdict(item) for item in request_list_of_objects]

    json_string = json.dumps(request_as_dicts, indent=2, ensure_ascii=False)

    prompt = (
        f"You are an AI assistant designed to simulate search engine rank tracking. "
        f"Given the following list of keyword requests in JSON format:\n\n"
        f"```json\n{json_string}\n```\n\n"
        f"For each keyword, provide an *estimated* search engine rank. "
        f"The rank should be an integer ranging from 1 to 10000. "
        f"If you estimate a keyword would not be ranked in the top 10000, set its rank to 0. "
        f"Ensure the 'id' from the input is preserved in the output."
        f"Respond strictly in JSON format as an array of objects, where each object has 'id' (string), 'keyword_name' (string), and 'rank' (integer)."
    )

    gemini_response_schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "id": {"type": "STRING"},
                "keyword_name": {"type": "STRING"},
                "rank": {"type": "INTEGER"}
            },
            "required": ["id", "keyword_name", "rank"]
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

    my_keywords: list[RankTrackingResponse] = [RankTrackingResponse(**item) for item in raw_keywords_data]

    external_api_results = []

    for keyword in my_keywords:
        payload = [{
            "id":  int(keyword.id),
            "rank": keyword.rank
        }]

        try:
            api_response = requests.patch(EXTERNAL_API_URL, json=payload)    
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
            "status": status,
            "message": message
        })

    return {
        "message": "Keywords generated and sent successfully.",
        "generated_keywords_count": len(my_keywords),
        "external_api_status": external_api_results
    }