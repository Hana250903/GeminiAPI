from dataclasses import asdict
import sys
from flask import Flask, request, jsonify
from flasgger import Swagger, swag_from
import google.generativeai as genai
from deserialize import deserialize_to_dataclass
from keyword_utils import generate_and_send_keywords
from rank_tracking import rank_tracking, update_rank_tracking, RankTrackingRequest, UpdateRankTrackingRequest
from top_ranking import top_ranking
from seo_advisor import seo_advisor, AuditRequestModel
from content_optimization import optimize_content as optimize_content_func
from content_optimization import ContentOptimizationRequest
from functools import wraps
from chat_box import ask_gemini as gemini_service
from chat_box_hcm import ask_gemini as gemini_service_hcm
from chat_box_vrn import ask_gemini as gemini_service_vrn

import os

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'SEO Boost AI API',
    'uiversion': 3,
    "specs_route": "/swagger/"
}
swagger = Swagger(app)

# Configure Gemini API
# GEMINI_API_KEY = "AIzaSyAFCZLK0Vr0mDLPcOFyDy8H7SWAl2vSb1A"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Internal API key for Flask
# FLASK_INTERNAL_API_KEY = "super-secret-ai-key"
# FLASK_INTERNAL_API_KEY = os.getenv("FLASK_INTERNAL_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# def require_internal_api_key(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth_header = request.headers.get("X-API-KEY")
#         if not auth_header or auth_header != FLASK_INTERNAL_API_KEY:
#             return jsonify({"error": "Unauthorized"}), 401
#         return f(*args, **kwargs)
#     return decorated

# BE
@app.route('/generate-seo-keywords', methods=['POST'])
def generate_seo_keywords():
    """
    Generates SEO keywords and sends them to external API.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            input_keyword:
              type: string
              example: seo
    responses:
      200:
        description: Keywords generated and sent successfully.
      400:
        description: Invalid input.
      500:
        description: Internal server error.
    """
    try:
        data = request.get_json()
        input_keyword = data.get('input_keyword')

        if not input_keyword:
            return jsonify({"error": "Missing 'input_keyword' in request body."}), 400

        result = generate_and_send_keywords(input_keyword)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"API Error: {str(e)}"}), 500

# BE
@app.route('/rank-tracking', methods=['POST'])
def generate_rank_tracking():
    """
    Generates Rank Tracking and sends them to external API.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            input_keyword:
              type: string
              example: seo
            user_id:
              type: integer
              example: 0
    responses:
      200:
        description: Keywords generated and sent successfully.
      400:
        description: Invalid input.
      500:
        description: Internal server error.
    """
    try:
        data = request.get_json()
        input_keyword = data.get('input_keyword')
        user = data.get('user_id')

        if not input_keyword or not user:
            return jsonify({"error": "Missing 'input_keyword' or 'user_id' in request body."}), 400

        # Assuming user ID is 2 for this example
        result = rank_tracking(input_keyword, user)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"API Error: {str(e)}"}), 500


@app.route('/top-ranking', methods=['POST'])
def generate_top_ranking():
    """
    Generates Rank Tracking and sends them to external API.
    ---
    responses:
      200:
        description: Keywords generated and sent successfully.
      400:
        description: Invalid input.
      500:
        description: Internal server error.
    """
    try:
        result = top_ranking()  # Assuming this function does not require any input parameters
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"API Error: {str(e)}"}), 500

