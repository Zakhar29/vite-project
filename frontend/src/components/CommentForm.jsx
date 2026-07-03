import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Avatar from "./Avatar";
import "../styles/comment.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function CommentForm({ entityId, entityType = "track", userAvatar, onCommentAdded }) {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");
  const storedUser = JSON.parse(localStorage.getItem("user") || "{}");
  const avatar = userAvatar || storedUser?.avatar_url;

  const [commentText, setCommentText] = useState("");
  const [timecode, setTimecode] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const isExpanded = isFocused || commentText.length > 0;

  const handleSubmit = async () => {
    if (!commentText.trim()) return;
    if (!token) {
      navigate("/login");
      return;
    }

    setErrorMessage("");
    setIsSubmitting(true);
    try {
      const payload = { comment: commentText.trim() };
      if (entityType === "track" && timecode) {
        const seconds = parseInt(timecode, 10);
        if (!Number.isNaN(seconds) && seconds >= 0) {
          payload.track_timecode = seconds;
        }
      }

      const endpoint =
        entityType === "track"
          ? `/api/v1/social/track/${entityId}/comment`
          : `/api/v1/social/posts/${entityId}/comment`;

      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        setCommentText("");
        setTimecode("");
        setIsFocused(false);
        setErrorMessage("");
        onCommentAdded?.();
      } else {
        const data = await response.json().catch(() => ({}));
        const detail = data.detail;
        const message =
          typeof detail === "string"
            ? detail
            : Array.isArray(detail)
              ? detail.map((item) => item.msg).join(", ")
              : "Не удалось отправить комментарий";
        setErrorMessage(message);
      }
    } catch (err) {
      console.error("Ошибка:", err);
      setErrorMessage("Не удалось отправить комментарий. Попробуйте ещё раз.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    setCommentText("");
    setTimecode("");
    setIsFocused(false);
    setErrorMessage("");
  };

  return (
    <div className={`yt-comment-form ${isExpanded ? "is-expanded" : ""}`}>
      <Avatar src={avatar} alt="" className="yt-comment-form__avatar" />
      <div className="yt-comment-form__body">
        <input
          type="text"
          className="yt-comment-form__input"
          placeholder="Введите комментарий..."
          value={commentText}
          onChange={(e) => setCommentText(e.target.value)}
          onFocus={() => setIsFocused(true)}
          disabled={isSubmitting}
        />

        {entityType === "track" && isExpanded && (
          <div className="yt-comment-form__timecode">
            <label htmlFor={`timecode-${entityId}`}>Временная метка (сек.)</label>
            <input
              id={`timecode-${entityId}`}
              type="number"
              placeholder="0"
              value={timecode}
              onChange={(e) => setTimecode(e.target.value)}
              disabled={isSubmitting}
              min="0"
            />
          </div>
        )}

        {isExpanded && (
          <div className="yt-comment-form__actions">
            {errorMessage && (
              <p className="yt-comment__error yt-comment-form__error" role="alert">{errorMessage}</p>
            )}
            <button
              type="button"
              className="yt-comment-form__cancel"
              onClick={handleCancel}
              disabled={isSubmitting}
            >
              Отмена
            </button>
            <button
              type="button"
              className="yt-comment-form__send"
              onClick={handleSubmit}
              disabled={isSubmitting || !commentText.trim()}
            >
              {isSubmitting ? "Отправка..." : "Комментировать"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default CommentForm;
