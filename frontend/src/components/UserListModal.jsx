// components/UserListModal.jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import UserCard from './UserCard';
import "../styles/userListModal.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function UserListModal({ isOpen, onClose, userId, type, title }) {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hasMore, setHasMore] = useState(false);
  const [skip, setSkip] = useState(0);
  const [total, setTotal] = useState(0);
  const [limit] = useState(20);

  // Определяем эндпоинт в зависимости от типа
  const getEndpoint = () => {
    const endpoints = {
      friends: `/api/v1/user/${userId}/friends`,
      followers: `/api/v1/user/${userId}/followers`,
      following: `/api/v1/user/${userId}/following`
    };
    return endpoints[type] || endpoints.friends;
  };

  // Загрузка данных
  useEffect(() => {
    if (isOpen && userId) {
      loadUsers(0);
    }
  }, [isOpen, userId, type]);

  const loadUsers = async (skipValue = 0) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `${API_URL}${getEndpoint()}?skip=${skipValue}&limit=${limit}`,
        {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        }
      );

      if (!response.ok) {
        throw new Error('Ошибка загрузки данных');
      }

      const data = await response.json();
      
      if (skipValue === 0) {
        setUsers(data.items || []);
      } else {
        setUsers(prev => [...prev, ...(data.items || [])]);
      }

      setTotal(data.total || 0);
      setSkip(skipValue + limit);
      setHasMore(data.has_more || false);

    } catch (err) {
      console.error('Ошибка загрузки:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadMore = () => {
    if (!loading && hasMore) {
      loadUsers(skip);
    }
  };

  const handleUserClick = (userId) => {
    onClose();
    navigate(`/profile/${userId}`);
  };

  if (!isOpen) return null;

  return (
    <div className="user-list-modal-overlay" onClick={onClose}>
      <div className="user-list-modal" onClick={(e) => e.stopPropagation()}>
        <div className="user-list-modal-header">
          <h2>{title}</h2>
          <span className="user-list-count">{total}</span>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="user-list-modal-body">
          {loading && users.length === 0 ? (
            <div className="loading-users">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="user-card-skeleton">
                  <div className="skeleton-avatar"></div>
                  <div className="skeleton-info">
                    <div className="skeleton-line"></div>
                    <div className="skeleton-line short"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : error ? (
            <div className="error-message">
              <p>{error}</p>
              <button onClick={() => loadUsers(0)}>Попробовать снова</button>
            </div>
          ) : users.length === 0 ? (
            <div className="empty-message">
              <p>Нет пользователей</p>
            </div>
          ) : (
            <>
              <div className="users-list">
                {users.map((user) => (
                  <UserCard
                    key={user.follower_id || user.following_id || user.friend_id || user.id}
                    user={user}
                    type={type}
                    onAction={() => handleUserClick(user.follower_id || user.following_id || user.friend_id || user.id)}
                  />
                ))}
              </div>
              {hasMore && (
                <button 
                  className="load-more-btn"
                  onClick={loadMore}
                  disabled={loading}
                >
                  {loading ? 'Загрузка...' : 'Загрузить еще'}
                </button>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default UserListModal;