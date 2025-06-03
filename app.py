from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()

app = Flask(__name__)
CORS(app) 

gemini_api_key = os.getenv("GOOGLE_API_KEY")
gemini_model = None # Khởi tạo là None

if not gemini_api_key:
    app.logger.error("สำคัญ: GOOGLE_API_KEY không được tìm thấy trong biến môi trường. Dịch vụ AI sẽ không hoạt động.")
else:
    try:
        genai.configure(api_key=gemini_api_key)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest') # Hoặc model bạn chọn
        app.logger.info("Đã cấu hình Gemini API Key và khởi tạo model thành công.")
    except Exception as e:
        app.logger.error(f"Lỗi khi cấu hình Gemini API hoặc khởi tạo model: {e}")
        # gemini_model sẽ vẫn là None

@app.route("/api/chat", methods=["POST"])
def chat_handler():
    # Kiểm tra xem API key và model đã được cấu hình và khởi tạo thành công ở lúc đầu chưa
    if not gemini_api_key: # Kiểm tra biến key đã đọc từ .env
        app.logger.error("API call attempted but GOOGLE_API_KEY was not found during startup.")
        return jsonify([{"text": "Lỗi máy chủ: Dịch vụ AI chưa được cấu hình (thiếu API key)."}]), 500
    
    if gemini_model is None: # Kiểm tra xem model đã được khởi tạo thành công chưa
        app.logger.error("API call attempted but Gemini model was not initialized successfully during startup.")
        return jsonify([{"text": "Lỗi máy chủ: Mô hình AI không khả dụng (lỗi khởi tạo)."}]), 500
        
    try:
        data = request.get_json()
        if not data:
            app.logger.warning("Request không có JSON body.")
            return jsonify({"error": "Request body phải là JSON"}), 400

        user_message_content = data.get("message")
        messages_history_from_frontend = data.get("history", []) 

        if not user_message_content:
            app.logger.warning("Không có 'message' trong JSON payload.")
            return jsonify({"error": "Không có tin nhắn nào được cung cấp ('message' field is missing)"}), 400

        app.logger.info(f"Nhận tin nhắn: '{user_message_content}' với {len(messages_history_from_frontend)} tin nhắn lịch sử.")

        gemini_conversation_history = []
        recent_history = messages_history_from_frontend[-(8 if len(messages_history_from_frontend) > 8 else len(messages_history_from_frontend)):]

        for msg in recent_history:
            content = msg.get("content", "") 
            sender = msg.get("sender")
            if sender == "bot" and "Tôi là trợ lý Tech Shop AI" in content and recent_history.index(msg) == 0 and len(recent_history) > 1:
                app.logger.info("Bỏ qua tin nhắn chào mừng của bot trong lịch sử.")
                continue
            role = "user" if sender == "user" else "model"
            gemini_conversation_history.append({
                "role": role,
                "parts": [{"text": content}] 
            })
        
        app.logger.debug(f"Lịch sử gửi cho Gemini: {gemini_conversation_history}")

        chat_session = gemini_model.start_chat(history=gemini_conversation_history)
        
        safety_settings_config = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        response = chat_session.send_message(user_message_content, safety_settings=safety_settings_config)
        
        app.logger.info("Đã nhận phản hồi từ Gemini.")
        bot_response_text = ""

        if response and hasattr(response, 'parts') and response.parts:
            bot_response_text = "".join(part.text for part in response.parts if hasattr(part, 'text'))
        elif response and hasattr(response, 'text') and response.text:
             bot_response_text = response.text
        elif response and hasattr(response, 'prompt_feedback') and response.prompt_feedback and hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
            block_reason = response.prompt_feedback.block_reason
            block_reason_message = getattr(response.prompt_feedback, 'block_reason_message', None) or str(block_reason)
            bot_response_text = f"Yêu cầu của bạn đã bị chặn vì lý do an toàn: {block_reason_message}"
            app.logger.warning(f"Gemini prompt blocked: {block_reason}. Message: {block_reason_message}")
        else:
            try:
                if response and response._result and response._result.candidates and response._result.candidates[0].content and response._result.candidates[0].content.parts:
                    bot_response_text = response._result.candidates[0].content.parts[0].text
                else:
                    raise AttributeError("Cấu trúc response không như mong đợi.")
            except (AttributeError, IndexError, TypeError) as e:
                bot_response_text = "Xin lỗi, tôi không thể tạo phản hồi lúc này (phản hồi không có nội dung text)."
                app.logger.error(f"Cấu trúc phản hồi không mong đợi từ Gemini hoặc không có text: {response}, lỗi: {e}")
        
        app.logger.info(f"Phản hồi của Bot: '{bot_response_text}'")
        return jsonify([{"text": bot_response_text}])

    except Exception as e:
        app.logger.error(f"Lỗi không mong muốn trong chat_handler: {e}", exc_info=True)
        return jsonify([{"text": "Xin lỗi, tôi đang gặp sự cố hệ thống và không thể phản hồi lúc này."}]), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=True)