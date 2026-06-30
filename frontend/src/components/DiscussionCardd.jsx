import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import "../styles/discussionCard.css";

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function DiscussionCardd({ post, onLike, onUnlike, onDelete }) {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");
  const currentUser = JSON.parse(localStorage.getItem("user") || '{}');

  const [isLiked, setIsLiked] = useState(post?.is_liked || false);
  const [likesCount, setLikesCount] = useState(post?.likes_quantity || 0);
  const [commentsCount, setCommentsCount] = useState(post?.comments_quantity || 0);
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState([]);
  const [isLoadingComments, setIsLoadingComments] = useState(false);
  const [commentText, setCommentText] = useState('');
  const [isSubmittingComment, setIsSubmittingComment] = useState(false);
  const [isAuthor, setIsAuthor] = useState(false);

  // ========== Проверка авторства ==========
  useEffect(() => {
    if (post?.author?.id && currentUser?.id) {
      setIsAuthor(post.author.id === currentUser.id);
    }
  }, [post, currentUser]);

  // ========== Загрузка комментариев ==========

  const loadComments = async () => {
    if (showComments) {
      setShowComments(false);
      return;
    }

    try {
      setIsLoadingComments(true);
      const response = await fetch(`${API_URL}/api/v1/post-page/${post.id}/comments?skip=0&limit=20`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });

      if (!response.ok) throw new Error('Failed to load comments');

      const data = await response.json();
      setComments(data.items || []);
      setShowComments(true);
    } catch (err) {
      console.error('Failed to load comments:', err);
    } finally {
      setIsLoadingComments(false);
    }
  };

  // ========== Добавление комментария ==========

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!commentText.trim() || isSubmittingComment) return;

    try {
      setIsSubmittingComment(true);
      const response = await fetch(`${API_URL}/api/v1/social/posts/${post.id}/comment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        credentials: 'include',
        body: JSON.stringify({ comment: commentText })
      });

      if (!response.ok) {
        if (response.status === 401) {
          navigate('/login');
          return;
        }
        throw new Error('Failed to add comment');
      }

      const data = await response.json();

      // Получаем данные автора комментария
      const commentAuthor = {
        id: currentUser?.id || 'me',
        nickname: currentUser?.nickname || 'Вы',
        avatar_url: currentUser?.avatar_url || '/default-avatar.png'
      };

      const newComment = {
        id: data.comment?.id || Date.now().toString(),
        author: commentAuthor,
        comment: commentText,
        created_at: new Date().toISOString(),
        created_at_formatted: 'Только что',
        likes_quantity: 0,
        dislikes_quantity: 0,
        rating_quantity: 0,
        answer_quantity: 0
      };

      setComments(prev => [...prev, newComment]);
      setCommentsCount(prev => prev + 1);
      setCommentText('');
    } catch (err) {
      console.error('Failed to add comment:', err);
      alert('Не удалось отправить комментарий');
    } finally {
      setIsSubmittingComment(false);
    }
  };

  // ========== Лайки поста ==========

  const handleLikeClick = async () => {
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      if (isLiked) {
        await onUnlike?.(post.id);
        setIsLiked(false);
        setLikesCount(prev => prev - 1);
      } else {
        await onLike?.(post.id);
        setIsLiked(true);
        setLikesCount(prev => prev + 1);
      }
    } catch (err) {
      console.error('Failed to toggle like:', err);
    }
  };

  // ========== Удаление поста ==========

  const handleDelete = () => {
    if (window.confirm('Вы уверены, что хотите удалить этот пост?')) {
      onDelete?.(post.id);
    }
  };

  // ========== Форматирование даты ==========

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      const date = new Date(dateStr);
      const now = new Date();
      const diff = Math.floor((now - date) / 1000 / 60); // минуты

      if (diff < 1) return 'только что';
      if (diff < 60) return `${diff} мин назад`;
      if (diff < 1440) return `${Math.floor(diff / 60)} ч назад`;
      return date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      });
    } catch {
      return dateStr;
    }
  };

  // ========== Копирование ссылки ==========

  const handleShare = async () => {
    try {
      const url = `${window.location.origin}/discussion/${post.id}`;
      await navigator.clipboard?.writeText(url);
      alert('Ссылка скопирована!');
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // ========== Отрисовка ==========

  return (
    <div className="discussion-card">
      <div className="discussion-body">
        {/* Мета-информация */}
        <div className="discussion-meta">
          <div className="meta-left">
            {post.author && (
              <Link to={`/user/${post.author.id}`} className="author-link">
                <img
                  src={post.author.avatar_url || '/default-avatar.png'}
                  alt={post.author.nickname}
                  className="author-avatar-small"
                />
                <span className="author-name">{post.author.nickname}</span>
              </Link>
            )}
            <span className="post-date">• {formatDate(post.created_at)}</span>
          </div>
          <div className="meta-right">
            {isAuthor && (
              <button
                className="delete-btn"
                onClick={handleDelete}
                aria-label="Удалить пост"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Текст */}
        {post.text && (
          <p className="discussion-text">
            {post.text}
          </p>
        )}

        {/* Медиа */}
        {post.media && post.media.length > 0 && (
          <div className="discussion-media">
            {post.media.map((media, index) => (
              media.type === 'image' ? (
                <img
                  key={index}
                  src={media.url}
                  alt={`Media ${index + 1}`}
                  className="media-preview-image"
                  loading="lazy"
                />
              ) : media.type === 'video' ? (
                <video
                  key={index}
                  src={media.url}
                  controls
                  className="media-preview-video"
                />
              ) : null
            ))}
          </div>
        )}

        {/* Действия */}
        <div className="discussion-actions">
          <button
            className={`action-btn like-btn ${isLiked ? 'liked' : ''}`}
            onClick={handleLikeClick}
            disabled={!token}
          >
            <span className="icon">{isLiked ? '❤️' : '🤍'}</span>
            <span className="count">{likesCount}</span>
          </button>

          <button
            className="action-btn comment-btn"
            onClick={loadComments}
          >
            <span className="icon">💬</span>
            <span className="count">{commentsCount}</span>
          </button>

          <button
            className="action-btn share-btn"
            onClick={handleShare}
          >
            <span className="icon">🔗</span>
            <span className="label">Поделиться</span>
          </button>
        </div>

        {/* Комментарии */}
        {showComments && (
          <div className="comments-section">
            {isLoadingComments ? (
              <div className="loading-comments">Загрузка комментариев...</div>
            ) : (
              <>
                {comments.length === 0 ? (
                  <div className="no-comments">Пока нет комментариев</div>
                ) : (
                  comments.map((comment) => (
                    <div key={comment.id} className="comment-item">
                      <img
                        src={comment.author?.avatar_url || '/default-avatar.png'}
                        alt={comment.author?.nickname}
                        className="comment-avatar"
                      />
                      <div className="comment-content">
                        <div className="comment-header">
                          <Link to={`/user/${comment.author?.id}`} className="comment-author">
                            {comment.author?.nickname || 'Пользователь'}
                          </Link>
                          <span className="comment-date">
                            {formatDate(comment.created_at)}
                          </span>
                        </div>
                        <p className="comment-text">{comment.comment}</p>
                        <div className="comment-actions">
                          <button className="comment-like-btn">
                            👍 {comment.likes_quantity || 0}
                          </button>
                          <button className="comment-reply-btn">
                            Ответить
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}

                {/* Форма добавления комментария */}
                {token ? (
                  <form className="comment-form" onSubmit={handleCommentSubmit}>
                    <input
                      type="text"
                      placeholder="Написать комментарий..."
                      value={commentText}
                      onChange={(e) => setCommentText(e.target.value)}
                      disabled={isSubmittingComment}
                    />
                    <button
                      type="submit"
                      disabled={!commentText.trim() || isSubmittingComment}
                    >
                      {isSubmittingComment ? 'Отправка...' : 'Отправить'}
                    </button>
                  </form>
                ) : (
                  <div className="login-to-comment">
                    <Link to="/login">Войдите</Link>, чтобы оставить комментарий
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default DiscussionCardd;