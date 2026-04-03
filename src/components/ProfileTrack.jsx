function ProfileTrack() {
  return (
    <div className="profile-track">

      <div className="track-info">

        <h3>Neon Dreamscape Anthem</h3>
        <span>Zakhar</span>

        <div className="track-controls">

          <button>▶</button>
          <button>♡</button>
          <button>↗</button>

        </div>

        <div className="track-progress">
          <span>0:00</span>
          <div className="progress-bar"></div>
          <span>3:04</span>
        </div>

      </div>

      <img
        src="https://picsum.photos/200"
        className="track-cover"
      />

    </div>
  );
}

export default ProfileTrack;