import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import DiscussionCard from "./DiscussionCard";
import SectionTitle from "./SectionTitle";
import "../styles/hotDiscussions.css";

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function HotDiscussions() {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ========== Загрузка постов ==========

  useEffect(() => {
    fetchHotDiscussions();
  }, []);

  const fetchHotDiscussions = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/v1/feed/main?skip=0&limit=6`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('📦 Горячие обсуждения:', data);
      
      const postsData = data.posts || [];
      if (!Array.isArray(postsData)) {
        console.error('❌ posts не массив:', postsData);
        setPosts([]);
        return;
      }
      
      setPosts(postsData);
      setError(null);
    } catch (err) {
      console.error('❌ Ошибка загрузки горячих обсуждений:', err);
      setError('Не удалось загрузить обсуждения');
    } finally {
      setLoading(false);
    }
  };

  // ========== Обработчик клика по карточке ==========

  const handleCardClick = (postId) => {
    if (postId) {
      navigate(`/discussion/${postId}`);
    }
  };

  // ========== Состояние загрузки ==========

  if (loading) {
    return (
      <section className="hot-section">
        <div className="hot-section__header">
          <SectionTitle title="Горячие обсуждения" />
        </div>
        <div className="hot-grid">
          {[...Array(3)].map((_, index) => (
            <div key={index} className="discussion-card-skeleton">
              <div className="skeleton-title"></div>
              <div className="skeleton-text"></div>
              <div className="skeleton-meta"></div>
            </div>
          ))}
        </div>
      </section>
    );
  }

  // ========== Ошибка ==========

  if (error) {
    return (
      <section className="hot-section">
        <div className="hot-section__header">
          <SectionTitle title="Горячие обсуждения" />
        </div>
        <div className="hot-error">
          <p>{error}</p>
          <button onClick={fetchHotDiscussions}>Попробовать снова</button>
        </div>
      </section>
    );
  }

  // ========== Нет постов ==========

  if (posts.length === 0) {
    return (
      <section className="hot-section">
        <div className="hot-section__header">
          <SectionTitle title="Горячие обсуждения" />
        </div>
        <div className="hot-empty">
          <p>Пока нет обсуждений</p>
          <p className="hot-empty-sub">Будьте первым, кто начнет дискуссию!</p>
        </div>
      </section>
    );
  }

  // ========== Рендер ==========

  return (
    <section className="hot-section">
      <div className="hot-section__header">
        <SectionTitle title="Горячие обсуждения" />
      </div>

      <div className="hot-grid">
        {posts.slice(0, 3).map((post) => (
          <DiscussionCard
            key={post.id}
            post={post}
            variant="hot"
            onClick={() => handleCardClick(post.id)}
          />
        ))}
      </div>
    </section>
  );
}

export default HotDiscussions;