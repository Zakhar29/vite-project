import { Link } from 'react-router-dom';
import "../styles/discussionCard.css";

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function DiscussionCard({ post, onClick }) {

  // ========== Обработка клика ==========

  const handleClick = () => {
    if (onClick) {
      onClick(post.id);
    }
  };

  // ========== Отрисовка ==========


  return (
    <div className="discussion-card" onClick={handleClick}>
      <div className="discussion-card-content">
        {/* Заголовок */}
        <h3 className="discussion-card-title">
          {post.title || 'Обсуждение'}
        </h3>

        {/* Текст */}
        {post.text && (
          <p className="discussion-card-text">
            {post.text.length > 200 ? `${post.text.slice(0, 200)}...` : post.text}
          </p>
        )}

        {/* Медиа превью */}
        {post.media && post.media.length > 0 && (
          <div className="discussion-card-media-preview">
            {post.media.slice(0, 2).map((media, index) => (
              media.type === 'image' ? (
                <img
                  key={index}
                  src={media.url}
                  alt=""
                  className="media-preview-image"
                />
              ) : media.type === 'video' ? (
                <div key={index} className="media-preview-video">
                  🎬 Видео
                </div>
              ) : null
            ))}
            {post.media.length > 2 && (
              <span className="media-more">+{post.media.length - 2}</span>
            )}
          </div>
        )}

        {/* Мета-информация */}
        <div className="discussion-card-meta">
          <div className="meta-left">
            {post.author && (
              <Link
                to={`/profile/${post.author.id}`}
                className="author-link"
                onClick={(e) => e.stopPropagation()}
              >
                <img
                  src={post.author.avatar_url || '/default-avatar.png'}
                  alt={post.author.nickname}
                  className="author-avatar-small"
                />
                <span className="author-name">{post.author.nickname}</span>
              </Link>
            )}
            <span className="post-date">{post.created_at}</span>
          </div>
          <div className="meta-right">
            <span className="stat-item">
              ❤️ {post.likes_quantity || 0}
            </span>
            <span className="stat-item">
              💬 {post.comments_quantity || 0}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DiscussionCard;