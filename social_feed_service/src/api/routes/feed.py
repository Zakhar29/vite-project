from typing import Annotated, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Body, Depends, Query, status

from src.api.dependencies import CurrentUser, get_current_user, get_post_service
from src.api.schemas import PostCreate, PostListResponse, PostResponse, PostUpdate
from src.services.post_service import PostService

router = APIRouter(
    prefix="/feed",
    tags=["posts"],
)


@router.get("/recommendations", response_model=PostListResponse)
async def get_recommended_posts(
    following_ids: Optional[str] = Query(None, description="Список ID авторов через запятую"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: PostService = Depends(get_post_service),
):
    """
    Рекомендации постов для ленты.

    Если following_ids передан и не пуст:
        - Берём посты от подписанных авторов (свежие)
        - Добиваем популярными постами до limit
    Если following_ids не передан или пуст:
        - Возвращаем только популярные посты
    """

    # Парсим following_ids из строки в список
    author_ids = []
    if following_ids and following_ids.strip():
        try:
            for aid in following_ids.split(","):
                aid = aid.strip()
                if aid:
                    author_ids.append(UUID(aid))
        except ValueError as e:
            print(f"Warning: Invalid UUID in following_ids: {e}")

    all_posts = []
    seen_ids = set()

    # 1. Получаем посты от подписанных авторов (если есть)
    if author_ids:
        items, total = await service.list_posts_by_authors(
            author_ids=author_ids,
            skip=0,
            limit=limit,
            sort_by="created_at",
            sort_order="desc"
        )
        # items — это список словарей
        for post in items:
            post_id = post.get("id") if isinstance(post, dict) else getattr(post, "id", None)
            if post_id not in seen_ids:
                all_posts.append(post)
                seen_ids.add(post_id)

    # 2. Если нужно больше постов, добиваем популярными
    if len(all_posts) < limit:
        needed = limit - len(all_posts)
        items, total = await service.list_posts(
            skip=0,
            limit=needed,
            sort_by="likes_quantity",
            sort_order="desc"
        )
        for post in items:
            post_id = post.get("id") if isinstance(post, dict) else getattr(post, "id", None)
            if post_id not in seen_ids:
                all_posts.append(post)
                seen_ids.add(post_id)

    # Преобразуем в формат PostResponse если нужно
    # items уже должны быть в правильном формате из _serialize_post

    return PostListResponse(
        items=all_posts[:limit],
        total=len(all_posts),
        skip=skip,
        limit=limit
    )