import { useState, useEffect } from "react";
import MusicCard from "./MusicCard";
import SectionTitle from "./SectionTitle";
import "../styles/forYou.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function ForYou() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchForYou = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/api/v1/music-feed/mixed?tracks_limit=10&albums_limit=10`);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        const allItems = [
          ...(data.tracks?.items || []).map(track => ({
            ...track,
            type: 'track',
            id: track.track_id
          })),
          ...(data.albums?.items || []).map(album => ({
            ...album,
            type: 'album',
            id: album.id
          }))
        ];

        const shuffled = allItems.sort(() => Math.random() - 0.5);
        setItems(shuffled.slice(0, 20));
        setError(null);
      } catch (err) {
        console.error('Failed to fetch recommendations:', err);
        setError('Не удалось загрузить рекомендации');
      } finally {
        setLoading(false);
      }
    };

    fetchForYou();
  }, []);

  // ========== ВОСПРОИЗВЕДЕНИЕ ==========
  const handlePlay = (tracks) => {
    if (!tracks || tracks.length === 0) {
      alert('Нет треков для воспроизведения');
      return;
    }

    console.log('🎵 Воспроизведение:', tracks);

    // Сохраняем в localStorage
    localStorage.setItem("playlist", JSON.stringify(tracks));
    localStorage.setItem("currentTrack", JSON.stringify(tracks[0]));
    localStorage.setItem("currentIndex", "0");

    // Диспатчим события
    window.dispatchEvent(new Event("trackChanged"));
    window.dispatchEvent(new Event("playlistChanged"));
  };

  const handleAuthorClick = (authorId) => {
    // Переход на страницу автора
    window.location.href = `/profile/${authorId}`;
  };

  if (loading) {
    return (
      <section className="foryou-section">
        <div className="foryou-header">
          <SectionTitle title="Для вас" subtitle="Подготовлено для вашего прослушивания" />
          <a href="/search" className="view-all">Посмотреть еще →</a>
        </div>
        <div className="foryou-grid">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="music-card-skeleton">
              <div className="skeleton-image"></div>
              <div className="skeleton-title"></div>
              <div className="skeleton-artist"></div>
            </div>
          ))}
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="foryou-section">
        <div className="foryou-header">
          <SectionTitle title="Для вас" subtitle="Подготовлено для вашего прослушивания" />
          <a href="/search" className="view-all">Посмотреть еще →</a>
        </div>
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Попробовать снова</button>
        </div>
      </section>
    );
  }

  return (
    <section className="foryou-section">
      <div className="foryou-header">
        <SectionTitle title="Для вас" subtitle="Подготовлено для вашего прослушивания" />
        <a href="/search" className="view-all">Посмотреть еще →</a>
      </div>

      <div className="foryou-grid">
        {items.slice(0, 8).map((item) => (
          <MusicCard
            key={item.id}
            item={item}
            onPlay={handlePlay}
            onAuthorClick={handleAuthorClick}
          />
        ))}
      </div>
    </section>
  );
}

export default ForYou;