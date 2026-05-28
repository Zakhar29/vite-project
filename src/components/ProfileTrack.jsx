function ProfileTrack() {
  return (
    <div className="profile-track neon-track">

      {/* Левая часть: обложка + название */}
      <div className="track-left">
        <img
          src="https://picsum.photos/id/1015/300/300"
          alt="Neon Dreamscape Anthem"
          className="track-cover"
        />
        <div className="track-info">
          <h3 className="track-title">Neon Dreamscape Anthem</h3>
          <span className="track-artist">Zakhar</span>
        </div>
      </div>

      {/* Прогресс-бар — теперь всегда виден для каждого трека */}
      <div className="track-progress-container">
        <div className="track-progress">
          <span className="time">0:00</span>
          <div className="progress-bar">
            <div className="progress" style={{ width: "45%" }}></div>
          </div>
          <span className="time">3:04</span>
        </div>
      </div>

      {/* Правая часть: кнопки */}
      <div className="track-right">
        <div className="track-controls">
          <button className="control-btn play-btn">▶</button>
          <button className="control-btn">♡</button>
          <button className="control-btn">↗</button>
        </div>
      </div>

    </div>
  );
}

export default ProfileTrack;