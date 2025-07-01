from dataclasses import dataclass, field, asdict 
import json
import sys
from jsonschema import ValidationError
import google.generativeai as genai

from deserialize import deserialize_to_dataclass

# External API
EXTERNAL_API_URL = "https://seoboostaiapi-e2bycxbjc4fmgggz.southeastasia-01.azurewebsites.net/api/RankTrackings"

# Gemini model setup
model = genai.GenerativeModel('gemini-2.0-flash')

@dataclass
class Elements:
    id: int
    url: str
    element: str
    current_value: str
    status: str
    important: int
    description: str
    audit_repost_id: int | None

@dataclass
class AuditRequestModel:
    id: int
    user_id: int
    url: str
    overall_score: int
    critical_issue: int
    warning: int
    opportunity: int
    passed_check: str
    failed_elements: list[Elements] = field(default_factory=list)

# --- CÁC DATACLASS ĐẦU RA (GIỮ NGUYÊN - VẪN DÙNG CHÚNG ĐỂ MAP) ---
@dataclass
class IssueDetail:
    issue_type: str
    importance: str
    fix_steps: list[str] = field(default_factory=list)
    affected_urls: list[str] = field(default_factory=list)
    example_error_detail: dict | None = None

@dataclass
class AdviceSection:
    critical_issues: list[IssueDetail] = field(default_factory=list)
    warnings: list[IssueDetail] = field(default_factory=list)
    opportunities: list[IssueDetail] = field(default_factory=list)

@dataclass
class SummaryOutput:
    url: str
    overall_score: int
    critical_issues_count: int
    warning_count: int
    opportunity_count: int

@dataclass
class SEOAdvisorResponse:
    summary: SummaryOutput
    advice: AdviceSection
    next_steps_message: str

