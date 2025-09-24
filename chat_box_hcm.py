import google.generativeai as genai

ai_model = genai.GenerativeModel('gemini-2.0-flash')

def get_base_prompt_text():
    try:
        with open('tu_lieu_hcm.txt', 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "Không tìm thấy tài liệu gốc. Vui lòng cung cấp nội dung."

base_prompt = get_base_prompt_text()

def ask_gemini(user_question: str):
    full_prompt = f"""
        Bạn là một trợ lý AI. Nhiệm vụ của bạn là trả lời câu hỏi dựa duy nhất vào nội dung trong phần "Tài liệu tham khảo" bên dưới.
        Nếu trong tài liệu không có thông tin để trả lời, hãy nói rõ: 
        "Tôi không tìm thấy thông tin trong tài liệu để trả lời câu hỏi này."

        --- Tài liệu tham khảo ---
        {base_prompt}
        ---------------------------

        Câu hỏi: {user_question}
    """


    try:
        response = ai_model.generate_content(full_prompt)
        return {"answer": response.text}
    except Exception as e:
        return {"error": str(e)}, 500