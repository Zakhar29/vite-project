function DiscussionCardd() {
  return (
    <div className="discussion-card">

      <div className="discussion-votes">
        ▲
        <span>125</span>
        ▼
      </div>

      <div className="discussion-body">

        <div className="discussion-meta">
          <span className="tag">Electronic</span>
          <span>Опубликовано SynthMaster88 • 2 часа назад</span>
        </div>

        <h3>
          Будущее искусственного интеллекта
          в музыкальном производстве: друг или враг?
        </h3>

        <p>
          Lorem Ipsum — это текст-заполнитель,
          используемый для демонстрации дизайна.
        </p>

        <img
          src="https://picsum.photos/600/250"
          alt=""
        />

        <div className="discussion-actions">
          <span>💬 34 комментария</span>
          <span>🔗 Поделиться</span>
        </div>

      </div>

    </div>
  );
}

export default DiscussionCardd;