# BE
@app.route('/seo-advisor', methods=['POST'])
def generate_seo_advisor():
    """
    Generates seo advisor and sends them to external API.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            user_id:
              type: integer
              example: 1
            url:
              type: string
              example: "https://example.com"
            overall_score:
              type: integer
              example: 85
            critical_issue:
              type: integer
              example: 2
            warning:
              type: integer
              example: 1
            opportunity:
              type: integer
              example: 3
            passed_check:
              type: string
              example: "All checks passed"
            failed_elements:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  url:
                    type: string
                    example: "https://example.com/page"
                  element:
                    type: string
                    example: "title"
                  current_value:
                    type: string
                    example: "Example Title"
                  status:
                    type: string
                    example: "not pass"
                  important:
                    type: integer
                    example: 1
                  description:
                    type: string
                    example: "Title is too short"
                  audit_repost_id:
                    type: integer
                    example: 1
                    nullable: true # Thêm nullable: true để chỉ rõ trường này có thể là null (OpenAPI 3.0+)
                required:
                  - id
                  - url
                  - element
                  - current_value
                  - status
                  - important
                  - description
          required:
            - id
            - user_id
            - url
            - overall_score
            - critical_issue
            - warning
            - opportunity
            - passed_check
            - failed_elements
    responses:
      200:
        description: SEO Advisor response generated successfully.
      400:
        description: Invalid input. (e.g., request body doesn't conform to schema, missing required fields)
      500:
        description: Internal server error. (e.g., API call to Gemini failed, unexpected error during processing)
    """
    try:
        data = request.get_json(silent=True)

        if data is None:
            return jsonify({
                "error": "Missing or invalid JSON in request body.",
                "details": "Ensure 'Content-Type: application/json' header is set and the body is valid JSON."
            }), 400
        
        # --- SỬ DỤNG deserialize_to_dataclass Ở ĐÂY ---
        try:
            request_data = deserialize_to_dataclass(AuditRequestModel, data)

        except (TypeError, KeyError, ValueError) as e:
            return jsonify({
                "error": "Invalid input data format or missing required fields for AuditRequest.",
                "details": str(e)
            }), 400
        
        seo_response_entity = seo_advisor(request_data)

        return jsonify(asdict(seo_response_entity)), 200

    except Exception as e:
        print(f"An unhandled internal server error occurred: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."}), 500

# BE
@app.route('/update-rank-tracking', methods=['POST'])
def update_rank_tracking_with_id():
    """
    Updates Rank Tracking and sends them to external API.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: array
          items:
            type: object
            properties:
              input_keyword:
                type: string
                example: seo
              id:
                type: string
                example: "5"
              old_rank:
                type: integer
                example: 10
    responses:
      200:
        description: Rank trackings updated successfully.
      400:
        description: Invalid input.
      500:
        description: Internal server error.
    """
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({"error": "Expected a list of rank tracking requests."}), 400

        request_data = [
            UpdateRankTrackingRequest(input_keyword=item.get(
                "input_keyword"), id=item.get("id"), old_rank=item.get("old_rank"))
            for item in data
            if item.get("input_keyword") and item.get("id") and item.get("old_rank") is not None
        ]

        if not request_data:
            return jsonify({"error": "No valid requests found in the input."}), 400

        result = update_rank_tracking(request_data)

        return jsonify({
            "message": "Batch processed.",
            "result_count": len(result),
            "details": result
        }), 200

    except Exception as e:
        return jsonify({"error": f"API Error: {str(e)}"}), 500

