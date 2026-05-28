import { Link } from "react-router-dom";
import "../styles/musicCard.css";

function MusicCard({ id, image, title, artist, type, year }) {
  return (
    <Link to={`/track/${id}`} className="music-card-link">
      <div className="music-card">
        <img src={image} alt={title} className="music-card__image" />

        <div className="music-card__info">
          <h3>{title}</h3>
          <p className="artist">{artist}</p>

          <div className="meta">
            <span className="badge">{type}</span>
            <span className="year">{year}</span>
          </div>
        </div>
      </div>
    </Link>
  );
}

export default MusicCard;