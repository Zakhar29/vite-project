import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DiscussionPost from "../components/DiscussionPost";
import Comment from "../components/Comment";
import CommentForm from "../components/CommentForm";
import RelatedSidebar from "../components/RelatedSidebar";
import "../styles/thread.css";

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function DiscussionThread() {
  const { id } = useParams();
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingComments, setLoadingComments] = useState(true);
  const [error, setError] = useState(null);
  const [hasMoreComments, setHasMoreComments] = useState(false);
  const [commentsSkip, setCommentsSkip] = useState(0);
  const [commentsLimit] = useState(20);
  const [isLiked, setIsLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(0);
  const [commentsCount, setCommentsCount] = useState(0);
  const [isSubmittingComment, setIsSubmittingComment] = useState(false);

  // ========== Отладка ==========
  console.log('🔍 DiscussionThread рендерится');
  console.log('🔍 postId из URL:', id);
  console.log('🔍 token:', token ? 'есть' : 'нет');

  // ========== Загрузка поста ==========

  useEffect(() => {
    console.log('🔄 useEffect вызван, postId:', id);

    if (id) {
      loadPost();
      loadComments(0);
    } else {
      console.warn('⚠️ postId не найден в URL');
      setError('ID поста не указан');
      setLoading(false);
    }
  }, [id]);

  const loadPost = async () => {
    try {
      setLoading(true);
      console.log('📥 Загрузка поста...');

      const url = `${API_URL}/api/v1/post-page/${id}`;
      console.log('📥 URL:', url);

      const response = await fetch(url, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });

      console.log('📥 Статус ответа:', response.status);

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Пост не найден');
        }
        throw new Error(`Ошибка загрузки поста: ${response.status}`);
      }

      const data = await response.json();
      console.log('📥 Данные поста:', data);

      if (data && data.post) {
        setPost(data.post);
        setIsLiked(data.post?.is_liked || false);
        setLikesCount(data.post?.likes_quantity || 0);
        setCommentsCount(data.post?.comments_quantity || 0);
        setError(null);
      } else {
        console.warn('⚠️ Нет данных post в ответе');
        setError('Не удалось загрузить пост');
      }
    } catch (err) {
      console.error('❌ Ошибка загрузки поста:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ========== Загрузка комментариев ==========

  const loadComments = async (skip = 0) => {
    try {
      setLoadingComments(true);
      console.log('📥 Загрузка комментариев...');

      const url = `${API_URL}/api/v1/post-page/${id}/comments?skip=${skip}&limit=${commentsLimit}`;
      console.log('📥 URL комментариев:', url);

      const response = await fetch(url, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });

      console.log('📥 Статус комментариев:', response.status);

      if (!response.ok) throw new Error('Ошибка загрузки комментариев');

      const data = await response.json();
      console.log('📥 Данные комментариев:', data);

      if (skip === 0) {
        setComments(data.items || []);
      } else {
        setComments(prev => [...prev, ...(data.items || [])]);
      }

      setHasMoreComments(data.has_more || false);
      setCommentsSkip(skip + commentsLimit);
    } catch (err) {
      console.error('❌ Ошибка загрузки комментариев:', err);
    } finally {
      setLoadingComments(false);
    }
  };

  // ========== Загрузка еще комментариев ==========

  const loadMoreComments = () => {
    if (!loadingComments && hasMoreComments) {
      loadComments(commentsSkip);
    }
  };

  // ========== Лайк поста ==========

  const handleLike = async () => {
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      const endpoint = isLiked ? 'unlike' : 'like';
      console.log(`📤 ${endpoint} поста:`, id);

      const response = await fetch(`${API_URL}/api/v1/social/post/${id}/${endpoint}`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        credentials: 'include'
      });

      if (!response.ok) {
        if (response.status === 401) {
          navigate('/login');
          return;
        }
        throw new Error('Failed to toggle like');
      }

      setIsLiked(!isLiked);
      setLikesCount(prev => isLiked ? prev - 1 : prev + 1);
    } catch (err) {
      console.error('❌ Ошибка лайка:', err);
    }
  };

  // ========== Добавление комментария ==========

  const handleCommentSubmit = async (commentText) => {
    if (!commentText.trim() || isSubmittingComment) return;

    if (!token) {
      navigate('/login');
      return;
    }

    try {
      setIsSubmittingComment(true);
      console.log('📤 Отправка комментария:', commentText);

      const response = await fetch(`${API_URL}/api/v1/social/posts/${id}/comment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        credentials: 'include',
        body: JSON.stringify({ comment: commentText })
      });

      console.log('📤 Статус ответа комментария:', response.status);

      if (!response.ok) {
        if (response.status === 401) {
          navigate('/login');
          return;
        }
        throw new Error('Failed to add comment');
      }

      const data = await response.json();
      console.log('📤 Ответ комментария:', data);

      const currentUser = JSON.parse(localStorage.getItem('user') || '{}');

      const newComment = {
        id: data.comment?.id || Date.now().toString(),
        author: {
          id: currentUser?.id || 'me',
          nickname: currentUser?.nickname || 'Вы',
          avatar_url: currentUser?.avatar_url || '/default-avatar.png'
        },
        comment: commentText,
        created_at: new Date().toISOString(),
        created_at_formatted: 'Только что',
        likes_quantity: 0,
        dislikes_quantity: 0,
        rating_quantity: 0,
        answer_quantity: 0
      };

      setComments(prev => [newComment, ...prev]);
      setCommentsCount(prev => prev + 1);

      return true;
    } catch (err) {
      console.error('❌ Ошибка добавления комментария:', err);
      alert('Не удалось отправить комментарий');
      return false;
    } finally {
      setIsSubmittingComment(false);
    }
  };

  // ========== Обработка скролла ==========

  useEffect(() => {
    const handleScroll = () => {
      if (window.innerHeight + document.documentElement.scrollTop
          >= document.documentElement.offsetHeight - 500) {
        loadMoreComments();
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [loadingComments, hasMoreComments, commentsSkip]);

  // ========== Рендер ==========

  console.log('🎨 Рендер компонента, loading:', loading, 'post:', !!post);

  // Если загрузка
  if (loading) {
    return (
      <div className="thread-page">
        <div className="thread-layout">
          <div className="thread-main">
            <div className="loading-skeleton">
              <div className="skeleton-post"></div>
              <div className="skeleton-comments">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="skeleton-comment"></div>
                ))}
              </div>
            </div>
          </div>
          <div className="sidebar-skeleton"></div>
        </div>
      </div>
    );
  }

  // Если ошибка
  if (error) {
    return (
      <div className="thread-page">
        <div className="thread-error">
          <h2>😕 {error}</h2>
          <p>Попробуйте вернуться на главную страницу</p>
          <button onClick={() => navigate('/')}>На главную</button>
        </div>
      </div>
    );
  }

  // Если пост не найден
  if (!post) {
    return (
      <div className="thread-page">
        <div className="thread-error">
          <h2>😕 Пост не найден</h2>
          <p>Возможно, он был удален или перемещен</p>
          <button onClick={() => navigate('/')}>На главную</button>
        </div>
      </div>
    );
  }

  // Основной рендер
  return (
    <div className="thread-page">
      <div className="thread-layout">
        <div className="thread-main">
          <DiscussionPost
            post={post}
            isLiked={isLiked}
            likesCount={likesCount}
            commentsCount={commentsCount}
            onLike={handleLike}
          />

          <CommentForm
            entityId={id}
            entityType="post"
            onCommentAdded={handleCommentSubmit}
          />
          <h3 className="comments-title">
            Комментарии ({commentsCount})
          </h3>

          {loadingComments && comments.length === 0 ? (
            <div className="comments-loading">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="skeleton-comment"></div>
              ))}
            </div>
          ) : (
            <>
              {comments.length === 0 ? (
                <div className="no-comments">
                  <p>Пока нет комментариев</p>
                  <p className="no-comments-sub">Будьте первым, кто оставит комментарий!</p>
                </div>
              ) : (
                comments.map((comment) => (
                  <Comment key={comment.id} comment={comment} />
                ))
              )}

              {loadingComments && comments.length > 0 && (
                <div className="loading-more-comments">Загрузка комментариев...</div>
              )}

              {hasMoreComments && !loadingComments && (
                <button
                  className="load-more-comments"
                  onClick={loadMoreComments}
                >
                  Загрузить еще комментарии
                </button>
              )}
            </>
          )}
        </div>

        <RelatedSidebar id={id} />
      </div>
    </div>
  );
}

export default DiscussionThread;