def seo_advisor(request_data: AuditRequestModel) -> SEOAdvisorResponse:

    # Chuẩn bị `failed_elements` thành chuỗi JSON để đưa vào prompt
    failed_elements_dicts = [asdict(el) for el in request_data.failed_elements]
    json_failed_elements_string = json.dumps(failed_elements_dicts, indent=2, ensure_ascii=False)

    # Prompt đã được tinh gọn, không còn mô tả cấu trúc JSON nữa
    # Vì cấu trúc đã được định nghĩa trong response_schema
    prompt = (
        f"""
        Bạn là một chuyên gia tư vấn SEO và phân tích kỹ thuật. Dưới đây là dữ liệu kiểm tra SEO cho một trang web.

        **Thông tin tổng quan:**
        - URL: {request_data.url}
        - Điểm tổng thể: {request_data.overall_score}
        - Số lỗi Nghiêm trọng (Critical Issues): {request_data.critical_issue}
        - Số Cảnh báo (Warnings): {request_data.warning}
        - Số Cơ hội cải thiện (Opportunities): {request_data.opportunity}

        **Chi tiết các phần tử không đạt kiểm tra (failed_elements):**
        {json_failed_elements_string}

        **Nhiệm vụ:** Dựa trên các thông tin trên, hãy phân tích và cung cấp lời khuyên cụ thể, dễ hiểu để khắc phục các vấn đề SEO.

        **Hãy trả lời DUY NHẤT dưới dạng JSON theo cấu trúc sau. Đảm bảo tất cả các khóa và giá trị đều tuân thủ định dạng JSON hợp lệ, không có bất kỳ văn bản giải thích nào khác bên ngoài JSON.**

        **Cấu trúc JSON mong muốn (TUÂN THỦ CHÍNH XÁC CÁC TRƯỜNG VÀ KIỂU DỮ LIỆU NÀY):**
        ```json
        {{
          "summary": {{
            "url": "{request_data.url}",
            "overall_score": {request_data.overall_score},
            "critical_issues_count": {request_data.critical_issue},
            "warning_count": {request_data.warning},
            "opportunity_count": {request_data.opportunity}
          }},
          "advice": {{
            "critical_issues": [
              {{
                "issue_type": "Tên lỗi hoặc loại phần tử bị ảnh hưởng (Ví dụ: Thẻ <meta> bị thiếu nội dung)",
                "importance": "Giải thích ngắn gọn tại sao lỗi này quan trọng và ảnh hưởng đến SEO (ngôn ngữ đơn giản).",
                "fix_steps": [
                  "Bước 1: Hướng dẫn hành động cụ thể và dễ hiểu.",
                  "Bước 2: Hướng dẫn tiếp theo.",
                  "...",
                  "Gom nhóm các lỗi giống nhau lại và chỉ đưa ra một hướng dẫn chung cho loại lỗi đó."
                ],
                "affected_urls": [
                  "Liệt kê các URL cụ thể bị ảnh hưởng bởi lỗi này. Nếu quá nhiều, có thể ghi 'Xem chi tiết trong báo cáo đầy đủ' hoặc chỉ liệt kê một vài ví dụ hàng đầu.",
                  "..."
                ],
                "example_error_detail": {{
                   // (TUỲ CHỌN) Sao chép chi tiết một lỗi cụ thể từ "failed_elements" để làm ví dụ minh họa
                   // ví dụ: {{ "id": 7, "element": "meta", "description": "Thẻ <meta> không có thuộc tính content hoặc nội dung bị rỗng." }}
                }}
              }}
            ],
            "warnings": [
              {{
                "issue_type": "Tên lỗi hoặc loại phần tử bị ảnh hưởng (Ví dụ: Thẻ <script> không có src)",
                "importance": "Giải thích ngắn gọn tầm quan trọng của cảnh báo này.",
                "fix_steps": [
                  "Bước 1: Hướng dẫn khắc phục cụ thể và dễ hiểu.",
                  "...",
                  "Gom nhóm các lỗi giống nhau lại."
                ],
                "affected_urls": [
                  "Liệt kê các URL bị ảnh hưởng."
                ]
              }}
            ],
            "opportunities": [
              {{
                "issue_type": "Tên cơ hội cải thiện (Ví dụ: Thẻ <button> không có nội dung)",
                "importance": "Giải thích tại sao đây là một cơ hội để tối ưu hóa.",
                "fix_steps": [
                  "Bước 1: Hướng dẫn cải thiện cụ thể và dễ hiểu.",
                  "...",
                  "Gom nhóm các lỗi giống nhau lại."
                ],
                "affected_urls": [
                  "Liệt kê các URL bị ảnh hưởng."
                ]
              }}
            ]
          }},
          "next_steps_message": "Sau khi bạn đã thực hiện các chỉnh sửa này, hãy chạy lại công cụ kiểm tra SEO của chúng tôi để xem điểm số của bạn đã cải thiện như thế nào và xác nhận các lỗi đã được khắc phục. Chúng tôi sẽ giúp bạn theo dõi tiến độ!"
        }}
        ```

        **LƯU Ý QUAN TRỌNG:**
        -   Đối với mỗi loại lỗi (critical_issues, warnings, opportunities), nếu không có lỗi nào thuộc loại đó, hãy trả về một mảng rỗng (ví dụ: `"critical_issues": []`).
        -   Hãy cố gắng gom nhóm các lỗi có cùng `element` và `description` vào cùng một mục `issue_type` để người dùng dễ theo dõi.
        -   Sắp xếp thứ tự các lỗi trong mỗi danh mục dựa trên `important` (nếu có) hoặc mức độ phổ biến.
        -   Hãy thay thế các giá trị placeholder như `"Tên lỗi hoặc loại phần tử..."` bằng nội dung thực tế dựa trên dữ liệu `failed_elements`.
        """
    )

    if 'model' not in globals():
        raise RuntimeError(
            "Google Gemini model not initialized. Please ensure 'genai.configure' and 'model = genai.GenerativeModel(...)' are set up.")

    try:
        gemini_response = model.generate_content(
            contents=prompt,
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=2048,
                temperature=0.7
            )
        )

        advisor_text = ""
        if gemini_response and gemini_response.candidates:
            advisor_text = gemini_response.candidates[0].content.parts[0].text
        elif gemini_response and hasattr(gemini_response, 'text'):
            advisor_text = gemini_response.text

        # Cần làm sạch chuỗi JSON nếu nó kèm theo markdown code block
        json_str = advisor_text.strip()
        if json_str.startswith("```json") and json_str.endswith("```"):
            json_str = json_str[len("```json"):-len("```")].strip()
        
        # Dùng json.loads để parse chuỗi JSON thành dictionary
        response_data = json.loads(json_str)

        # Sử dụng hàm deserialize_to_dataclass để chuyển đổi dictionary thành SEOAdvisorResponse
        response_entity = deserialize_to_dataclass(SEOAdvisorResponse, response_data)

        return response_entity

    except json.JSONDecodeError as e:
        print(f"Lỗi JSONDecodeError từ phản hồi của Gemini (có thể do AI trả về JSON không hợp lệ): {e}", file=sys.stderr)
        print(f"Phản hồi thô từ Gemini: {advisor_text}", file=sys.stderr)
        raise # Ném lại ngoại lệ

    except Exception as e:
        print(f"Đã xảy ra lỗi không mong đợi khi gọi Gemini API hoặc xử lý phản hồi (sau JSONDecodeError): {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise