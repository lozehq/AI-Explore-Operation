from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from dotenv import load_dotenv
from config import SECURITY_CONFIG
from routers import analysis, bilibili
import logging
import os
import httpx
import asyncio
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent
STATIC_DIR = ROOT_DIR / "static"
TEMPLATES_DIR = ROOT_DIR / "templates"

# 确保目录存在
STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

logger.debug(f"Templates directory: {TEMPLATES_DIR.absolute()}")
logger.debug(f"Static directory: {STATIC_DIR.absolute()}")

# 创建FastAPI应用
app = FastAPI(
    title="内容分析API",
    description="基于AI的内容分析服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 配置模板
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
logger.debug(f"Template files: {list(TEMPLATES_DIR.glob('*.html'))}")

# 注册路由
app.include_router(analysis.router)
app.include_router(bilibili.router)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    if not isinstance(response, JSONResponse):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    return response

@app.middleware("http")
async def cookie_middleware(request: Request, call_next):
    response = await call_next(request)
    if isinstance(response, JSONResponse):
        origin = request.headers.get("origin", "")
        if origin in origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

async def proxy_image(url: str) -> Optional[StreamingResponse]:
    """代理图片请求"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.bilibili.com",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        
        async with httpx.AsyncClient(verify=False, timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            # 获取正确的内容类型
            content_type = response.headers.get("content-type", "image/jpeg")
            if not content_type.startswith("image/"):
                content_type = "image/jpeg"
            
            # 设置响应头
            headers = {
                "Cache-Control": "public, max-age=31536000",
                "Access-Control-Allow-Origin": "*",
                "Content-Type": content_type,
                "Content-Length": str(len(response.content)),
                "X-Frame-Options": "DENY",
                "X-Content-Type-Options": "nosniff"
            }
            
            return StreamingResponse(
                content=response.iter_bytes(),
                headers=headers,
                media_type=content_type
            )
    except Exception as e:
        logger.error(f"Failed to proxy image {url}: {str(e)}")
        return None

@app.get("/proxy/image/{path:path}")
async def get_proxied_image(path: str, request: Request):
    """处理图片代理请求"""
    try:
        # 解码URL
        from urllib.parse import unquote
        url = unquote(path)
        
        # 如果URL不完整，添加协议
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        # 检查URL是否是B站域名
        if not any(domain in url.lower() for domain in ['bilibili.com', 'hdslb.com']):
            raise ValueError("只允许代理B站图片")
        
        response = await proxy_image(url)
        if response:
            return response
        else:
            # 如果代理失败，返回默认头像
            default_avatar = STATIC_DIR / "default-avatar.png"
            if not default_avatar.exists():
                with open(default_avatar, 'wb') as f:
                    f.write(b'')  # 创建空文件
            return FileResponse(
                default_avatar,
                media_type='image/png',
                headers={
                    "Cache-Control": "public, max-age=31536000",
                    "Access-Control-Allow-Origin": "*"
                }
            )
    except Exception as e:
        logger.error(f"Image proxy error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.get("/favicon.ico")
async def get_favicon():
    """返回网站图标"""
    favicon_path = STATIC_DIR / "favicon.ico"
    if not favicon_path.exists():
        # 如果favicon不存在，创建一个空的favicon
        favicon_path.write_bytes(b"")
    return FileResponse(favicon_path)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """返回主页"""
    logger.debug("Rendering index.html template")
    try:
        response = templates.TemplateResponse("index.html", {"request": request})
        logger.debug("Template rendered successfully")
        return response
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.options("/{path:path}")
async def options_route(request: Request, path: str):
    """处理 OPTIONS 请求"""
    origin = request.headers.get("origin", "")
    response = Response()
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Cookie"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Expose-Headers"] = "Set-Cookie"
    return response

# 添加健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}

# 确保在 Vercel 环境中正确运行
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)