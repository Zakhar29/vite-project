// components/UserCard.jsx
import { useNavigate } from 'react-router-dom';
import Avatar from "./Avatar";
import "../styles/userCard.css";

function UserCard({ 
  user, 
  type,           // 'friends' | 'followers' | 'following'
  onAction,       // колбэк для действия (подписка/отписка)
  showAction = true,
  onClick 
}) {
  const navigate = useNavigate();

  // Определяем ID в зависимости от типа
  const userId = user.follower_id || user.following_id || user.friend_id || user.id;
  const nickname = user.nickname || user.username || 'Пользователь';
  const bio = user.bio || '';
  const isFollowing = user.is_following || false;
  const isFriend = type === 'friends' || user.follow_status === 'friend';

  const handleClick = () => {
    if (onClick) {
      onClick(userId);
    } else {
      navigate(`/profile/${userId}`);
    }
  };

  const handleAction = (e) => {
    e.stopPropagation();
    if (onAction) {
      onAction(userId);
    }
  };

  // Определяем текст и класс для кнопки действия
  const getActionButton = () => {
    if (!showAction) return null;

    if (isFriend) {
      return (
        <button 
          className="user-card-action-btn friend"
          onClick={handleAction}
          title="Друг"
        >
          👥
        </button>
      );
    }

    if (type === 'followers') {
      return (
        <button 
          className="user-card-action-btn"
          onClick={handleAction}
          title="Перейти в профиль"
        >
          👤
        </button>
      );
    }

    if (type === 'following') {
      return (
        <button 
          className={`user-card-action-btn ${isFollowing ? 'following' : ''}`}
          onClick={handleAction}
          title={isFollowing ? 'Отписаться' : 'Подписаться'}
        >
          {isFollowing ? '✅' : '➕'}
        </button>
      );
    }

    return null;
  };

  return (
    <div className="user-card" onClick={handleClick}>
      <Avatar
        src={user.avatar_url}
        alt={nickname}
        className="user-card-avatar"
      />
      <div className="user-card-info">
        <div className="user-card-name">{nickname}</div>
        {bio && <div className="user-card-bio">{bio}</div>}
      </div>
      {getActionButton()}
    </div>
  );
}

export default UserCard;