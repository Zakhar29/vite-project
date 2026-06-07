from typing import Annotated, Optional
from fastapi import APIRouter, Body, Depends, Query, status

from src.api.dependencies import CurrentUser, get_current_user
from src.api.schemas import (
    TrackCommentCreate,
    TrackCommentListResponse,
    TrackCommentResponse,
    TrackCommentUpdate,
)
from src.services.comment_service import CommentService

router = APIRouter(prefix="/tracks", tags=["track-comments"])


def get_comment_service() -> CommentService:
    return CommentService()


@router.get(
    "/{track_id}/comments",
    response_model=TrackCommentListResponse,
    summary="Список комментариев к треку",
)
async def list_track_comments(
    track_id: str,
    root_only: bool = Query(True, description="Только корневые комментарии"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    timecode_from: Optional[int] = Query(None, ge=0),
    timecode_to: Optional[int] = Query(None, ge=0),
    sort_by: str = Query("created_at", pattern="^(created_at|likes_quantity|rating_quantity|track_timecode)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    service: CommentService = Depends(get_comment_service),
):
    filters = {}
    if timecode_from:
        filters["track_timecode"] = {"$gte": timecode_from}
    if timecode_to:
        filters.setdefault("track_timecode", {})
        filters["track_timecode"]["$lte"] = timecode_to

    items, total = await service.list_for_entity(
        "track", track_id,
        extra_filters=filters,
        root_only=root_only,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return TrackCommentListResponse(items=items, total=total, skip=skip, limit=limit)


@router.post(
    "/{track_id}/comments",
    response_model=TrackCommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Комментарий к треку",
)
async def create_track_comment(
    track_id: str,
    data: Annotated[
        TrackCommentCreate,
        Body(
            openapi_examples={
                "default": {
                    "value": {"comment": "Крутой дроп!", "track_timecode": 125}
                }
            }
        ),
    ],
    user: CurrentUser = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return await service.create(
        user.id,
        entity_type="track",
        entity_id=track_id,
        comment=data.comment,
        track_timecode=data.track_timecode,
    )


@router.get(
    "/{track_id}/comments/{comment_id}",
    response_model=TrackCommentResponse,
    summary="Комментарий к треку по ID",
)
async def get_track_comment(
    track_id: str,
    comment_id: str,
    service: CommentService = Depends(get_comment_service),
):
    return await service.get_for_entity(comment_id, "track", track_id)


@router.get(
    "/{track_id}/comments/{comment_id}/replies",
    response_model=TrackCommentListResponse,
    summary="Ответы на комментарий к треку",
)
async def list_track_comment_replies(
    track_id: str,
    comment_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", pattern="^(created_at|likes_quantity|rating_quantity|track_timecode)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    service: CommentService = Depends(get_comment_service),
):
    items, total = await service.list_for_entity(
        "track", track_id, 
        answer_id=comment_id, 
        skip=skip, 
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return TrackCommentListResponse(items=items, total=total, skip=skip, limit=limit)


@router.post(
    "/{track_id}/comments/{comment_id}/replies",
    response_model=TrackCommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ответ на комментарий к треку",
)
async def reply_to_track_comment(
    track_id: str,
    comment_id: str,
    data: Annotated[
        TrackCommentCreate,
        Body(
            openapi_examples={
                "default": {"value": {"comment": "Полностью согласен!", "track_timecode": 130}}
            }
        ),
    ],
    user: CurrentUser = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return await service.create(
        user.id,
        entity_type="track",
        entity_id=track_id,
        comment=data.comment,
        answer_id=comment_id,
        track_timecode=data.track_timecode,
    )


@router.put(
    "/{track_id}/comments/{comment_id}",
    response_model=TrackCommentResponse,
    summary="Изменить комментарий к треку",
)
async def update_track_comment(
    track_id: str,
    comment_id: str,
    data: TrackCommentUpdate,
    user: CurrentUser = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return await service.update(
        comment_id,
        user.id,
        "track",
        track_id,
        comment=data.comment,
        track_timecode=data.track_timecode,
    )


@router.delete(
    "/{track_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить комментарий к треку",
)
async def delete_track_comment(
    track_id: str,
    comment_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    await service.delete(comment_id, user.id, "track", track_id)
