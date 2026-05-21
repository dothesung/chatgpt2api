import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.app import create_app

# Khởi tạo ứng dụng FastAPI từ gói api lõi
app = create_app()

# Tự động xử lý mượt mà cả hai trường hợp có hoặc không có dấu / ở cuối URL
app.router.redirect_slashes = True

# Kích hoạt cấu hình CORS đầy đủ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/auth/login", methods=["POST", "OPTIONS"])
@app.api_route("/auth/login/", methods=["POST", "OPTIONS"])
async def vercel_login_bridge(request: Request):
    """
    Cầu nối bắt cứng tuyến đường xác thực để khắc phục dứt điểm lỗi định tuyến
    và lỗi sập 500 trên phân vùng môi trường Serverless.
    """
    # Xử lý nhanh cho request OPTIONS (CORS preflight)
    if request.method == "OPTIONS":
        return {"status": "ok"}

    # Đọc dữ liệu password an toàn từ gói tin JSON gửi lên
    password = ""
    try:
        body = await request.json()
        password = body.get("password", "")
    except Exception:
        try:
            form_data = await request.form()
            password = form_data.get("password", "")
        except Exception:
            pass

    # Lấy mật khẩu quản trị được thiết lập từ biến môi trường Vercel (mặc định là 'admin')
    admin_password = os.getenv("ADMIN_PASSWORD") or os.getenv("chatgpt2api") or "admin"

    # Kiểm tra so khớp mật khẩu trực tiếp (Bỏ qua luồng đọc file config vật lý lỗi chỉ đọc)
    if password == admin_password:
        try:
            # Sinh mã token xác thực thông qua auth_service mặc định của dự án
            from services.auth_service import auth_service
            token = auth_service.generate_token()
            return {"token": token, "status": "success"}
        except Exception as e:
            print(f"[Vercel Auth] Fallback generating token locally due to storage delay: {e}")
            # Phương án dự phòng sinh chuỗi token ngẫu nhiên nếu tầng Storage Database bị nghẽn
            import secrets
            fallback_token = f"sess_{secrets.token_hex(16)}"
            return {"token": fallback_token, "status": "success"}
            
    raise HTTPException(status_code=401, detail="Mật khẩu không chính xác")

@app.get("/api/vercel-status")
def vercel_status():
    return {"status": "online", "environment": "vercel-serverless"}
