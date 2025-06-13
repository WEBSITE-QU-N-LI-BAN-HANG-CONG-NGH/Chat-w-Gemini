# Hướng dẫn Cài đặt và Chạy Ứng dụng Chatbot AI

Dự án này là một ứng dụng web chatbot sử dụng Flask làm backend và tích hợp với Gemini API của Google để cung cấp khả năng trả lời tự động.

## Yêu cầu hệ thống

* Python 3.x
* `pip` (trình quản lý gói của Python)

## Các bước cài đặt

### 1. Tạo và kích hoạt môi trường ảo

Môi trường ảo giúp cô lập các gói phụ thuộc của dự án, tránh xung đột với các dự án khác trên máy của bạn.

**Trên macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Trên Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate
```

Sau khi kích hoạt, bạn sẽ thấy `(venv)` ở đầu dòng lệnh của mình.

### 2. Cài đặt các gói phụ thuộc

Tất cả các thư viện cần thiết được liệt kê trong file `requirements.txt`. Chạy lệnh sau để cài đặt chúng:

```bash
pip install -r requirements.txt
```

File này bao gồm các thư viện chính sau:
* `Flask`: Một micro web framework cho Python.
* `google-generativeai`: Thư viện chính thức của Google để tương tác với Gemini API.
* `python-dotenv`: Dùng để quản lý các biến môi trường.
* `flask-cors`: Một extension của Flask để xử lý Cross-Origin Resource Sharing (CORS).

### 3. Cấu hình biến môi trường

Ứng dụng cần một khóa API từ Google để có thể giao tiếp với mô hình Gemini.

1.  Tạo một file mới trong thư mục gốc của dự án và đặt tên là `.env`.
2.  Mở file `.env` và thêm vào nội dung sau:

    ```
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
    ```

3.  **Quan trọng:** Thay thế `"YOUR_GOOGLE_API_KEY"` bằng khóa API thực tế của bạn.

File `.gitignore` đã được cấu hình để bỏ qua thư mục `venv/` và bạn cũng nên thêm file `.env` vào đó để tránh việc đưa các thông tin nhạy cảm (như API key) lên git.

### 4. Chạy ứng dụng

Sau khi đã hoàn tất các bước trên, bạn có thể khởi động máy chủ Flask bằng lệnh:

```bash
python app.py
```

Nếu mọi thứ thành công, bạn sẽ thấy output tương tự như sau trong terminal, cho biết máy chủ đang chạy:

```
 * Serving Flask app 'app'
 * Debug mode: on
INFO:werkzeug: * Running on http://0.0.0.0:5006
Press CTRL+C to quit
INFO:werkzeug: * Restarting with stat
INFO:root:Đã cấu hình Gemini API Key và khởi tạo model thành công.
 * Debugger is active!
 * Debugger PIN: ...
```

Ứng dụng backend chatbot của bạn hiện đang chạy và sẵn sàng nhận các yêu cầu tại địa chỉ `http://localhost:5006`. Cụ thể, endpoint cho việc chat là `/api/chat`.

## Cấu trúc dự án

* `app.py`: File chính của ứng dụng Flask, xử lý logic API và giao tiếp với Gemini.
* `requirements.txt`: Liệt kê các gói Python cần thiết cho dự án.
* `.env`: Chứa các biến môi trường (cần được tạo thủ công).
* `.gitignore`: Chỉ định các file và thư mục mà Git nên bỏ qua.
* `venv/`: Thư mục chứa môi trường ảo (được tạo sau bước cài đặt).
