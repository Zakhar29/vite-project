function ProfilePlaylistCard({ title, trackCount, coverUrl, onClick }) {
  return (
    <button type="button" className="profile-playlist-card" onClick={onClick}>
      <div className="profile-playlist-card__cover">
        <img
          src={coverUrl || "/default-cover.jpg"}
          alt=""
          loading="lazy"
          onError={(e) => {
            e.currentTarget.src = "/default-cover.jpg";
          }}
        />
      </div>
      <div className="profile-playlist-card__info">
        <h4>{title}</h4>
        <p>{trackCount} треков</p>
      </div>
    </button>
  );
}

export default ProfilePlaylistCard;
