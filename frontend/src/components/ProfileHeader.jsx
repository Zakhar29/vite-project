import { useState } from "react";
import { Link } from "react-router-dom";
import Avatar from "./Avatar";
import UserListModal from "./UserListModal";

function ProfileHeader({
  user,
  isMyProfile,
  isFollowing,
  onFollow,
}) {
  const [isUserListModalOpen, setIsUserListModalOpen] = useState(false);
  const [userListModalType, setUserListModalType] = useState(null);

  const nickname = user?.nickname || "Пользователь";
  const username = user?.username || "";
  const bio = user?.bio || "Музыкант и продюсер";
  const followerQuantity = user?.follower_quantity || 0;
  const followingQuantity = user?.following_quantity || 0;

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
      <section className="profile-header">
        <div className="profile-header__main">
          <Avatar
            src={user?.avatar_url}
            className="profile-header__avatar"
            alt={nickname}
          />

          <div className="profile-header__info">
            <h1 className="profile-header__name">{nickname}</h1>
            {username && (
              <p className="profile-header__username">@{username}</p>
            )}
            <p className="profile-header__bio">{bio}</p>
          </div>
        </div>

        <div className="profile-header__aside">
          <div className="profile-header__stats">
            <button
              type="button"
              className="profile-header__stat"
              onClick={() => openModal("followers")}
            >
              <span className="profile-header__stat-value">{followerQuantity}</span>
              <span className="profile-header__stat-label">Подписчиков</span>
            </button>

            <button
              type="button"
              className="profile-header__stat"
              onClick={() => openModal("following")}
            >
              <span className="profile-header__stat-value">{followingQuantity}</span>
              <span className="profile-header__stat-label">Подписок</span>
            </button>
          </div>

          <div className="profile-header__actions">
            {isMyProfile ? (
              <>
                <Link to="/settings" className="profile-header__btn profile-header__btn--ghost">
                  Настройки
                </Link>
                <Link to="/profile/edit" className="profile-header__btn profile-header__btn--ghost">
                  Редактировать
                </Link>
                <Link to="/create-release" className="profile-header__btn profile-header__btn--primary">
                  Создать релиз
                </Link>
              </>
            ) : (
              <button
                type="button"
                className={`profile-header__btn profile-header__btn--primary ${isFollowing ? "is-following" : ""}`}
                onClick={onFollow}
              >
                {isFollowing ? "Отписаться" : "Подписаться"}
              </button>
            )}
          </div>
        </div>
      </section>

      <UserListModal
        isOpen={isUserListModalOpen}
        onClose={closeModal}
        userId={user?.id}
        type={userListModalType}
        title={
          userListModalType === "friends"
            ? "Друзья"
            : userListModalType === "followers"
              ? "Подписчики"
              : userListModalType === "following"
                ? "Подписки"
                : ""
        }
      />
    </>
  );
}

export default ProfileHeader;
