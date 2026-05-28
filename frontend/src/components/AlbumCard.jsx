// components/AlbumCard.jsx
import { useState } from 'react';

function AlbumCard({ album }) {
  const [expanded, setExpanded] = useState(false);
  if (!album || !album.cover) return null;

  // Показываем первые 3 трека, если не развёрнуто
  const visibleTracks = expanded ? album.tracks : album.tracks.slice(0, 3);

  return (
    <div className="album-card">
      <img src={album.cover} alt={album.title} />
      <div className="album-info">
        <h4>{album.title}</h4>
        <p>{album.artist}</p>
        <div className="album-meta">
          <span>Альбом</span>
          <span>{album.year}</span>
        </div>
        <button className="toggle-tracks" onClick={() => setExpanded(!expanded)}>
          {expanded ? 'Скрыть треки' : `Показать треки (${album.tracks.length})`}
        </button>
        {expanded && (
          <ul className="album-tracks-list">
            {visibleTracks.map((track, idx) => (
              <li key={track.id}>
                <span>{idx+1}. {track.title}</span>
                <span className="track-duration">{track.duration}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default AlbumCard;