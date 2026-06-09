from typing import Annotated, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Body, Depends, Query, status

from src.api.dependencies import CurrentUser, get_current_user, get_post_service
from src.api.schemas import PostCreate, PostListResponse, PostResponse, PostUpdate
from src.services.post_service import PostService

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)



@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пост",
    description=(
        "Нужна авторизация (кнопка **Authorize** → только значение токена, без слова Bearer). "
        "В JSON после строки `text` обязательна **запятая** перед `media` "
        "(запятая внутри «Привет, лента!» — часть текста, не разделитель полей)."
    ),
)
async def create_post(
    data: Annotated[
        PostCreate,
        Body(
            openapi_examples={
                "with_image": {
                    "summary": "Текст + изображение",
                    "value": {
                        "text": "Привет, лента!",
                        "media": [
                            {
                                "type": "image",
                                "url": "http://localhost:9000/media/posts/img1.jpg",
                            }
                        ],
                    },
                },
                "text_only": {
                    "summary": "Только текст",
                    "value": {"text": "Только текст", "media": []},
                },
            },
        ),
    ],
    user: CurrentUser = Depends(get_current_user),
    service: PostService = Depends(get_post_service),
):
    return await service.create(user.id, data)


@router.get("", response_model=PostListResponse)
async def list_posts(
    author_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", pattern="^(created_at|likes_quantity|comments_quantity)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    service: PostService = Depends(get_post_service),
):
    items, total = await service.list_posts(
        author_id=author_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        created_after=created_after,
        created_before=created_before
    )
    return PostListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    service: PostService = Depends(get_post_service),
):
    return await service.get_by_id(post_id)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    data: PostUpdate,
    user: CurrentUser = Depends(get_current_user),
    service: PostService = Depends(get_post_service),
):
    return await service.update(post_id, user.id, data)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: PostService = Depends(get_post_service),
):
    await service.delete(post_id, user.id)

@router.post("/{post_id}/like", status_code=status.HTTP_200_OK)
async def like_post(
    post_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: PostService = Depends(get_post_service),
):
    return await service.like(post_id, str(user.id))


@router.delete("/{post_id}/like", status_code=status.HTTP_200_OK)
async def unlike_post(
    post_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: PostService = Depends(get_post_service),
):
    return await service.unlike(post_id, str(user.id))


@router.patch("/{post_id}/inc-comments")
async def increment_post_comments(
    post_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: PostService = Depends(get_post_service),
):
    """Увеличить счётчик комментариев поста (внутренний эндпоинт для BFF)"""
    result = await service.increment_comments(post_id)
    if not result:
        raise HTTPException(404, "Post not found")
    return result


@router.patch("/{post_id}/dec-comments")
async def decrement_post_comments(
    post_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: PostService = Depends(get_post_service),
):
    """Уменьшить счётчик комментариев поста (внутренний эндпоинт для BFF)"""
    result = await service.decrement_comments(post_id)
    if not result:
        raise HTTPException(404, "Post not found or comments_quantity is 0")
    return result


