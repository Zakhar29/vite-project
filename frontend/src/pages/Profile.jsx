import { useState, useEffect } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import ProfileHeader from "../components/ProfileHeader";
import PlaylistCard from "../components/PlaylistCard";
import AlbumCard from "../components/AlbumCard";
import ProfileTrack from "../components/ProfileTrack";
import DiscussionCard from "../components/DiscussionCard";
import CreatePostModal from "../components/CreatePostModal";
import "../styles/profile.css";

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function Profile() {
  const { id } = useParams();
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  // ========== Состояния ==========
  const [tab, setTab] = useState("wall");
  const [posts, setPosts] = useState([]);
  const [albums, setAlbums] = useState([]);
  const [tracks, setTracks] = useState([]);
  const [userData, setUserData] = useState(null);
  const [currentUser, setCurrentUser] = useState(null); // ← ТЕКУЩИЙ ПОЛЬЗОВАТЕЛЬ
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingUser, setIsLoadingUser] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [postsSkip, setPostsSkip] = useState(0);
  const [tracksSkip, setTracksSkip] = useState(0);
  const [albumsSkip, setAlbumsSkip] = useState(0);
  const [hasMorePosts, setHasMorePosts] = useState(true);
  const [hasMoreTracks, setHasMoreTracks] = useState(true);
  const [hasMoreAlbums, setHasMoreAlbums] = useState(true);
  const [isFollowing, setIsFollowing] = useState(false);

  const POSTS_LIMIT = 10;
  const TRACKS_LIMIT = 20;
  const ALBUMS_LIMIT = 20;

  // ========== Загрузка текущего пользователя ==========

  const fetchCurrentUser = async () => {
    if (!token) {
      setIsLoadingUser(false);
      return null;
    }

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentUser(data);
        return data;
      } else {
        localStorage.removeItem("access_token");
        setCurrentUser(null);
        return null;
      }
    } catch (error) {
      console.error("Ошибка загрузки пользователя:", error);
      setCurrentUser(null);
      return null;
    } finally {
      setIsLoadingUser(false);
    }
  };

  // ========== Определяем, свой это профиль ==========
  // isMyProfile = true если:
  // 1. Нет id в URL (страница /profile)
  // 2. id === "me"
  // 3. id совпадает с id текущего пользователя
  const isMyProfile = (currentUser && id === currentUser.id);

  // ========== Загрузка данных профиля ==========

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }
    
    // Сначала загружаем текущего пользователя
    fetchCurrentUser().then(() => {
      // После загрузки текущего пользователя загружаем профиль
      loadProfileData();
    });
  }, [id, token]);

  const loadProfileData = async () => {
    setIsLoading(true);
    try {
      // Определяем userId для запроса
      let userId;
      if (!id || id === "me") {
        // Если страница /profile или /profile/me - используем текущего пользователя
        if (currentUser) {
          userId = currentUser.id;
        } else {
          // Если currentUser еще не загружен, ждем
          return;
        }
      } else {
        userId = id;
      }

      const response = await fetch(`${API_URL}/api/v1/user/${userId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          navigate("/not-found");
          return;
        }
        throw new Error("Ошибка загрузки профиля");
      }

      const data = await response.json();

      setUserData(data.user);
      setTracks(data.top_tracks || []);
      setTracksSkip(data.top_tracks?.length || 0);
      setHasMoreTracks((data.top_tracks?.length || 0) >= 5);

      setAlbums(data.recent_albums || []);
      setAlbumsSkip(data.recent_albums?.length || 0);
      setHasMoreAlbums((data.recent_albums?.length || 0) >= 5);

      const postsItems = data.recent_posts?.items || [];
      setPosts(postsItems);
      setPostsSkip(postsItems.length);
      setHasMorePosts((data.recent_posts?.total || 0) > postsItems.length);

      setIsFollowing(data.user?.is_following || false);

    } catch (error) {
      console.error("Ошибка загрузки профиля:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // ========== Загрузка дополнительных постов ==========

  const loadMorePosts = async () => {
    if (!hasMorePosts || isLoading) return;

    const userId = isMyProfile ? (currentUser?.id || "me") : id;
    try {
      const response = await fetch(
        `${API_URL}/api/v1/user/${userId}/posts?skip=${postsSkip}&limit=${POSTS_LIMIT}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPosts(prev => [...prev, ...data.items]);
        setPostsSkip(postsSkip + data.items.length);
        setHasMorePosts(data.has_more);
      }
    } catch (error) {
      console.error("Ошибка загрузки постов:", error);
    }
  };

  // ========== Загрузка дополнительных треков ==========

  const loadMoreTracks = async () => {
    if (!hasMoreTracks || isLoading) return;

    const userId = isMyProfile ? (currentUser?.id || "me") : id;
    try {
      const response = await fetch(
        `${API_URL}/api/v1/user/${userId}/tracks?skip=${tracksSkip}&limit=${TRACKS_LIMIT}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setTracks(prev => [...prev, ...data.items]);
        setTracksSkip(tracksSkip + data.items.length);
        setHasMoreTracks(data.has_more);
      }
    } catch (error) {
      console.error("Ошибка загрузки треков:", error);
    }
  };

  // ========== Загрузка дополнительных альбомов ==========

  const loadMoreAlbums = async () => {
    if (!hasMoreAlbums || isLoading) return;

    const userId = isMyProfile ? (currentUser?.id || "me") : id;
    try {
      const response = await fetch(
        `${API_URL}/api/v1/user/${userId}/albums?skip=${albumsSkip}&limit=${ALBUMS_LIMIT}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAlbums(prev => [...prev, ...data.items]);
        setAlbumsSkip(albumsSkip + data.items.length);
        setHasMoreAlbums(data.has_more);
      }
    } catch (error) {
      console.error("Ошибка загрузки альбомов:", error);
    }
  };

  // ========== Обработчик подписки ==========

  const handleFollow = async () => {
    if (!token || isMyProfile) return;

    const url = `${API_URL}/api/v1/user/${id}/${isFollowing ? "unfollow" : "follow"}`;
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setIsFollowing(!isFollowing);
        setUserData(prev => ({
          ...prev,
          follower_quantity: prev.follower_quantity + (isFollowing ? -1 : 1),
        }));
      }
    } catch (error) {
      console.error("Ошибка подписки:", error);
    }
  };

  // ========== Обработчик создания поста ==========

  const handlePostCreated = (newPost) => {
    setPosts(prev => [newPost, ...prev]);
  };

  // ========== Обработчик клика по посту ==========

  const handlePostClick = (postId) => {
    if (postId) {
      navigate(`/discussion/${postId}`);
    }
  };

  // ========== Состояние загрузки ==========

  if (isLoadingUser || isLoading) {
    return (
      <div className="profile-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Загрузка профиля...</p>
        </div>
      </div>
    );
  }

  if (!userData) {
    return (
      <div className="profile-page">
        <div className="error-container">
          <p>Пользователь не найден</p>
          <button onClick={() => navigate("/")}>На главную</button>
        </div>
      </div>
    );
  }

  // ========== Рендер ==========

  return (
    <div className="profile-page">

      {/* ===== ШАПКА ПРОФИЛЯ ===== */}
      <ProfileHeader user={userData} isMyProfile={isMyProfile} />

      {/* ===== КНОПКИ ДЕЙСТВИЙ ===== */}
      {isMyProfile && (
        <div className="profile-edit-link">
          <Link to="/profile/edit" className="edit-profile-btn neon-btn-small">
            ✎ Редактировать профиль
          </Link>
          <Link to="/create-release" className="create-release-btn neon-btn-small">
            ➕ Создать релиз
          </Link>
        </div>
      )}

      {!isMyProfile && (
        <div className="profile-follow-section">
          <button
            className={`follow-btn ${isFollowing ? "following" : ""}`}
            onClick={handleFollow}
          >
            {isFollowing ? "✅ Отписаться" : "➕ Подписаться"}
          </button>
        </div>
      )}

      {/* ===== ВКЛАДКИ ===== */}
      <div className="profile-tabs">
        <span
          className={tab === "wall" ? "active" : ""}
          onClick={() => setTab("wall")}
        >
          Музыка
        </span>
        <span
          className={tab === "posts" ? "active" : ""}
          onClick={() => setTab("posts")}
        >
          Посты
        </span>
      </div>

      {/* ===== ВКЛАДКА "СТЕНА" ===== */}
      {tab === "wall" && (
        <>

          {/* Альбомы */}
          <h2>Альбомы</h2>
          <div className="album-row">
            {albums.length > 0 ? (
              albums.map(album => (
                <AlbumCard
                  key={album.id}
                  album={album}
                  onClick={() => navigate(`/album/${album.id}`)}
                />
              ))
            ) : (
              <p className="empty-message">Нет альбомов</p>
            )}
          </div>
          {hasMoreAlbums && (
            <button className="load-more-btn" onClick={loadMoreAlbums}>
              Загрузить ещё альбомы
            </button>
          )}

          {/* Треки */}
          <h2>Треки</h2>
          <div className="tracks-list">
            {tracks.length > 0 ? (
              tracks.map(track => (
                <ProfileTrack
                  key={track.track_id}
                  track={track}
                  onClick={() => navigate(`/track/${track.track_id}`)}
                />
              ))
            ) : (
              <p className="empty-message">Нет треков</p>
            )}
          </div>
          {hasMoreTracks && (
            <button className="load-more-btn" onClick={loadMoreTracks}>
              Загрузить ещё треки
            </button>
          )}
        </>
      )}

      {/* ===== ВКЛАДКА "ПОСТЫ" ===== */}
      {tab === "posts" && (
        <div className="posts-section">

          <div className="posts-header">
            <h2>Посты</h2>
            {isMyProfile && (
              <button
                className="add-post"
                onClick={() => setIsModalOpen(true)}
              >
                +
              </button>
            )}
          </div>

          {posts.length > 0 ? (
            posts.map((post) => {
              if (!post || !post.id) {
                console.warn('⚠️ Невалидный пост:', post);
                return null;
              }
              
              return (
                <DiscussionCard
                  key={post.id}
                  post={post}
                  onClick={() => handlePostClick(post.id)}
                />
              );
            })
          ) : (
            <p className="empty-message">Нет постов</p>
          )}

          {hasMorePosts && (
            <button className="load-more-btn" onClick={loadMorePosts}>
              Загрузить ещё посты
            </button>
          )}
        </div>
      )}

      {/* ===== МОДАЛКА СОЗДАНИЯ ПОСТА ===== */}
      <CreatePostModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onPostCreated={handlePostCreated}
      />

    </div>
  );
}

export default Profile;