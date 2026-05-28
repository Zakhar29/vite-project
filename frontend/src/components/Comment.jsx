function Comment() {
  return (
    <div className="comment">

      <div className="comment-votes">
        ▲
        <span>45</span>
        ▼
      </div>

      <img
        src="https://i.pravatar.cc/35"
        className="avatar"
      />

      <div className="comment-body">

        <div className="comment-meta">
          <b>CodeWave_99</b>
          <span>2 часа назад</span>
        </div>

        <p>
          В этом ремиксе всё по-другому!
          Синтезатор просто безумный.
        </p>

        <div className="comment-actions">
          <span>Ответить</span>
           <span>12</span>
        </div>

      </div>

    </div>
  );
}

export default Comment;