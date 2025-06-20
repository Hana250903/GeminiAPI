from flask import Flask, request, jsonify
from flasgger import Swagger
import google.generativeai as genai
from keyword_utils import generate_and_send_keywords  # <--- import function bạn vừa tách
from rank_tracking import rank_tracking  # <--- import function bạn vừa tách
from top_ranking import top_ranking  # <--- import function bạn vừa tách
from seo_advisor import seo_advisor
import os

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'SEO Boost AI API',
    'uiversion': 3,
    "specs_route": "/swagger/"
}
swagger = Swagger(app)

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyAFCZLK0Vr0mDLPcOFyDy8H7SWAl2vSb1A"
#GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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

        result = rank_tracking(input_keyword, user)  # Assuming user ID is 2 for this example
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

def main():
    app.run(debug=True, port=5001)

if __name__ == "__main__":
    main()
