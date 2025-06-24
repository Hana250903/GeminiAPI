from dataclasses import asdict, dataclass
import json
import requests
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai


# External API
EXTERNAL_API_URL = "https://seoboostaiapi-e2bycxbjc4fmgggz.southeastasia-01.azurewebsites.net/api/ContentOptimizations"

# Localhost API
# EXTERNAL_API_URL = "https://localhost:7144/api/ContentOptimizations"

# Gemini model setup
model = genai.GenerativeModel('gemini-2.0-flash')


@dataclass
class ContentOptimizationRequest:
    id: int
    user_id: int
    keyword: str
    content: str
    content_length: str
    optimization_level: int
    readability_level: str
    include_citation: bool


@dataclass
class ContentOptimizationResponse:
    optimized_content: str
    seo_score: int
    readability: int
    engagement: int
    originality: int


def optimize_content(request: ContentOptimizationRequest):
    # Chuyển đổi đối tượng ContentOptimizationRequest thành dict để dễ dàng đưa vào prompt
    request_as_dict = asdict(request)

    prompt = (
        f"You are an expert SEO content strategist and a highly skilled content writer. "
        f"Your task is to optimize and rewrite the provided content based on specific criteria. "
        f"The goal is to improve its search engine ranking and user engagement for the target keyword.\n\n"
        f"Here are the details for content optimization:\n"
        f"- **Target Keyword:** '{request_as_dict['keyword']}'\n"
        f"- **Original Content:**\n"
        f"```\n{request_as_dict['content']}\n```\n"
        f"- **Desired Content Length:** {request_as_dict['content_length']} (Options: Short, Medium, Long, Comprehensive, In-depth)\n"
        f"- **Optimization Level:** {request_as_dict['optimization_level']} (Level 1: Basic, Level 2: Moderate, Level 3: Advanced, Level 4: Expert, Level 5: Aggressive)\n"
        f"- **Desired Readability Level:** {request_as_dict['readability_level']} (Options: Easy, Medium, Hard, Advanced, Expert)\n"
        f"- **Include Citations:** {'Yes, add high-quality citations to support claims.' if request_as_dict['include_citation'] else 'No, do not add external citations.'}\n\n"
        f"Based on these criteria, please provide the **fully optimized and rewritten content** along with estimated scores for SEO, Readability, Engagement, and Originality. "
        f"Focus on natural language, user intent, and SEO best practices without keyword stuffing. "
        f"Ensure the content logically flows and maintains its original core message while significantly enhancing its quality and SEO performance.\n\n"
        f"If 'Include Citations' is 'Yes', integrate citations naturally using a common format (e.g., [1], [Source Name]). "
        f"For 'Optimization Level':\n"
        f"  - Level 1 (Basic): Incorporate keyword naturally a few times.\n"
        f"  - Level 2 (Moderate): Integrate keyword and related terms, improve headings.\n"
        f"  - Level 3 (Advanced): Deep keyword integration, add LSI keywords, strong internal/external linking suggestions (if applicable).\n"
        f"  - Level 4 (Expert): Comprehensive keyword strategy, advanced semantic SEO, user intent optimization, competitive analysis implied.\n"
        f"  - Level 5 (Aggressive): Very strong focus on keyword density (while maintaining readability), highly competitive LSI/topic coverage, potentially controversial or highly opinionated if aligns with original content and keyword strategy.\n\n"
        f"For 'Readability Level', adjust vocabulary, sentence structure, and paragraph length accordingly.\n\n"
        f"**Your response must be in strict JSON format**, as a single object, with the following fields:\n"
        f"- `optimized_content` (string): The fully rewritten and optimized content.\n"
        f"- `seo_score` (integer): An estimated SEO score from 0-100, reflecting how well the content is optimized for the keyword and general SEO practices.\n"
        f"- `readability_score` (integer): An estimated readability score from 0-100, reflecting the ease of understanding for the desired readability level.\n"
        f"- `engagement_score` (integer): An estimated engagement score from 0-100, reflecting how likely users are to interact with the content (e.g., time on page, clicks).\n"
        f"- `originality_score` (integer): An estimated originality score from 0-100, reflecting the uniqueness and freshness of the content's perspective or approach compared to common online content on the topic."
    )

    # --- Điều chỉnh gemini_response_schema để khớp với ContentOptimizationResponse ---
    gemini_response_schema = {
        "type": "OBJECT",  # <-- Thay đổi thành OBJECT vì bạn muốn 1 đối tượng duy nhất
        "properties": {
            "optimized_content": {"type": "STRING"},
            "seo_score": {"type": "INTEGER"},
            "readability": {"type": "INTEGER"},
            "engagement": {"type": "INTEGER"},
            "originality": {"type": "INTEGER"}
        },
        "required": ["optimized_content", "seo_score", "readability", "engagement", "originality"]
    }

    gemini_response = model.generate_content(
        contents=prompt,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": gemini_response_schema,
        },
    )

    # Đổi tên biến cho rõ ràng hơn
    raw_response_data = json.loads(gemini_response.text)
    my_optimized_content: ContentOptimizationResponse = ContentOptimizationResponse(
        **raw_response_data)

    external_api_results = []

    # Payload cho API ngoài
    payload = {
        "id": request.id,
        "userId": request.user_id,
        "keyword": request.keyword,
        "originalContent": request.content,
        "contentLenght": request.content_length,
        "optimizationLevel": request.optimization_level,
        "readabilityLevel": request.readability_level,
        "includeCitation": request.include_citation,
        "optimizedContent": my_optimized_content.optimized_content,
        "seoscore": my_optimized_content.seo_score,
        "readability": my_optimized_content.readability,
        "engagement": my_optimized_content.engagement,
        "originality": my_optimized_content.originality
    }

    try:
        api_response = requests.put(EXTERNAL_API_URL, json=payload, verify=False)
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
        "external_api_status": external_api_results
    }
