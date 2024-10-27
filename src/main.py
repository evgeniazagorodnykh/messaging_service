from typing import List
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend
# from redis import asyncio as aioredis

from auth.base_config import auth_backend, fastapi_users
from auth.models import User
from auth.schemas import UserRead, UserCreate, UserUpdate
from chat.router import router as router_chat
from database import get_async_session


app = FastAPI(
    title="Messagind Servis"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory='templates')

# Зависимость для получения текущего пользователя, возвращающая None, если пользователь не авторизован
async def get_current_user_optional(
    current_user: User = Depends(fastapi_users.current_user(optional=True))
):
    return current_user

# Главная страница, перенаправляющая на /auth, если пользователь не авторизован
@app.get("/", response_class=HTMLResponse, summary="Главная страница чата")
async def main_page(request: Request, current_user: User = Depends(get_current_user_optional)):
    if current_user is None:
        return RedirectResponse(url="/auth")
    return templates.TemplateResponse("chat.html", {"request": request, "user": current_user})

# Страница авторизации
@app.get("/auth", response_class=HTMLResponse, summary="Страница авторизации")
async def get_auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@app.get("/users", response_model=List[UserRead], tags=["Users"])
async def get_all_users(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_optional)
):
    if current_user is None:
        return RedirectResponse(url="/auth")

    result = await session.execute(select(User))
    users = result.scalars().all()
    return users


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["Users"],
)

app.include_router(router_chat)

# @app.on_event("startup")
# async def startup_event():
#     redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
#     FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
