import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import DiscussionCardd from "../components/DiscussionCardd";
import GenreSidebar from "../components/GenreSidebar";
import CreatePost from "../components/CreatePost";
import "../styles/discussions.css";

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function Discussions() {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreatePost, setShowCreatePost] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [skip, setSkip] = useState(0);
  const [limit] = useState(20);
  const [isLoadingMore, setIsLoadingMore] = useState(false);

  // ========== Загрузка постов ==========

  const fetchPosts = async (skipValue = 0, append = false) => {
    try {
      const url = `${API_URL}/api/v1/feed/main?skip=${skipValue}&limit=${limit}`;
      const response = await fetch(url, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        credentials: 'include'
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Если не авторизован, все равно показываем популярные посты
          // Просто продолжаем
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Добавляем поле is_liked для каждого поста
      const postsWithState = (data.posts || []).map(post => ({
        ...post,
        is_liked: false // TODO: получать из API
      }));

      if (append) {
        setPosts(prev => [...prev, ...postsWithState]);
      } else {
        setPosts(postsWithState);
      }

      setHasMore(data.has_more);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch posts:', err);
      setError('Не удалось загрузить посты');
    } finally {
      setLoading(false);
      setIsLoadingMore(false);
    }
  };

  // Загрузка при монтировании
  useEffect(() => {
    fetchPosts(0, false);
  }, []);

  // Загрузка следующей страницы
  const loadMore = async () => {
    if (isLoadingMore || !hasMore) return;

    setIsLoadingMore(true);
    const newSkip = skip + limit;
    setSkip(newSkip);
    await fetchPosts(newSkip, true);
  };

  // ========== Создание поста ==========

  const handlePostCreated = (newPost) => {
    setPosts(prev => [{
      ...newPost,
      is_liked: false,
      likes_quantity: 0,
      comments_quantity: 0
    }, ...prev]);
    setShowCreatePost(false);
  };

  // ========== Лайки ==========

  const handleLike = async (postId) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/social/post/${postId}/like`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        credentials: 'include'
      });

      if (!response.ok) {
        if (response.status === 401) {
          navigate('/login');
          return;
        }
        throw new Error('Failed to like post');
      }

      setPosts(prev => prev.map(post =>
        post.id === postId
          ? { ...post, likes_quantity: (post.likes_quantity || 0) + 1, is_liked: true }
          : post
      ));
    } catch (err) {
      console.error('Failed to like post:', err);
    }
  };

  const handleUnlike = async (postId) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/social/post/${postId}/unlike`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        credentials: 'include'
      });

      if (!response.ok) {
        if (response.status === 401) {
          navigate('/login');
          return;
        }
        throw new Error('Failed to unlike post');
      }

      setPosts(prev => prev.map(post =>
        post.id === postId
          ? { ...post, likes_quantity: Math.max((post.likes_quantity || 0) - 1, 0), is_liked: false }
          : post
      ));
    } catch (err) {
      console.error('Failed to unlike post:', err);
    }
  };

  // ========== Удаление поста ==========

  const handleDeletePost = async (postId) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/post/${postId}`, {
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        credentials: 'include'
      });

      if (!response.ok) {
        if (response.status === 401) {
          navigate('/login');
          return;
        }
        throw new Error('Failed to delete post');
      }

      setPosts(prev => prev.filter(post => post.id !== postId));
    } catch (err) {
      console.error('Failed to delete post:', err);
    }
  };

  // ========== Бесконечная прокрутка ==========

  useEffect(() => {
    const handleScroll = () => {
      if (window.innerHeight + document.documentElement.scrollTop
          >= document.documentElement.offsetHeight - 200) {
        loadMore();
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [loading, hasMore, skip, isLoadingMore]);

  // ========== Отрисовка ==========

  if (loading && posts.length === 0) {
    return (
      <div className="discussions-page">
        <div className="discussion-hero">
          <div className="hero-text">
            <h1>Погружение в сердце звука</h1>
            <p>Загрузка дискуссий...</p>
          </div>
        </div>
        <div className="discussion-content">
          <GenreSidebar />
          <div className="discussion-list">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="post-skeleton">
                <div className="skeleton-avatar"></div>
                <div className="skeleton-content">
                  <div className="skeleton-line"></div>
                  <div className="skeleton-line"></div>
                  <div className="skeleton-line short"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error && posts.length === 0) {
    return (
      <div className="discussions-page">
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => fetchPosts(0, false)}>Попробовать снова</button>
        </div>
      </div>
    );
  }

  return (
    <div className="discussions-page">
      {/* HERO */}
      <div className="discussion-hero">
        <div className="hero-text">
          <h1>
            Погружение в сердце звука:
            дискуссия "Возрождение синтезаторных волн"
          </h1>
          <p>
            Познакомьтесь с возрождением электронной музыки 80-х.
            Поделитесь любимыми треками и обсудите методы продюсирования.
          </p>
          <button onClick={() => setShowCreatePost(true)}>
            Присоединиться к дискуссии
          </button>
        </div>
        <img
          src="https://picsum.photos/500/300"
          alt="sound wave"
        />
      </div>

      {/* MAIN CONTENT */}
      <div className="discussion-content">
        <GenreSidebar />

        <div className="discussion-list">
          <div className="discussion-list-header">
            <h2>Дискуссии</h2>
            <button
              className="add-post-btn"
              onClick={() => setShowCreatePost(true)}
            >
              + Добавить пост
            </button>
          </div>

          {posts.map((post) => (
            <DiscussionCardd
              key={post.id}
              post={post}
              onLike={handleLike}
              onUnlike={handleUnlike}
              onDelete={handleDeletePost}
            />
          ))}

          {isLoadingMore && (
            <div className="loading-more">Загрузка...</div>
          )}

          {!hasMore && posts.length > 0 && (
            <div className="no-more-posts">Больше постов нет</div>
          )}
        </div>
      </div>

      {/* Модальное окно создания поста */}
      <CreatePost
        isOpen={showCreatePost}
        onClose={() => setShowCreatePost(false)}
        onPostCreated={handlePostCreated}
      />
    </div>
  );
}

export default Discussions;