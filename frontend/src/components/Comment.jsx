import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Avatar from "./Avatar";
import "../styles/comment.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function formatDate(dateStr) {
  if (!dateStr) return "недавно";
  const date = new Date(dateStr);
  if (Number.isNaN(date.getTime())) return "недавно";
  try {
    const now = new Date();
    const diff = Math.floor((now - date) / 1000 / 60);
    if (diff < 60) return `${Math.max(diff, 1)} мин. назад`;
    if (diff < 1440) return `${Math.floor(diff / 60)} ч. назад`;
    return date.toLocaleDateString("ru-RU", { day: "numeric", month: "short", year: "numeric" });
  } catch {
    return "недавно";
  }
}

function formatCommentDate(comment) {
  if (comment.created_at_formatted) return comment.created_at_formatted;
  const raw = comment.created_at_raw || comment.created_at;
  if (!raw) return "недавно";
  const parsed = new Date(raw);
  if (!Number.isNaN(parsed.getTime())) return formatDate(raw);
  if (typeof comment.created_at === "string") return comment.created_at;
  return "недавно";
}

function ThumbUpIcon({ filled }) {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
      <path
        fill={filled ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="1.8"
        d="M7 10v10H4V10h3zm2-1 4-5.5a1.5 1.5 0 0 1 2.5 1.1V8h3.2c.9 0 1.6.8 1.5 1.7l-1.2 7.5a1.5 1.5 0 0 1-1.5 1.3H9V9h0z"
      />
    </svg>
  );
}

function Comment({ comment, entityType = "track", entityId, onUpdate, userAvatar }) {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const [isLiked, setIsLiked] = useState(false);
  const [likes, setLikes] = useState(comment.likes_quantity || 0);
  const [isReplying, setIsReplying] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const displayDate = formatCommentDate(comment);

  const handleLike = async () => {
    if (!token) {
      navigate("/login");
      return;
    }

    const action = isLiked ? "unlike" : "like";
    try {
      const response = await fetch(`${API_URL}/api/v1/comments/${comment.id}/${action}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        if (isLiked) {
          setLikes((prev) => Math.max(prev - 1, 0));
          setIsLiked(false);
        } else {
          setLikes((prev) => prev + 1);
          setIsLiked(true);
        }
      }
    } catch (err) {
      console.error("Ошибка лайка:", err);
    }
  };

  const handleReplySubmit = async () => {
    if (!replyText.trim()) return;
    if (!token) {
      navigate("/login");
      return;
    }

    setErrorMessage("");

    const replyEndpoint =
      entityType === "track"
        ? `/api/v1/social/track/${entityId}/comment/${comment.id}/reply`
        : `/api/v1/social/posts/${entityId}/comment/${comment.id}/reply`;

    const payload = { comment: replyText.trim() };
    if (entityType === "track" && comment.track_timecode != null) {
      payload.track_timecode = comment.track_timecode;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch(`${API_URL}${replyEndpoint}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        setReplyText("");
        setIsReplying(false);
        setErrorMessage("");
        onUpdate?.();
      } else {
        const data = await response.json().catch(() => ({}));
        const detail = data.detail;
        const message =
          typeof detail === "string"
            ? detail
            : Array.isArray(detail)
              ? detail.map((item) => item.msg).join(", ")
              : "Не удалось отправить ответ";
        setErrorMessage(message);
      }
    } catch (err) {
      console.error("Ошибка ответа:", err);
      setErrorMessage("Не удалось отправить ответ. Попробуйте ещё раз.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <article className="yt-comment">
      <Avatar
        src={comment.author?.avatar_url}
        alt={comment.author?.nickname}
        className="yt-comment__avatar"
        onClick={() => comment.author?.id && navigate(`/profile/${comment.author.id}`)}
      />

      <div className="yt-comment__content">
        <div className="yt-comment__header">
          <button
            type="button"
            className="yt-comment__author"
            onClick={() => comment.author?.id && navigate(`/profile/${comment.author.id}`)}
          >
            {comment.author?.nickname || "Пользователь"}
          </button>
          <span className="yt-comment__date">{displayDate}</span>
          {comment.track_timecode != null && (
            <span className="yt-comment__timecode">
              {Math.floor(comment.track_timecode / 60)}:
              {(comment.track_timecode % 60).toString().padStart(2, "0")}
            </span>
          )}
        </div>

        <p className="yt-comment__text">{comment.comment}</p>

        <div className="yt-comment__actions">
          <button
            type="button"
            className={`yt-action-btn yt-action-btn--like ${isLiked ? "is-active" : ""}`}
            onClick={handleLike}
            disabled={!token}
          >
            <ThumbUpIcon filled={isLiked} />
            {likes > 0 && <span>{likes}</span>}
          </button>

          <button
            type="button"
            className="yt-action-btn yt-action-btn--reply"
            onClick={() => {
              setIsReplying((prev) => !prev);
              setErrorMessage("");
            }}
          >
            Ответить
          </button>

          {comment.answer_quantity > 0 && (
            <span className="yt-comment__replies-count">
              {comment.answer_quantity} {comment.answer_quantity === 1 ? "ответ" : "ответов"}
            </span>
          )}
        </div>

        {isReplying && (
          <div className="yt-reply-form">
            <Avatar src={userAvatar} alt="" className="yt-reply-form__avatar" />
            <div className="yt-reply-form__body">
              <textarea
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                placeholder={`Ответить ${comment.author?.nickname || "пользователю"}...`}
                rows={2}
                disabled={isSubmitting}
              />
              <div className="yt-reply-form__actions">
                {errorMessage && (
                  <p className="yt-comment__error" role="alert">{errorMessage}</p>
                )}
                <button
                  type="button"
                  className="yt-reply-form__cancel"
                  onClick={() => {
                    setIsReplying(false);
                    setReplyText("");
                  }}
                  disabled={isSubmitting}
                >
                  Отмена
                </button>
                <button
                  type="button"
                  className="yt-reply-form__send"
                  onClick={handleReplySubmit}
                  disabled={isSubmitting || !replyText.trim()}
                >
                  {isSubmitting ? "Отправка..." : "Ответить"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </article>
  );
}

export default Comment;
