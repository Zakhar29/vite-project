import { Link } from "react-router-dom";
import { getPostTitle } from "../utils/postTitle";
import Avatar from "./Avatar";
import { formatCommentsLabel } from "../utils/formatComments";

function DiscussionPost({ post, isLiked, likesCount, commentsCount, onLike }) {
  const handleLikeClick = () => {
    if (onLike) {
      onLike();
    }
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: getPostTitle(post),
        text: post?.text || "",
        url: window.location.href,
      }).catch(() => {});
    } else {
      navigator.clipboard?.writeText(window.location.href);
      alert("Ссылка скопирована!");
    }
  };

  if (!post) {
    return (
      <div className="discussion-post">
        <p className="post-empty">Пост не найден</p>
      </div>
    );
  }

  const title = getPostTitle(post);
  const firstImage = post.media?.find((item) => item.type === "image");

  return (
    <article className="discussion-post">
      <div className="post-header">
        <Link to={`/profile/${post.author?.id}`} className="author-link">
          <Avatar
            src={post.author?.avatar_url}
            alt={post.author?.nickname || "User"}
            className="avatar"
          />
          <div className="post-author-info">
            <b className="author-name">{post.author?.nickname || "Пользователь"}</b>
            <span className="post-meta">
              {post.created_at || post.created_at_formatted || "Недавно"}
            </span>
          </div>
        </Link>
        <span className="post-tag">Genre Discussion</span>
      </div>

      <h1 className="post-title">{title}</h1>

      <div className="post-body">
        <div className="post-text-block">
          <p className="post-text">{post.text}</p>
        </div>

        {firstImage && (
          <img
            src={firstImage.url}
            alt=""
            className="post-image"
            loading="lazy"
          />
        )}
      </div>

      <div className="post-actions">
        <div className="actions-left">
          <div className="vote-group">
            <button
              type="button"
              className={`vote-btn up ${isLiked ? "active" : ""}`}
              onClick={handleLikeClick}
              aria-label="Нравится"
            >
              ▲
            </button>
            <span className="vote-count">{likesCount || 0}</span>
            <button type="button" className="vote-btn down" aria-label="Не нравится">
              ▼
            </button>
          </div>

          <div className="action-stat">
            <span className="icon">💬</span>
            <span>{formatCommentsLabel(commentsCount)}</span>
          </div>

          <button type="button" className="action-btn share-btn" onClick={handleShare}>
            Поделиться
          </button>
        </div>

        <div className="actions-right">
          <button type="button" className="icon-action" aria-label="Меню">⋯</button>
          <button type="button" className="icon-action" aria-label="Редактировать">✎</button>
        </div>
      </div>
    </article>
  );
}

export default DiscussionPost;
