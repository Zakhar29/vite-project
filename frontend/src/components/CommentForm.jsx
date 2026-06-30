import { useState } from "react";
import "../styles/comment.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function CommentForm({ entityId, entityType = "track", onCommentAdded }) {
  const token = localStorage.getItem("access_token");

  const [commentText, setCommentText] = useState("");
  const [timecode, setTimecode] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!commentText.trim()) return;
    if (!token) {
      alert("Войдите, чтобы оставить комментарий");
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = { comment: commentText.trim() };
      if (entityType === "track" && timecode) {
        const seconds = parseInt(timecode);
        if (!isNaN(seconds) && seconds >= 0) {
          payload.track_timecode = seconds;
        }
      }

      const endpoint = entityType === "track"
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
        if (onCommentAdded) onCommentAdded();
      } else {
        const data = await response.json();
        alert(data.detail || "Ошибка отправки комментария");
      }
    } catch (err) {
      console.error("Ошибка:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="comment-form">

      <h3>Добавить комментарий</h3>

      <textarea
        className="comment-textarea"
        placeholder="Написать комментарий..."
        value={commentText}
        onChange={(e) => setCommentText(e.target.value)}
        disabled={isSubmitting}
      />

      {entityType === "track" && (
        <div className="timecode-input">
          <label htmlFor="track-timecode">⏱ Временная метка (секунды, опционально)</label>
          <input
            type="number"
            placeholder="Например: 125"
            value={timecode}
            onChange={(e) => setTimecode(e.target.value)}
            disabled={isSubmitting}
            min="0"
          />
        </div>
      )}

      <button
        className="submit-comment"
        onClick={handleSubmit}
        disabled={isSubmitting || !commentText.trim()}
      >
        {isSubmitting ? "Отправка..." : "Отправить"}
      </button>

    </div>
  );
}

export default CommentForm;