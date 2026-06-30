import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/comment.css";

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function Comment({ comment, onUpdate }) {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const [isLiked, setIsLiked] = useState(false);
  const [isDisliked, setIsDisliked] = useState(false);
  const [likes, setLikes] = useState(comment.likes_quantity || 0);
  const [dislikes, setDislikes] = useState(comment.dislikes_quantity || 0);
  const [rating, setRating] = useState(comment.rating_quantity || 0);
  const [isReplying, setIsReplying] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // ========== Голосование ==========

  const handleLike = async () => {
    if (!token) {
      alert("Войдите, чтобы оценить комментарий");
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
          setLikes(prev => prev - 1);
          setRating(prev => prev - 1);
          setIsLiked(false);
        } else {
          setLikes(prev => prev + 1);
          setRating(prev => prev + 1);
          setIsLiked(true);
          if (isDisliked) {
            setDislikes(prev => prev - 1);
            setRating(prev => prev + 1);
            setIsDisliked(false);
          }
        }
      }
    } catch (err) {
      console.error("Ошибка лайка:", err);
    }
  };

  const handleDislike = async () => {
    if (!token) {
      alert("Войдите, чтобы оценить комментарий");
      return;
    }

    const action = isDisliked ? "undislike" : "dislike";
    try {
      const response = await fetch(`${API_URL}/api/v1/comments/${comment.id}/${action}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        if (isDisliked) {
          setDislikes(prev => prev - 1);
          setRating(prev => prev + 1);
          setIsDisliked(false);
        } else {
          setDislikes(prev => prev + 1);
          setRating(prev => prev - 1);
          setIsDisliked(true);
          if (isLiked) {
            setLikes(prev => prev - 1);
            setRating(prev => prev - 1);
            setIsLiked(false);
          }
        }
      }
    } catch (err) {
      console.error("Ошибка дизлайка:", err);
    }
  };

  // ========== Ответ на комментарий ==========

  const handleReplySubmit = async () => {
    if (!replyText.trim()) return;
    if (!token) {
      alert("Войдите, чтобы ответить");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/social/track/${comment.track_id}/comment`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          comment: replyText,
          answer_id: comment.id,
          track_timecode: comment.track_timecode || null,
        }),
      });

      if (response.ok) {
        setReplyText("");
        setIsReplying(false);
        if (onUpdate) onUpdate();
      } else {
        const data = await response.json();
        alert(data.detail || "Ошибка отправки ответа");
      }
    } catch (err) {
      console.error("Ошибка ответа:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  // ========== Рендер ==========

  return (
    <div className="comment">

      {/* Голосование */}
      <div className="comment-votes">
        <button
          className={`vote-btn up ${isLiked ? "active" : ""}`}
          onClick={handleLike}
          disabled={!token}
        >
          ▲
        </button>
        <span className="vote-count">{rating}</span>
        <button
          className={`vote-btn down ${isDisliked ? "active" : ""}`}
          onClick={handleDislike}
          disabled={!token}
        >
          ▼
        </button>
      </div>

      {/* Аватар */}
      <img
        src={comment.author?.avatar_url || "https://i.pravatar.cc/35"}
        alt={comment.author?.nickname}
        className="avatar"
        onClick={() => navigate(`/profile/${comment.author?.id}`)}
        style={{ cursor: "pointer" }}
      />

      {/* Тело комментария */}
      <div className="comment-body">

        <div className="comment-meta">
          <b
            onClick={() => navigate(`/profile/${comment.author?.id}`)}
            style={{ cursor: "pointer" }}
          >
            {comment.author?.nickname || "Пользователь"}
          </b>
          <span>{comment.created_at || "только что"}</span>
          {comment.track_timecode !== null && comment.track_timecode !== undefined && (
            <span className="timecode">
              ⏱ {Math.floor(comment.track_timecode / 60)}:
              {(comment.track_timecode % 60).toString().padStart(2, "0")}
            </span>
          )}
        </div>

        <p>{comment.comment}</p>

        <div className="comment-actions">
          <button
            className="reply-btn"
            onClick={() => setIsReplying(!isReplying)}
          >
            Ответить
          </button>
          <span className="comment-likes">
            ❤ {likes}
          </span>
          {comment.answer_quantity > 0 && (
            <span className="replies-count">
              💬 {comment.answer_quantity} ответов
            </span>
          )}
        </div>

        {/* Форма ответа */}
        {isReplying && (
          <div className="reply-form">
            <textarea
              value={replyText}
              onChange={(e) => setReplyText(e.target.value)}
              placeholder={`Ответить ${comment.author?.nickname || "пользователю"}...`}
              rows="2"
              disabled={isSubmitting}
            />
            <div className="reply-actions">
              <button
                className="cancel-reply"
                onClick={() => {
                  setIsReplying(false);
                  setReplyText("");
                }}
                disabled={isSubmitting}
              >
                Отмена
              </button>
              <button
                className="send-reply"
                onClick={handleReplySubmit}
                disabled={isSubmitting || !replyText.trim()}
              >
                {isSubmitting ? "Отправка..." : "Ответить"}
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default Comment;