# BE
@app.route('/optimize-content', methods=['POST'])
# @require_internal_api_key
def optimize_content():
    """
    Optimize content and sends them to external API.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            user_id:
              type: integer
              example: 1
            keyword:
              type: string
              example: "seo"
            content:
              type: string
              example: "This is the original content to be optimized."
            content_length:
              type: string
              example: "short"
            optimization_level:
              type: integer
              example: 3
            readability_level:
              type: string
              example: "high"
            include_citation:
              type: boolean
              example: true
    responses:
      200:
        description: Optimization successful.
      400:
        description: Invalid input.
      500:
        description: Internal server error.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Missing input data."}), 400

        # Sử dụng **data để khởi tạo dataclass gọn gàng hơn
        # Tuy nhiên, cần bắt lỗi nếu thiếu trường hoặc sai kiểu
        try:
            request_data = ContentOptimizationRequest(
                id=data.get('id'),
                user_id=data.get('user_id'),
                keyword=data.get('keyword'),
                content=data.get('content'),
                content_length=data.get('content_length'),
                optimization_level=data.get('optimization_level'),
                readability_level=data.get('readability_level'),
                include_citation=data.get('include_citation')
            )
            # Hoặc gọn hơn với validation mạnh mẽ:
            # request_data = ContentOptimizationRequest(**data)
            # (Nhưng cần đảm bảo tất cả các trường trong data đều có và đúng kiểu,
            # nếu không sẽ gây TypeError/ValidationError)

        except Exception as e:  # Bắt lỗi khi tạo ContentOptimizationRequest
            return jsonify({"error": f"Invalid input data for ContentOptimizationRequest: {str(e)}"}), 400

        # Gọi hàm xử lý chính (tôi giả định hàm của bạn tên là optimize_content_func
        # để tránh trùng tên với endpoint Flask)
        # <--- Đổi tên hàm thành optimize_content_func
        result = optimize_content_func(request_data)

        return jsonify(result), 200

    except Exception as e:
        # Ghi log lỗi ra console để debug
        print(f"Error in /optimize-content: {str(e)}")
        return jsonify({"error": f"API Error: {str(e)}"}), 500

# --- Gemini Chat Endpoint ---
@app.route('/ask_gemini', methods=['POST'])
@swag_from({
    'tags': ['Gemini AI Chat'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'question': {
                        'type': 'string',
                        'example': 'Sứ mệnh của giai cấp công nhân thể hiện ở những khía cạnh nào?'
                    }
                },
                'required': ['question']
            }
        }
    ],
    'consumes': ['application/json'],
    'produces': ['application/json'],
    'responses': {
        200: {
            'description': 'Phản hồi từ AI',
            'examples': {
                'application/json': {
                    'answer': 'Chào bạn! Tôi có thể giúp gì?'
                }
            }
        },
        400: {
            'description': 'Thiếu dữ liệu question'
        },
        500: {
            'description': 'Lỗi nội bộ server'
        }
    }
})
def ask_gemini():
    data = request.get_json(silent=True)
    if not data or 'question' not in data:
        return jsonify({"error": "Vui lòng cung cấp 'question' trong request body."}), 400

    user_question = data.get('question')

    try:
        response = gemini_service(user_question)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask_gemini_hcm', methods=['POST'])
@swag_from({
    'tags': ['Gemini AI Chat HCM'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'question': {
                        'type': 'string',
                        'example': ''
                    }
                },
                'required': ['question']
            }
        }
    ],
    'consumes': ['application/json'],
    'produces': ['application/json'],
    'responses': {
        200: {
            'description': 'Phản hồi từ AI',
            'examples': {
                'application/json': {
                    'answer': 'Chào bạn! Tôi có thể giúp gì?'
                }
            }
        },
        400: {
            'description': 'Thiếu dữ liệu question'
        },
        500: {
            'description': 'Lỗi nội bộ server'
        }
    }
})
def ask_gemini_hcm():
    data = request.get_json(silent=True)
    if not data or 'question' not in data:
        return jsonify({"error": "Vui lòng cung cấp 'question' trong request body."}), 400

    user_question = data.get('question')

    try:
        response = gemini_service_hcm(user_question)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask_gemini_vnr', methods=['POST'])
@swag_from({
    'tags': ['Gemini AI Chat VRN'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'question': {
                        'type': 'string',
                        'example': ''
                    }
                },
                'required': ['question']
            }
        }
    ],
    'consumes': ['application/json'],
    'produces': ['application/json'],
    'responses': {
        200: {
            'description': 'Phản hồi từ AI',
            'examples': {
                'application/json': {
                    'answer': 'Chào bạn! Tôi có thể giúp gì?'
                }
            }
        },
        400: {
            'description': 'Thiếu dữ liệu question'
        },
        500: {
            'description': 'Lỗi nội bộ server'
        }
    }
})
def ask_gemini_vrn():
    data = request.get_json(silent=True)
    if not data or 'question' not in data:
        return jsonify({"error": "Vui lòng cung cấp 'question' trong request body."}), 400

    user_question = data.get('question')

    try:
        response = gemini_service_vrn(user_question)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def main():
    app.run(debug=True, port=5001)

if __name__ == "__main__":
    main()
