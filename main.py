import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.app import create_app

# Khởi tạo ứng dụng FastAPI lõi từ gói api
app = create_app()

# Ép buộc hệ thống tự động xử lý mượt mà cả 2 trường hợp có/không có dấu / ở cuối
app.router.redirect_slashes = True

# Kích hoạt CORS đầy đủ để Frontend Next.js gọi vào không bị chặn phương thức
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/auth/login", methods=["POST", "OPTIONS"])
@app.api_route("/auth/login/", methods=["POST", "OPTIONS"])
async def vercel_login_bridge(request: dict | None = None):
    """
    Cầu nối tuyến đường bắt cứng để xử lý lỗi 405 trên môi trường Serverless.
    Chuyển tiếp trực tiếp logic xử lý sang luồng auth_service của hệ thống.
    """
    from services.auth_service import auth_service
    from fastapi import HTTPException
    
    # Đọc thông tin mật khẩu gửi lên từ body
    try:
        body = await request.json() if request else {}
        password = body.get("password", "")
    except Exception:
        # Hỗ trợ nếu dữ liệu gửi dạng form thay vì JSON object
        try:
            form_data = await request.form()
            password = form_data.get("password", "")
        except Exception:
            password = ""

    # Kiểm tra khớp mã khóa xác thực
    if auth_service.verify_password(password):
        token = auth_service.generate_token()
        return {"token": token, "status": "success"}
    
    raise HTTPException(status_code=401, detail="Mật khẩu không chính xác")
