from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from config import settings
from src.api.routes import (
    track_create_page,
    social,
    music_social,
    post_create_page,
    post_feed,
    music_feed,
    track_page,
    post_page,
    user_profile,
    album_page,
    search,
    auth
)

# ========== СОЗДАНИЕ ПРИЛОЖЕНИЯ ==========

app = FastAPI(
    title="BFF API Gateway",
    description="Backend For Frontend для музыкального сервиса",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# ========== CORS НАСТРОЙКИ ==========

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if hasattr(settings, 'CORS_ORIGINS') else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== СТАТИЧЕСКИЕ ФАЙЛЫ ==========

app.mount("/static", StaticFiles(directory="static"), name="static")


# ========== HTML СТРАНИЦА ДЛЯ ТЕСТИРОВАНИЯ ==========
@app.get("/test/login", response_class=HTMLResponse)
async def test_login_page():
    """Страница ввода токена"""
    try:
        with open("static/login.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>404</h1><p>File not found</p>", status_code=404)
@app.get("/test/album-create", response_class=HTMLResponse)
async def test_album_create_page():
    """Страница для тестирования создания альбома"""
    try:
        with open("static/album_create.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>404</h1><p>File not found. Please create static/album_create.html</p>", 
            status_code=404
        )

@app.get("/test/post-create", response_class=HTMLResponse)
async def test_post_create_page():
    try:
        with open("static/post_create.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>404</h1><p>File not found</p>", status_code=404)


@app.get("/test/feed", response_class=HTMLResponse)
async def test_feed_page():
    try:
        with open("static/feed.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>404</h1><p>File not found</p>", status_code=404)


@app.get("/test", response_class=HTMLResponse)
async def test_home_page():
    """Главная страница с рекомендациями"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>404</h1><p>File not found</p>", status_code=404)

@app.get("/track/{track_id}", response_class=HTMLResponse)
async def test_home_page():
    """Главная страница с рекомендациями"""
    try:
        with open("static/track.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>404</h1><p>File not found</p>", status_code=404)

# ========== ПОДКЛЮЧЕНИЕ РОУТЕРОВ ==========

app.include_router(track_create_page.router, prefix="/api/v1")
app.include_router(social.router, prefix="/api/v1")
app.include_router(music_social.router, prefix="/api/v1")
app.include_router(post_create_page.router, prefix="/api/v1")
app.include_router(post_feed.router, prefix="/api/v1")
app.include_router(music_feed.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(album_page.router, prefix="/api/v1")
app.include_router(track_page.router, prefix="/api/v1")
app.include_router(user_profile.router, prefix="/api/v1")
app.include_router(post_page.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")


# ========== КОРНЕВОЙ ЭНДПОИНТ ==========

@app.get("/")
async def root():
    return {
        "service": "BFF API Gateway",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health",
        "test_ui": "/test/album-create"
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}