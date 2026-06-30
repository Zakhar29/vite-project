import { Link } from 'react-router-dom';

function DiscussionPost({ post, isLiked, likesCount, commentsCount, onLike }) {
  // ========== Обработчик лайка ==========

  const handleLikeClick = () => {
    if (onLike) {
      onLike();
    }
  };

  // ========== Обработчик шаринга ==========

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: post?.title || 'Обсуждение',
        text: post?.text || '',
        url: window.location.href,
      }).catch(() => {});
    } else {
      navigator.clipboard?.writeText(window.location.href);
      alert('Ссылка скопирована!');
    }
  };

  // ========== Если нет данных ==========

  if (!post) {
    return (
      <div className="discussion-post">
        <p className="post-empty">Пост не найден</p>
      </div>
    );
  }

  // ========== Рендер ==========

  return (
    <div className="discussion-post">
      {/* ===== Заголовок с автором ===== */}
      <div className="post-header">
        <Link to={`/user/${post.author?.id}`} className="author-link">
          <img
            src={post.author?.avatar_url || 'https://i.pravatar.cc/40'}
            alt={post.author?.nickname || 'User'}
            className="avatar"
          />
          <div>
            <b className="author-name">{post.author?.nickname || 'Пользователь'}</b>
            <span className="post-meta">
              {post.created_at || post.created_at_formatted || 'Неизвестная дата'}
              {post.genres && post.genres.length > 0 && (
                <> • {post.genres[0]}</>
              )}
            </span>
          </div>
        </Link>
      </div>

      {/* ===== Заголовок поста ===== */}
      <div className="post-title-wrapper">
        <h1 className="post-title">
          {post.title || 'Обсуждение'}
        </h1>
      </div>

      {/* ===== Тело поста ===== */}
      <div className="post-body">
        <p className="post-text">
          {post.text}
        </p>

        {/* Медиа */}
        {post.media && post.media.length > 0 && (
          <div className="post-media">
            {post.media.map((media, index) => (
              media.type === 'image' ? (
                <img
                  key={index}
                  src={media.url}
                  alt={`Media ${index + 1}`}
                  className="post-image"
                  loading="lazy"
                />
              ) : media.type === 'video' ? (
                <video
                  key={index}
                  src={media.url}
                  controls
                  className="post-video"
                />
              ) : null
            ))}
          </div>
        )}
      </div>

      {/* ===== Действия ===== */}
      <div className="post-actions">
        <div className="actions-left">
          <button
            className={`action-btn like-btn ${isLiked ? 'liked' : ''}`}
            onClick={handleLikeClick}
          >
            <span className="icon">{isLiked ? '❤️' : '🤍'}</span>
            <span className="count">{likesCount || 0}</span>
          </button>

          <div className="action-stat">
            <span className="icon">💬</span>
            <span className="count">{commentsCount || 0}</span>
          </div>
        </div>

        <button
          className="action-btn share-btn"
          onClick={handleShare}
        >
          <span className="icon">🔗</span>
          <span className="label">Поделиться</span>
        </button>
      </div>
    </div>
  );
}

export default DiscussionPost;