// components/ProfileHeader.jsx
import { useState } from "react";
import UserListModal from "./UserListModal";

function ProfileHeader({ user, isMyProfile }) {
  const [isUserListModalOpen, setIsUserListModalOpen] = useState(false);
  const [userListModalType, setUserListModalType] = useState(null);

  // Если user передан — используем его, иначе заглушки
  const avatar = user?.avatar_url || "https://i.pravatar.cc/100";
  const nickname = user?.nickname || "Пользователь";
  const username = user?.username || "";
  const bio = user?.bio || "Музыкант и продюсер";
  const followerQuantity = user?.follower_quantity || 0;
  const followingQuantity = user?.following_quantity || 0;
  const friendsQuantity = user?.friends_quantity || 0;
  const listeningQuantity = user?.listening_quantity || 0;
  const monthListeningQuantity = user?.month_listening_quantity || 0;

  const openModal = (type) => {
    setUserListModalType(type);
    setIsUserListModalOpen(true);
  };

  const closeModal = () => {
    setIsUserListModalOpen(false);
    setUserListModalType(null);
  };

  return (
    <>
      <div className="profile-header">

        <div className="profile-left">

          <img
            src={avatar}
            className="profile-avatar"
            alt={nickname}
            onError={(e) => e.target.src = 'https://i.pravatar.cc/100'}
          />

          <div>
            <h1>{nickname}</h1>
            {username && <p className="profile-username">@{username}</p>}

            <div className="text_prof">
              <p>{bio}</p>
            </div>
          </div>

        </div>

        <div className="profile-right">

          <div className="profile-stats">
            <div 
              className="stat-item clickable"
              onClick={() => openModal('followers')}
            >
              <span className="count blue">{followerQuantity}</span>
              <p>Подписчиков</p>
            </div>

            <div 
              className="stat-item clickable"
              onClick={() => openModal('following')}
            >
              <span className="count purple">{followingQuantity}</span>
              <p>Подписок</p>
            </div>

            <div 
              className="stat-item clickable"
              onClick={() => openModal('friends')}
            >
              <span className="count green">{friendsQuantity}</span>
              <p>Друзей</p>
            </div>

            <div>
              <span className="count orange">{listeningQuantity}</span>
              <p>Количество прослушиваний</p>
            </div>

            <div>
              <span className="count pink">{monthListeningQuantity}</span>
              <p>Прослушивания за месяц</p>
            </div>
          </div>

        </div>

      </div>

      {/* ===== МОДАЛКА СПИСКА ПОЛЬЗОВАТЕЛЕЙ ===== */}
      <UserListModal
        isOpen={isUserListModalOpen}
        onClose={closeModal}
        userId={user?.id}
        type={userListModalType}
        title={
          userListModalType === 'friends' ? 'Друзья' :
          userListModalType === 'followers' ? 'Подписчики' :
          userListModalType === 'following' ? 'Подписки' : ''
        }
      />
    </>
  );
}

export default ProfileHeader;