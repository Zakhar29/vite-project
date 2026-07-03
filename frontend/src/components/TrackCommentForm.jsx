import { useState } from "react";
import Avatar from "./Avatar";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function TrackCommentForm({ trackId, userAvatar, onCommentAdded }) {
  const token = localStorage.getItem("access_token");
  const [commentText, setCommentText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!commentText.trim()) return;
    if (!token) {
      alert("Войдите, чтобы оставить комментарий");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/social/track/${trackId}/comment`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ comment: commentText.trim() }),
      });

      if (response.ok) {
        setCommentText("");
        onCommentAdded?.();
      } else {
        const data = await response.json();
        alert(data.detail || "Ошибка отправки комментария");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="track-comment-form">
      <Avatar
        src={userAvatar}
        alt=""
        className="track-comment-form__avatar"
      />
      <div className="track-comment-form__body">
        <textarea
          placeholder="Написать комментарий..."
          value={commentText}
          onChange={(e) => setCommentText(e.target.value)}
          disabled={isSubmitting}
        />
        <div className="track-comment-form__actions">
          <button
            type="button"
            className="track-comment-form__cancel"
            onClick={() => setCommentText("")}
            disabled={isSubmitting}
          >
            Отмена
          </button>
          <button
            type="button"
            className="track-comment-form__send"
            onClick={handleSubmit}
            disabled={isSubmitting || !commentText.trim()}
          >
            {isSubmitting ? "Отправка..." : "Отправить"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default TrackCommentForm;
