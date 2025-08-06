from dataclasses import asdict, dataclass
import json
import requests
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
from datetime import datetime, timezone

# External API
EXTERNAL_API_URL = "https://seoboostaiapi-e2bycxbjc4fmgggz.southeastasia-01.azurewebsites.net/api/RankTrackings"

# Localhost API
# EXTERNAL_API_URL = "https://localhost:7144/api/RankTrackings"

# Gemini model setup
model = genai.GenerativeModel('gemini-2.5-flash')

# Pydantic model
class RankTracking(BaseModel):
    keyword_name: str
    rank: int

@dataclass
class RankTrackingRequest:
    input_keyword: str
    id: str

@dataclass
class UpdateRankTrackingRequest:
    input_keyword: str
    id: str
    old_rank: int

class RankTrackingResponse(BaseModel):
    id: str
    keyword_name: str
    rank: int

# Generate keywords and call external API
def rank_tracking(input_keyword: str, userID: int):
    prompt = (
    f"You are an AI assistant that simulates realistic search engine rank tracking. "
    "Given the keyword '{input_keyword}', provide its current estimated search engine rank. "
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

    utc_now = datetime.now(timezone.utc)
    formatted = utc_now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    for keyword in my_keywords:
        payload = {
            "userId": userID,
            "model": "gemini-2.5-flash",
            "keyword": input_keyword,
            "rank": keyword.rank,
            "createDate": formatted
        }

        try:
            api_response = requests.post(EXTERNAL_API_URL, json=payload, verify=False)    
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

def update_rank_tracking(request_list_of_objects :list[UpdateRankTrackingRequest]):
    # Chuyển đổi list[UpdateRankTrackingRequest] thành list[dict]
    # để json.dumps có thể serialize
    request_as_dicts = [asdict(item) for item in request_list_of_objects]

    json_string = json.dumps(request_as_dicts, indent=2, ensure_ascii=False)

    prompt = (
    f"You are an AI assistant that simulates realistic search engine rank tracking. "
    f"Given the following list of keywords, each with its current rank (`old_rank`), in JSON format:\n\n"
    f"```json\n{json_string}\n```\n\n"
    f"Your task is to provide a new estimated `rank` for each keyword. You must follow these rules precisely to ensure realistic fluctuations:\n\n"
    f"1.  **The new rank must be a plausible, small change from the `old_rank`.**\n"
    f"2.  **For high ranks (e.g., 1-20),** the change must be very small, typically +/- 1 to 3 positions. A large, unrealistic jump like from rank 3 to 300 is **strictly forbidden**.\n"
    f"3.  **For mid-range ranks (e.g., 21-100),** the change can be more moderate, such as +/- 5 to 15 positions.\n"
    f"4.  **If `old_rank` is 0,** provide a realistic initial rank for a newly discovered keyword, for example, between 50 and 200.\n\n"
    f"Ensure the `id` and `keyword_name` from the input are preserved in the output. "
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
    utc_now = datetime.now(timezone.utc)
    formatted = utc_now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    for keyword in my_keywords:
        payload = [{
            "id":  int(keyword.id),
            "rank": keyword.rank,
            "updatedDate": formatted
        }]

        try:
            api_response = requests.patch(EXTERNAL_API_URL, json=payload, verify=False)    
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