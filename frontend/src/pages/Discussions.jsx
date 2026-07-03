import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import DiscussionFeedCard from "../components/DiscussionFeedCard";
import GenreSidebar from "../components/GenreSidebar";
import CreatePost from "../components/CreatePost";
import "../styles/discussions.css";

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
  const [activeGenre, setActiveGenre] = useState(null);
  const [activeFilter, setActiveFilter] = useState("trending");

  useEffect(() => {
    const openCreate = () => setShowCreatePost(true);
    window.addEventListener("openCreateDiscussion", openCreate);
    return () => window.removeEventListener("openCreateDiscussion", openCreate);
  }, []);

  const fetchPosts = async (skipValue = 0, append = false) => {
    try {
      const url = `${API_URL}/api/v1/feed/main?skip=${skipValue}&limit=${limit}`;
      const response = await fetch(url, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const postsWithState = (data.posts || []).map((post) => ({
        ...post,
        is_liked: false,
      }));

      if (append) {
        setPosts((prev) => [...prev, ...postsWithState]);
      } else {
        setPosts(postsWithState);
      }

      setHasMore(data.has_more);
      setError(null);
    } catch (err) {
      console.error("Failed to fetch posts:", err);
      setError("Не удалось загрузить посты");
    } finally {
      setLoading(false);
      setIsLoadingMore(false);
    }
  };

  useEffect(() => {
    fetchPosts(0, false);
  }, []);

  const loadMore = async () => {
    if (isLoadingMore || !hasMore) return;
    setIsLoadingMore(true);
    const newSkip = skip + limit;
    setSkip(newSkip);
    await fetchPosts(newSkip, true);
  };

  const handlePostCreated = (newPost) => {
    setPosts((prev) => [
      {
        ...newPost,
        is_liked: false,
        likes_quantity: 0,
        comments_quantity: 0,
      },
      ...prev,
    ]);
    setShowCreatePost(false);
  };

  const handleLike = async (postId) => {
    const response = await fetch(`${API_URL}/api/v1/social/post/${postId}/like`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      credentials: "include",
    });

    if (!response.ok) {
      if (response.status === 401) navigate("/login");
      throw new Error("Failed to like post");
    }

    setPosts((prev) =>
      prev.map((post) =>
        post.id === postId
          ? { ...post, likes_quantity: (post.likes_quantity || 0) + 1, is_liked: true }
          : post
      )
    );
  };

  const handleUnlike = async (postId) => {
    const response = await fetch(`${API_URL}/api/v1/social/post/${postId}/unlike`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      credentials: "include",
    });

    if (!response.ok) {
      if (response.status === 401) navigate("/login");
      throw new Error("Failed to unlike post");
    }

    setPosts((prev) =>
      prev.map((post) =>
        post.id === postId
          ? {
              ...post,
              likes_quantity: Math.max((post.likes_quantity || 0) - 1, 0),
              is_liked: false,
            }
          : post
      )
    );
  };

  const handleDeletePost = async (postId) => {
    const response = await fetch(`${API_URL}/api/v1/post/${postId}`, {
      method: "DELETE",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      credentials: "include",
    });

    if (!response.ok) {
      if (response.status === 401) navigate("/login");
      throw new Error("Failed to delete post");
    }

    setPosts((prev) => prev.filter((post) => post.id !== postId));
  };

  useEffect(() => {
    const handleScroll = () => {
      if (
        window.innerHeight + document.documentElement.scrollTop >=
        document.documentElement.offsetHeight - 200
      ) {
        loadMore();
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [loading, hasMore, skip, isLoadingMore]);

  const handleJoinFeatured = () => {
    if (posts.length > 0) {
      navigate(`/discussion/${posts[0].id}`);
      return;
    }
    setShowCreatePost(true);
  };

  const visiblePosts = posts.filter((post) => {
    if (activeFilter === "new") {
      return true;
    }
    if (activeFilter === "mine" && token) {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      return post.author?.id === user.id;
    }
    return true;
  });

  return (
    <div className="discussions-page">
      <div className="discussions-page__inner">
        <section className="discussion-hero">
          <div className="discussion-hero__text">
            <h1>
              Погружение в сердце звука: дискуссия «Возрождение синтезаторных волн»
            </h1>
            <p>
              Познакомьтесь с возрождением электронной музыки 80-х. Поделитесь
              любимыми треками, обсудите методы продюсирования и откройте для себя
              новых артистов вместе с сообществом Melo.
            </p>
            <button type="button" className="discussion-hero__cta" onClick={handleJoinFeatured}>
              Присоединиться к дискуссии
            </button>
          </div>
          <div className="discussion-hero__visual">
            <div className="discussion-hero__wave" aria-hidden="true" />
          </div>
        </section>

        <div className="discussion-content">
          <GenreSidebar
            activeGenre={activeGenre}
            activeFilter={activeFilter}
            onGenreChange={setActiveGenre}
            onFilterChange={setActiveFilter}
          />

          <div className="discussion-list">
            <h2 className="discussion-list__title">Дискуссии</h2>

            {loading && posts.length === 0 && (
              <>
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="post-skeleton" />
                ))}
              </>
            )}

            {error && posts.length === 0 && (
              <div className="discussion-list__error">
                <p>{error}</p>
                <button type="button" onClick={() => fetchPosts(0, false)}>
                  Попробовать снова
                </button>
              </div>
            )}

            {!loading && visiblePosts.length === 0 && !error && (
              <div className="discussion-list__empty">
                <p>Пока нет обсуждений в этой категории</p>
                <button type="button" onClick={() => setShowCreatePost(true)}>
                  Создать первое обсуждение
                </button>
              </div>
            )}

            {visiblePosts.map((post) => (
              <DiscussionFeedCard
                key={post.id}
                post={post}
                onLike={handleLike}
                onUnlike={handleUnlike}
                onDelete={handleDeletePost}
              />
            ))}

            {isLoadingMore && <div className="loading-more">Загрузка...</div>}
            {!hasMore && posts.length > 0 && (
              <div className="no-more-posts">Больше постов нет</div>
            )}
          </div>
        </div>
      </div>

      <CreatePost
        isOpen={showCreatePost}
        onClose={() => setShowCreatePost(false)}
        onPostCreated={handlePostCreated}
      />
    </div>
  );
}

export default Discussions;
