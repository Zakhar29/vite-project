function ProfileAlbumCard({ album, onClick }) {
  if (!album) return null;

  const title = album.title || "Без названия";
  const coverUrl = album.cover_url || album.cover || "/default-cover.jpg";
  const artistName = album.author?.nickname || "Неизвестный исполнитель";
  const albumType = album.subtype || album.type || "Альбом";
  const year = album.published_at_formatted || "2024";

  return (
    <div className="profile-album-card" onClick={onClick} role="button" tabIndex={0}>
      <div className="profile-album-card__cover">
        <img
          src={coverUrl}
          alt={title}
          loading="lazy"
          onError={(e) => {
            e.currentTarget.src = "/default-cover.jpg";
          }}
        />
      </div>
      <div className="profile-album-card__body">
        <h4 className="profile-album-card__title">{title}</h4>
        <p className="profile-album-card__artist">{artistName}</p>
        <div className="profile-album-card__footer">
          <span>{albumType}</span>
          <span>{year}</span>
        </div>
      </div>
    </div>
  );
}

export default ProfileAlbumCard;
