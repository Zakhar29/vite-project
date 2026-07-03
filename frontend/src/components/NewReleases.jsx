import { useState, useEffect } from "react";
import MusicCard from "./MusicCard";
import SectionTitle from "./SectionTitle";
import "../styles/newReleases.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function NewReleases() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNewReleases = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/api/v1/music-feed/new-releases?limit=20`);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        setItems(data.items || []);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch new releases:', err);
        setError('Не удалось загрузить новинки');
      } finally {
        setLoading(false);
      }
    };

    fetchNewReleases();
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
      <section className="new-section">
        <div className="new-header">
          <SectionTitle title="Новинки" subtitle="Следите за последними треками" />
          <a href="/search" className="view-all">Посмотреть все →</a>
        </div>
        <div className="new-grid">
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
      <section className="new-section">
        <div className="new-header">
          <SectionTitle title="Новинки" subtitle="Следите за последними треками" />
          <a href="/search" className="view-all">Посмотреть все →</a>
        </div>
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Попробовать снова</button>
        </div>
      </section>
    );
  }

  return (
    <section className="new-section">
      <div className="new-header">
        <SectionTitle title="Новинки" subtitle="Следите за последними треками" />
        <a href="/search" className="view-all">Посмотреть все →</a>
      </div>

      <div className="new-grid">
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

export default NewReleases;