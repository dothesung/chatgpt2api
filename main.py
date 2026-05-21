from api.app import create_app

app = create_app()

# Kích hoạt cấu hình bỏ qua nghiêm ngặt dấu gạch chéo ở cuối đường dẫn
app.router.redirect_slashes = True

@app.get("/api/vercel-status")
def vercel_status():
    return {"status": "online", "environment": "vercel-serverless"}
