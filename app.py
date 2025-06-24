from flask import Flask, request, jsonify
from flasgger import Swagger
import google.generativeai as genai
from keyword_utils import generate_and_send_keywords
from rank_tracking import rank_tracking, update_rank_tracking, RankTrackingRequest
from top_ranking import top_ranking
from seo_advisor import seo_advisor
from content_optimization import optimize_content as optimize_content_func
from content_optimization import ContentOptimizationRequest
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

genai.configure(api_key=GEMINI_API_KEY)


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


@app.route('/seo-advisor', methods=['POST'])
def generate_seo_advisor():
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
        result = seo_advisor()  # Assuming this function does not require any input parameters
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"API Error: {str(e)}"}), 500


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
            RankTrackingRequest(input_keyword=item.get(
                "input_keyword"), id=item.get("id"))
            for item in data
            if item.get("input_keyword") and item.get("id") is not None
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


@app.route('/optimize-content', methods=['POST'])
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

        except Exception as e: # Bắt lỗi khi tạo ContentOptimizationRequest
            return jsonify({"error": f"Invalid input data for ContentOptimizationRequest: {str(e)}"}), 400

        # Gọi hàm xử lý chính (tôi giả định hàm của bạn tên là optimize_content_func
        # để tránh trùng tên với endpoint Flask)
        result = optimize_content_func(request_data) # <--- Đổi tên hàm thành optimize_content_func

        return jsonify(result), 200

    except Exception as e:
        # Ghi log lỗi ra console để debug
        print(f"Error in /optimize-content: {str(e)}")
        return jsonify({"error": f"API Error: {str(e)}"}), 500


def main():
    app.run(debug=True, port=5001)


if __name__ == "__main__":
    main()
