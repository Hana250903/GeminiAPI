import json
import requests
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai

# External API
EXTERNAL_API_URL = "https://seoboostaiapi-e2bycxbjc4fmgggz.southeastasia-01.azurewebsites.net/api/RankTrackings"

# Gemini model setup
model = genai.GenerativeModel('gemini-2.0-flash')

# Pydantic model
class RankTracking(BaseModel):
    keyword_name: str
    rank: int

seo_audit_data = {
  "audit_summary": {
    "url": "https://www.yourwebsite.com",
    "overallScore": 73,
    "criticalIssue": 2,
    "warning": 2,
    "opportunity": 61,
    "passedCheck": "167/230 element passed"
  },
  "failed_elements": [
    {
      "id": "H1_TAG_CHECK",
      "name": "Missing or Multiple H1 Tags",
      "description": "Some pages either lack an H1 heading or contain more than one, which can confuse search engines about the page's main topic.",
      "category": "On-Page SEO",
      "severity": "Critical",
      "status": "not_passed",
      "affectedUrls": [
        "https://www.yourwebsite.com/page_A",
        "https://www.yourwebsite.com/page_B"
      ],
      "recommendation_from_audit_tool": "Ensure each page has one unique and descriptive H1 tag."
    },
    {
      "id": "MOBILE_SPEED_CHECK",
      "name": "Slow Mobile Page Speed",
      "description": "The mobile version of your website loads slowly, impacting user experience and mobile search rankings.",
      "category": "Performance",
      "severity": "Critical",
      "status": "not_passed",
      "affectedUrls": [
        "https://www.yourwebsite.com/"
      ],
      "recommendation_from_audit_tool": "Optimize images, leverage browser caching, minify CSS/JS, and reduce server response time."
    },
    {
      "id": "ALT_TEXT_CHECK",
      "name": "Missing Alt Text for Images",
      "description": "Several images on your site are missing descriptive 'alt' attributes, which are crucial for accessibility and SEO.",
      "category": "Technical SEO",
      "severity": "Warning",
      "status": "not_passed",
      "affectedUrls": [
        "https://www.yourwebsite.com/image_gallery",
        "https://www.yourwebsite.com/blog_post"
      ],
      "recommendation_from_audit_tool": "Add concise and descriptive alt text to all informational images. Use empty alt for decorative images."
    },
    {
      "id": "BROKEN_LINKS",
      "name": "Broken Internal Links",
      "description": "Some internal links on your website are broken, leading to a 404 error page. This harms user experience and SEO.",
      "category": "Technical SEO",
      "severity": "Warning",
      "status": "not_passed",
      "affectedUrls": [
        "https://www.yourwebsite.com/about",
        "https://www.yourwebsite.com/contact"
      ],
      "recommendation_from_audit_tool": "Identify and fix all broken internal links. Update or remove dead links."
    },
    {
      "id": "MISSING_META_DESCRIPTION",
      "name": "Missing Meta Descriptions",
      "description": "Several pages lack a meta description, which can reduce click-through rates from search results.",
      "category": "On-Page SEO",
      "severity": "Opportunity",
      "status": "not_passed",
      "affectedUrls": [
        "https://www.yourwebsite.com/service-page",
        "https://www.yourwebsite.com/faq"
      ],
      "recommendation_from_audit_tool": "Write unique, compelling meta descriptions for all pages."
    }
  ]
}

# Chuyển đổi dữ liệu JSON thành chuỗi để đưa vào prompt
json_string = json.dumps(seo_audit_data, indent=2, ensure_ascii=False)

# Generate keywords and call external API
def seo_advisor():
    prompt = (
    f"""
        You are an SEO and technical analysis expert. I have run an SEO Audit for my website and have a list of failed audit items (failed_elements).

        Below is the JSON data containing the audit summary and details of the failing issues.
        The website's URL is: {seo_audit_data['audit_summary']['url']}
        Overall Score: {seo_audit_data['audit_summary']['overallScore']}
        Number of Critical Issues: {seo_audit_data['audit_summary']['criticalIssue']}
        Number of Warnings: {seo_audit_data['audit_summary']['warning']}
        Number of Opportunities: {seo_audit_data['audit_summary']['opportunity']}

        Here are the details of the failed audit items:{json_string}

        Based on this information, please provide specific advice on how to fix each issue. Please prioritize issues with 'severity: Critical' first, followed by 'Warning', and finally 'Opportunity'. For each issue, explain why it's important and provide clear action steps.

        Present your advice as a list of issues and their corresponding solutions.
    """
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
        generation_config=genai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=2048, # Tăng số lượng token đầu ra nếu cần
            temperature=0.7 # Điều chỉnh nhiệt độ để kiểm soát tính sáng tạo/tính chính xác
        )
    )

    return {
        "message": "Keywords generated and sent successfully.",
        "advisor": gemini_response.text
    }