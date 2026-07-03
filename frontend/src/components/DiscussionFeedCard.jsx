import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getPostTitle } from "../utils/postTitle";
import { formatCommentsLabel } from "../utils/formatComments";
import "../styles/discussionFeedCard.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function DiscussionFeedCard({ post, onLike, onUnlike, onDelete }) {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");
  const currentUser = JSON.parse(localStorage.getItem("user") || "{}");

  const [isLiked, setIsLiked] = useState(post?.is_liked || false);
  const [likesCount, setLikesCount] = useState(post?.likes_quantity || 0);
  const [isAuthor, setIsAuthor] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (post?.author?.id && currentUser?.id) {
      setIsAuthor(post.author.id === currentUser.id);
    }
  }, [post, currentUser]);

  const formatDate = (dateStr) => {
    if (!dateStr) return "недавно";
    try {
      const date = new Date(dateStr);
      const now = new Date();
      const diff = Math.floor((now - date) / 1000 / 60);

      if (diff < 1) return "только что";
      if (diff < 60) return `${diff} мин назад`;
      if (diff < 1440) return `${Math.floor(diff / 60)} ч назад`;
      return date.toLocaleDateString("ru-RU", { day: "numeric", month: "long" });
    } catch {
      return dateStr;
    }
  };

  const title = getPostTitle(post);
  const excerpt = post?.text?.length > 220 ? `${post.text.slice(0, 220)}...` : post?.text;
  const firstImage = post?.media?.find((item) => item.type === "image");
  const tag = post?.genres?.[0] || "Electronic";

  const openThread = () => navigate(`/discussion/${post.id}`);

  const handleVote = async (direction) => {
    if (!token) {
      navigate("/login");
      return;
    }

    if (direction === "up" && !isLiked) {
      await onLike?.(post.id);
      setIsLiked(true);
      setLikesCount((prev) => prev + 1);
    } else if (direction === "down" && isLiked) {
      await onUnlike?.(post.id);
      setIsLiked(false);
      setLikesCount((prev) => Math.max(prev - 1, 0));
    }
  };

  const handleShare = async (e) => {
    e.stopPropagation();
    const url = `${window.location.origin}/discussion/${post.id}`;
    try {
      if (navigator.share) {
        await navigator.share({ title, url });
      } else {
        await navigator.clipboard?.writeText(url);
        alert("Ссылка скопирована!");
      }
    } catch {
      /* cancelled */
    }
  };

  const handleDelete = (e) => {
    e.stopPropagation();
    if (window.confirm("Удалить обсуждение?")) {
      onDelete?.(post.id);
    }
  };

  return (
    <article className="feed-card" onClick={openThread} role="button" tabIndex={0} onKeyDown={(e) => e.key === "Enter" && openThread()}>
      <div className="feed-card__votes" onClick={(e) => e.stopPropagation()}>
        <button
          type="button"
          className={`feed-card__vote ${isLiked ? "active" : ""}`}
          onClick={() => handleVote("up")}
          aria-label="Нравится"
        >
          ▲
        </button>
        <span className="feed-card__score">{likesCount}</span>
        <button
          type="button"
          className="feed-card__vote"
          onClick={() => handleVote("down")}
          aria-label="Не нравится"
        >
          ▼
        </button>
      </div>

      <div className="feed-card__content">
        <div className="feed-card__meta">
          <span className="feed-card__tag">{tag}</span>
          <span className="feed-card__published">
            Опубликовано <b>{post.author?.nickname || "Аноним"}</b> {formatDate(post.created_at)}
          </span>
          {isAuthor && (
            <button type="button" className="feed-card__delete" onClick={handleDelete}>
              ✕
            </button>
          )}
        </div>

        <h3 className="feed-card__title">{title}</h3>

        {excerpt && <p className="feed-card__text">{excerpt}</p>}

        {firstImage && (
          <img src={firstImage.url} alt="" className="feed-card__image" loading="lazy" />
        )}

        <div className="feed-card__footer" onClick={(e) => e.stopPropagation()}>
          <button type="button" className="feed-card__action" onClick={openThread}>
            💬 {formatCommentsLabel(post.comments_quantity)}
          </button>
          <button type="button" className="feed-card__action" onClick={handleShare}>
            ↗ Поделиться
          </button>
          <button
            type="button"
            className={`feed-card__bookmark ${saved ? "active" : ""}`}
            onClick={() => setSaved(!saved)}
            aria-label="Сохранить"
          >
            🔖
          </button>
        </div>
      </div>
    </article>
  );
}

export default DiscussionFeedCard;
