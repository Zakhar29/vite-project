import { useState, useEffect, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import ProfileHeader from "../components/ProfileHeader";
import ProfilePlaylistCard from "../components/ProfilePlaylistCard";
import ProfileAlbumCard from "../components/ProfileAlbumCard";
import ProfileTrack from "../components/ProfileTrack";
import DiscussionCard from "../components/DiscussionCard";
import CreatePostModal from "../components/CreatePostModal";
import "../styles/profile.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function Profile() {
  const { id } = useParams();
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const [tab, setTab] = useState("wall");
  const [posts, setPosts] = useState([]);
  const [albums, setAlbums] = useState([]);
  const [tracks, setTracks] = useState([]);
  const [userData, setUserData] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
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

  const isMyProfile = currentUser && (!id || id === "me" || id === currentUser.id);

  const resolveProfileUserId = () => {
    if (!id || id === "me") {
      return currentUser?.id || userData?.id || null;
    }
    return id;
  };

  const playlists = useMemo(() => {
    const nickname = userData?.nickname || "пользователя";
    const fallbackCover = tracks[0]?.cover_url || albums[0]?.cover_url || "/default-cover.jpg";

    return [
      {
        id: "user-tracks",
        title: `Треки ${nickname}`,
        trackCount: tracks.length,
        coverUrl: tracks[0]?.cover_url || fallbackCover,
      },
      {
        id: "liked",
        title: "Понравившееся",
        trackCount: tracks.filter((track) => track.is_liked).length,
        coverUrl: tracks.find((track) => track.is_liked)?.cover_url || albums[1]?.cover_url || fallbackCover,
      },
      {
        id: "recent",
        title: "Недавние",
        trackCount: Math.min(tracks.length, 10),
        coverUrl: tracks[1]?.cover_url || albums[0]?.cover_url || fallbackCover,
      },
    ];
  }, [userData, tracks, albums]);

  const fetchCurrentUser = async () => {
    if (!token) {
      setIsLoadingUser(false);
      return null;
    }

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentUser(data);
        return data;
      }

      localStorage.removeItem("access_token");
      setCurrentUser(null);
      return null;
    } catch (error) {
      console.error("Ошибка загрузки пользователя:", error);
      setCurrentUser(null);
      return null;
    } finally {
      setIsLoadingUser(false);
    }
  };

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }

    fetchCurrentUser().then(() => {
      loadProfileData();
    });
  }, [id, token]);

  const loadProfileData = async () => {
    setIsLoading(true);
    try {
      const profileUrl = (!id || id === "me")
        ? `${API_URL}/api/v1/user/me`
        : `${API_URL}/api/v1/user/${id}`;

      const response = await fetch(profileUrl, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        if (response.status === 404) {
          setUserData(null);
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

  const loadMorePosts = async () => {
    if (!hasMorePosts || isLoading) return;

    const userId = resolveProfileUserId();
    if (!userId) return;

    try {
      const response = await fetch(
        `${API_URL}/api/v1/user/${userId}/posts?skip=${postsSkip}&limit=${POSTS_LIMIT}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.ok) {
        const data = await response.json();
        setPosts((prev) => [...prev, ...data.items]);
        setPostsSkip(postsSkip + data.items.length);
        setHasMorePosts(data.has_more);
      }
    } catch (error) {
      console.error("Ошибка загрузки постов:", error);
    }
  };

  const loadMoreTracks = async () => {
    if (!hasMoreTracks || isLoading) return;

    const userId = resolveProfileUserId();
    if (!userId) return;

    try {
      const response = await fetch(
        `${API_URL}/api/v1/user/${userId}/tracks?skip=${tracksSkip}&limit=${TRACKS_LIMIT}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.ok) {
        const data = await response.json();
        setTracks((prev) => [...prev, ...data.items]);
        setTracksSkip(tracksSkip + data.items.length);
        setHasMoreTracks(data.has_more);
      }
    } catch (error) {
      console.error("Ошибка загрузки треков:", error);
    }
  };

  const loadMoreAlbums = async () => {
    if (!hasMoreAlbums || isLoading) return;

    const userId = resolveProfileUserId();
    if (!userId) return;

    try {
      const response = await fetch(
        `${API_URL}/api/v1/user/${userId}/albums?skip=${albumsSkip}&limit=${ALBUMS_LIMIT}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.ok) {
        const data = await response.json();
        setAlbums((prev) => [...prev, ...data.items]);
        setAlbumsSkip(albumsSkip + data.items.length);
        setHasMoreAlbums(data.has_more);
      }
    } catch (error) {
      console.error("Ошибка загрузки альбомов:", error);
    }
  };

  const handleFollow = async () => {
    if (!token || isMyProfile) return;

    const url = `${API_URL}/api/v1/user/${id}/${isFollowing ? "unfollow" : "follow"}`;
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        setIsFollowing(!isFollowing);
        setUserData((prev) => ({
          ...prev,
          follower_quantity: prev.follower_quantity + (isFollowing ? -1 : 1),
        }));
      }
    } catch (error) {
      console.error("Ошибка подписки:", error);
    }
  };

  const handlePostCreated = (newPost) => {
    setPosts((prev) => [newPost, ...prev]);
  };

  const handlePostClick = (postId) => {
    if (postId) {
      navigate(`/discussion/${postId}`);
    }
  };

  if (isLoadingUser || isLoading) {
    return (
      <div className="profile-page">
        <div className="profile-page__inner">
          <div className="loading-container">
            <div className="loading-spinner" />
            <p>Загрузка профиля...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!userData) {
    return (
      <div className="profile-page">
        <div className="profile-page__inner">
          <div className="error-container">
            <p>Пользователь не найден</p>
            <button type="button" onClick={() => navigate("/")}>На главную</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="profile-page__inner">
        <ProfileHeader
          user={userData}
          isMyProfile={isMyProfile}
          isFollowing={isFollowing}
          onFollow={handleFollow}
        />

        <div className="profile-tabs">
          <button
            type="button"
            className={`profile-tabs__tab ${tab === "wall" ? "is-active" : ""}`}
            onClick={() => setTab("wall")}
          >
            <span aria-hidden="true">☰</span>
            Стена пользователя
          </button>
          <button
            type="button"
            className={`profile-tabs__tab ${tab === "posts" ? "is-active" : ""}`}
            onClick={() => setTab("posts")}
          >
            <span aria-hidden="true">▦</span>
            Посты
          </button>
        </div>

        {tab === "wall" && (
          <>
            <section className="profile-section">
              <h2 className="profile-section__title">Плейлисты</h2>
              <div className="profile-section__row">
                {playlists.map((playlist) => (
                  <ProfilePlaylistCard
                    key={playlist.id}
                    title={playlist.title}
                    trackCount={playlist.trackCount}
                    coverUrl={playlist.coverUrl}
                    onClick={() => navigate(`/playlist/${playlist.id}`)}
                  />
                ))}
              </div>
            </section>

            <section className="profile-section">
              <h2 className="profile-section__title">Альбомы</h2>
              {albums.length > 0 ? (
                <div className="profile-section__grid">
                  {albums.map((album) => (
                    <ProfileAlbumCard
                      key={album.id}
                      album={album}
                      onClick={() => navigate(`/album/${album.id}`)}
                    />
                  ))}
                </div>
              ) : (
                <p className="empty-message">Нет альбомов</p>
              )}
              {hasMoreAlbums && (
                <button type="button" className="load-more-btn" onClick={loadMoreAlbums}>
                  Загрузить ещё альбомы
                </button>
              )}
            </section>

            <section className="profile-section">
              <h2 className="profile-section__title">Треки</h2>
              {tracks.length > 0 ? (
                <div className="profile-section__list">
                  {tracks.map((track) => (
                    <ProfileTrack
                      key={track.track_id}
                      track={track}
                      onClick={() => navigate(`/track/${track.track_id}`)}
                    />
                  ))}
                </div>
              ) : (
                <p className="empty-message">Нет треков</p>
              )}
              {hasMoreTracks && (
                <button type="button" className="load-more-btn" onClick={loadMoreTracks}>
                  Загрузить ещё треки
                </button>
              )}
            </section>
          </>
        )}

        {tab === "posts" && (
          <section className="profile-section posts-section">
            <div className="posts-section__header">
              <h2 className="profile-section__title">Посты</h2>
              {isMyProfile && (
                <button
                  type="button"
                  className="posts-section__add"
                  onClick={() => setIsModalOpen(true)}
                  aria-label="Создать пост"
                >
                  +
                </button>
              )}
            </div>

            {posts.length > 0 ? (
              posts.map((post) => {
                if (!post?.id) return null;
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
              <button type="button" className="load-more-btn" onClick={loadMorePosts}>
                Загрузить ещё посты
              </button>
            )}
          </section>
        )}

        <CreatePostModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onPostCreated={handlePostCreated}
        />
      </div>
    </div>
  );
}

export default Profile;
