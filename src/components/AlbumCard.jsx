function AlbumCard() {
  return (
    <div className="album-card">

      <img src="https://picsum.photos/300/300" />

      <div className="album-info">
        <h4>Morning Coffee Jams</h4>
        <p>Various Artists</p>

        <div className="album-meta">
          <span>Альбом</span>
          <span>2023</span>
        </div>
      </div>

    </div>
  );
}

export default AlbumCard;